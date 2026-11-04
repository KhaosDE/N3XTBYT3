"""Hauptmenü (vier Systeme) und Szenarioliste eines Systems."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ..kern import auswahl
from ..kern import pfade
from ..kern.spielstand import Spielstand
from ..kern.systeme import REIHENFOLGE, SYSTEME
from ..kern.szenario import Ladeergebnis, SzenarioFehler, lade_allgemein, lade_system
from .basis import Ansicht, MatrixRegen
from .stil import FARBE, glow_text
from .text import umbrechen

if TYPE_CHECKING:
    from .app import App


def lade_alles(system_id: str) -> tuple[Ladeergebnis, object, Spielstand]:
    """Szenarien, allgemeine Befehle und Spielstand eines Systems."""
    try:
        allgemein = lade_allgemein(system_id)
    except SzenarioFehler as e:
        return Ladeergebnis([], [e]), None, Spielstand.lade(system_id)
    ergebnis = lade_system(system_id, allgemein=allgemein)
    return ergebnis, allgemein, Spielstand.lade(system_id)


def schwierigkeit_zeichnen(flaeche, x, y, stufe, groesse):
    for i in range(3):
        farbe = FARBE["gruen"] if i < stufe else FARBE["linie_dunkel"]
        pygame.draw.rect(flaeche, farbe, (x + i * (groesse + 3), y, groesse, groesse), border_radius=2)
    return 3 * (groesse + 3)


def etikett(flaeche, font, text, x, y, hinter, vorder):
    bild = font.render(f" {text} ", True, vorder)
    rect = pygame.Rect(x, y, bild.get_width() + 4, bild.get_height())
    pygame.draw.rect(flaeche, hinter, rect, border_radius=3)
    flaeche.blit(bild, (x + 2, y))
    return rect.width


class Hauptmenue(Ansicht):
    def __init__(self, app: "App"):
        super().__init__(app)
        self.auswahl = 0
        self.daten = {sid: lade_alles(sid) for sid in REIHENFOLGE}
        self.rects: list[pygame.Rect] = []
        self.regen: MatrixRegen | None = None

    def _spielbar(self, sid: str) -> bool:
        return bool(self.daten[sid][0].szenarien)

    def schrift_geaendert(self) -> None:
        self.regen = None

    def ereignis(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.auswahl = (self.auswahl - 1) % len(REIHENFOLGE)
            elif e.key in (pygame.K_DOWN, pygame.K_s, pygame.K_TAB):
                self.auswahl = (self.auswahl + 1) % len(REIHENFOLGE)
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._oeffnen(REIHENFOLGE[self.auswahl])
            elif e.key == pygame.K_ESCAPE:
                self.app.beenden()
            elif pygame.K_1 <= e.key <= pygame.K_4:
                self.auswahl = e.key - pygame.K_1
                self._oeffnen(REIHENFOLGE[self.auswahl])
        elif e.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.rects):
                if r.collidepoint(e.pos):
                    self.auswahl = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(e.pos):
                    self._oeffnen(REIHENFOLGE[i])

    def _oeffnen(self, sid: str) -> None:
        ergebnis, allgemein, stand = self.daten[sid]
        if not ergebnis.szenarien and not ergebnis.fehler:
            return  # kommt noch
        self.app.wechsle(Szenarioliste(self.app, sid, ergebnis, allgemein, stand))

    def update(self, dt):
        if self.regen:
            self.regen.update(dt)

    def zeichnen(self, f):
        s = self.app.schriften
        w, h = f.get_size()
        if self.regen is None or (self.regen.breite, self.regen.hoehe) != (w, h):
            self.regen = MatrixRegen(s.klein_mono, (w, h))
        f.fill(FARBE["hintergrund"])
        self.regen.zeichnen(f)
        schleier = pygame.Surface((w, h), pygame.SRCALPHA)
        schleier.fill((0, 0, 0, 150))
        f.blit(schleier, (0, 0))

        y = int(h * 0.08)
        glow_text(f, s.titel, "N3XTBYT3", FARBE["gruen"], (w // 2, y), staerke=3, mitte=True)
        y += s.titel.get_linesize()
        unter = s.text.render("Lern-Simulator für Systemwartung – reine Simulation, dein echtes System bleibt unberührt",
                              True, FARBE["text"])
        f.blit(unter, unter.get_rect(midtop=(w // 2, y)))
        y += unter.get_height() + s.zeilen_hoehe * 2

        kachel_b = min(int(w * 0.6), 60 * s.zeichen_breite)
        kachel_h = int(s.zeilen_hoehe * 3.2)
        x = (w - kachel_b) // 2
        self.rects = []
        for i, sid in enumerate(REIHENFOLGE):
            ergebnis, _allg, stand = self.daten[sid]
            rect = pygame.Rect(x, y, kachel_b, kachel_h)
            self.rects.append(rect)
            spielbar = self._spielbar(sid)
            gewaehlt = i == self.auswahl
            hinter = pygame.Surface(rect.size, pygame.SRCALPHA)
            hinter.fill((0, 60, 36, 230) if gewaehlt else (9, 17, 15, 230))
            f.blit(hinter, rect.topleft)
            rand = FARBE["linie"] if gewaehlt and spielbar else (FARBE["linie_dunkel"] if spielbar else FARBE["aus"])
            pygame.draw.rect(f, rand, rect, width=3 if gewaehlt else 2, border_radius=6)
            name = f"{i + 1}  {SYSTEME[sid].name}"
            farbe = FARBE["gruen_hell"] if spielbar else FARBE["aus"]
            if gewaehlt and spielbar:
                glow_text(f, s.zwischen, name, farbe, (rect.left + s.zeichen_breite * 2, rect.top + kachel_h // 6))
            else:
                f.blit(s.zwischen.render(name, True, farbe), (rect.left + s.zeichen_breite * 2, rect.top + kachel_h // 6))
            if spielbar:
                ids = [sz.id for sz in ergebnis.szenarien]
                info = f"{len(ids)} Szenarien · {stand.anzahl_geloest(ids)} gelöst"
                info_farbe = FARBE["text"]
            elif ergebnis.fehler:
                info = "Szenario-Dateien fehlerhaft – Enter für Details"
                info_farbe = FARBE["fehler"]
            else:
                info = "kommt noch"
                info_farbe = FARBE["aus"]
            bild = s.text.render(info, True, info_farbe)
            f.blit(bild, (rect.left + s.zeichen_breite * 2, rect.bottom - bild.get_height() - kachel_h // 6))
            if ergebnis.fehler and spielbar:
                warn = s.klein.render(f"{len(ergebnis.fehler)} Datei(en) fehlerhaft", True, FARBE["fehler"])
                f.blit(warn, (rect.right - warn.get_width() - s.zeichen_breite * 2, rect.bottom - warn.get_height() - kachel_h // 6))
            y += kachel_h + s.zeilen_hoehe // 2

        fuss = "Pfeiltasten oder 1–4 + Enter: System wählen  ·  Esc: Beenden  ·  Strg +/−: Schriftgröße  ·  F11: Vollbild"
        bild = s.klein.render(fuss, True, FARBE["text_schwach"])
        f.blit(bild, bild.get_rect(midbottom=(w // 2, h - s.zeilen_hoehe * 1.6)))
        ort = s.klein.render(f"Spielstand und eigene Szenarien: {pfade.datenordner()}", True, FARBE["text_schwach"])
        f.blit(ort, ort.get_rect(midbottom=(w // 2, h - s.zeilen_hoehe * 0.5)))


SONDER = (
    ("zufall", "»  Zufälliges Szenario (empfohlen: Fälliges und Schwaches zuerst)"),
    ("training", "»  Befehls-Training: Welcher Befehl …?"),
    ("auswertung", "»  Auswertung ansehen: Stärken, Schwächen, Empfehlung"),
)


class Szenarioliste(Ansicht):
    """Alle Szenarien eines Systems. Oben: Zufall, Befehls-Training, Auswertung."""

    def __init__(self, app: "App", system_id: str, ergebnis: Ladeergebnis, allgemein, stand: Spielstand):
        super().__init__(app)
        self.system_id = system_id
        self.ergebnis = ergebnis
        self.allgemein = allgemein
        self.stand = stand
        self.szenarien = sorted(ergebnis.szenarien, key=lambda s: (s.kategorie, s.schwierigkeit, s.titel))
        self.auswahl = 0
        self.oben = 0
        self.rects: list[tuple[pygame.Rect, int]] = []

    def _anzahl(self) -> int:
        return len(self.szenarien) + len(SONDER)

    def ereignis(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_UP:
                self.auswahl = (self.auswahl - 1) % self._anzahl()
            elif e.key == pygame.K_DOWN:
                self.auswahl = (self.auswahl + 1) % self._anzahl()
            elif e.key == pygame.K_PAGEUP:
                self.auswahl = max(0, self.auswahl - 8)
            elif e.key == pygame.K_PAGEDOWN:
                self.auswahl = min(self._anzahl() - 1, self.auswahl + 8)
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._starten(self.auswahl)
            elif e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.app.wechsle(Hauptmenue(self.app))
        elif e.type == pygame.MOUSEMOTION:
            for r, i in self.rects:
                if r.collidepoint(e.pos):
                    self.auswahl = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for r, i in self.rects:
                if r.collidepoint(e.pos):
                    self._starten(i)
        elif e.type == pygame.MOUSEWHEEL:
            self.auswahl = max(0, min(self._anzahl() - 1, self.auswahl - e.y))

    def _starten(self, index: int) -> None:
        if not self.szenarien or self.allgemein is None:
            return
        if index < len(SONDER):
            art = SONDER[index][0]
            if art == "training":
                from .training_ansicht import Trainingsansicht
                self.app.wechsle(Trainingsansicht(self.app, self.system_id, self.ergebnis,
                                                  self.allgemein, self.stand))
                return
            if art == "auswertung":
                from .auswertung_ansicht import Auswertungsansicht
                self.app.wechsle(Auswertungsansicht(self.app, self.system_id, self.ergebnis,
                                                    self.allgemein, self.stand))
                return
            szenario = auswahl.waehle(self.szenarien, self.stand)
        else:
            szenario = self.szenarien[index - len(SONDER)]
        from .spiel import Spielansicht
        self.app.wechsle(Spielansicht(self.app, self.system_id, szenario, self.szenarien,
                                      self.allgemein, self.stand))

    def zeichnen(self, f):
        s = self.app.schriften
        w, h = f.get_size()
        f.fill(FARBE["hintergrund"])
        rand = s.zeichen_breite * 3
        y = s.zeilen_hoehe
        ids = [sz.id for sz in self.szenarien]
        glow_text(f, s.zwischen, f"N3XTBYT3 // {SYSTEME[self.system_id].name}", FARBE["gruen"], (rand, y))
        info = s.text.render(f"{len(ids)} Szenarien · {self.stand.anzahl_geloest(ids)} gelöst", True, FARBE["text"])
        f.blit(info, (w - rand - info.get_width(), y + s.zeilen_hoehe // 4))
        y += s.zwischen.get_linesize() + s.zeilen_hoehe // 2
        pygame.draw.line(f, FARBE["linie"], (rand, y), (w - rand, y), 2)
        y += s.zeilen_hoehe // 2

        if self.stand.warnung:
            for zeile in umbrechen("Spielstand: " + self.stand.warnung, s.klein, w - 2 * rand):
                f.blit(s.klein.render(zeile, True, FARBE["warnung"]), (rand, y))
                y += s.klein.get_linesize()

        # Fehlerhafte Dateien unten anzeigen
        fehlerzeilen: list[str] = []
        for fehler in self.ergebnis.fehler:
            fehlerzeilen.append(f"Fehlerhafte Datei: {fehler.datei}")
            fehlerzeilen.extend(f"   – {m}" for m in fehler.meldungen[:6])
        fehler_hoehe = 0
        if fehlerzeilen:
            gebrochen = [z for zeile in fehlerzeilen for z in umbrechen(zeile, s.klein, w - 2 * rand)]
            gebrochen = gebrochen[:12]
            fehler_hoehe = (len(gebrochen) + 1) * s.klein.get_linesize()
            fy = h - fehler_hoehe - s.zeilen_hoehe * 2
            for zeile in gebrochen:
                f.blit(s.klein.render(zeile, True, FARBE["fehler"]), (rand, fy))
                fy += s.klein.get_linesize()

        zeile_h = int(s.zeilen_hoehe * 1.5)
        platz = h - y - fehler_hoehe - s.zeilen_hoehe * 3
        sichtbar = max(3, platz // zeile_h)
        if self.auswahl < self.oben:
            self.oben = self.auswahl
        elif self.auswahl >= self.oben + sichtbar:
            self.oben = self.auswahl - sichtbar + 1
        self.rects = []
        for i in range(self.oben, min(self._anzahl(), self.oben + sichtbar)):
            rect = pygame.Rect(rand, y, w - 2 * rand, zeile_h - 4)
            self.rects.append((rect, i))
            gewaehlt = i == self.auswahl
            if gewaehlt:
                pygame.draw.rect(f, FARBE["auswahl"], rect, border_radius=4)
                pygame.draw.rect(f, FARBE["linie"], rect, width=2, border_radius=4)
            ty = rect.top + (rect.height - s.text.get_linesize()) // 2
            x = rect.left + s.zeichen_breite
            if i < len(SONDER):
                f.blit(s.text_fett.render(SONDER[i][1], True, FARBE["gruen_hell"]), (x, ty))
            else:
                sz = self.szenarien[i - len(SONDER)]
                e = self.stand.eintrag(sz.id)
                if e["geloest"]:
                    punkt = FARBE["gruen"]
                elif e["versuche"]:
                    punkt = FARBE["warnung"]
                else:
                    punkt = FARBE["aus"]
                r = s.zeilen_hoehe // 4
                pygame.draw.circle(f, punkt, (x + r, rect.centery), r)
                x += 3 * r + s.zeichen_breite
                f.blit(s.text.render(sz.kategorie, True, FARBE["text_schwach"]), (x, ty))
                x += s.zeichen_breite * 12
                x += schwierigkeit_zeichnen(f, x, rect.centery - s.zeilen_hoehe // 4, sz.schwierigkeit,
                                            s.zeilen_hoehe // 2) + s.zeichen_breite
                f.blit(s.text.render(sz.titel, True, FARBE["gruen_hell"] if gewaehlt else FARBE["text"]), (x, ty))
                rx = rect.right - s.zeichen_breite
                if sz.bestaetigt:
                    tag = s.klein.render(" bestätigt ", True, FARBE["warnung_text"], FARBE["bestaetigt"])
                else:
                    tag = s.klein.render(" ungeprüft ", True, FARBE["warnung_text"], FARBE["warnung"])
                rx -= tag.get_width()
                f.blit(tag, (rx, rect.centery - tag.get_height() // 2))
                if sz.eigen:
                    eigen = s.klein.render(" eigen ", True, FARBE["warnung_text"], FARBE["sim"])
                    rx -= eigen.get_width() + s.zeichen_breite
                    f.blit(eigen, (rx, rect.centery - eigen.get_height() // 2))
                if e["versuche"]:
                    karte = self.stand.kartei.szenario(sz.id)
                    faellig = self.stand.kartei.ist_faellig(karte)
                    text = f"Fach {karte['fach']}" + (" · fällig" if faellig else "")
                    fach = s.klein.render(text, True, FARBE["sim"] if faellig else FARBE["text_schwach"])
                    rx -= fach.get_width() + s.zeichen_breite
                    f.blit(fach, (rx, rect.centery - fach.get_height() // 2))
                    v = s.klein.render(f"{e['versuche']} Versuch(e) ·", True, FARBE["text_schwach"])
                    rx -= v.get_width() + s.zeichen_breite // 2
                    f.blit(v, (rx, rect.centery - v.get_height() // 2))
            y += zeile_h

        fuss = "Pfeiltasten + Enter: starten  ·  Esc: zurück  ·  grün = gelöst, orange = versucht, grau = neu  ·  Fach 1–5 = Lernkartei"
        bild = s.klein.render(fuss, True, FARBE["text_schwach"])
        f.blit(bild, bild.get_rect(midbottom=(w // 2, h - s.zeilen_hoehe // 2)))
