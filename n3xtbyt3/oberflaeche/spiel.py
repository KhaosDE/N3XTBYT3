"""Spielansicht: links das Terminal, rechts Aufgabe, Hinweise, Begriffe, Erklärung."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ..kern import auswahl, auswertung
from ..kern.sitzung import Sitzung
from ..kern.systeme import SYSTEME
from .basis import Ansicht, Knopf, knopf_klick, zeichne_knopf
from .menue import Szenarioliste, etikett, lade_alles, schwierigkeit_zeichnen
from .stil import FARBE, glow_text
from .terminal import Terminal
from .text import umbrechen

if TYPE_CHECKING:
    from .app import App


class Spielansicht(Ansicht):
    def __init__(self, app: "App", system_id: str, szenario, szenarien, allgemein, stand):
        super().__init__(app)
        self.system_id = system_id
        self.szenario = szenario
        self.szenarien = szenarien
        self.allgemein = allgemein
        self.stand = stand
        self.sitzung = Sitzung(szenario, allgemein)
        self.terminal = Terminal()
        for z in self.sitzung.startzeilen():
            self.terminal.schreibe(z.text, z.art)
        self.terminal.schreibe("")
        self.warnungen: list[str] = []  # Erklärungen zu falschen Befehlen
        self.panel_scroll = 0
        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.terminal_rect = pygame.Rect(0, 0, 0, 0)
        self.knoepfe: list[Knopf] = []
        self.blink = 0.0
        self._gespeichert = False

    # ------------------------------------------------------------------ Aktionen

    def hinweis(self) -> None:
        text = self.sitzung.naechster_hinweis()
        if text is None:
            self.terminal.schreibe("[N3XTBYT3] Alle drei Hinweise sind schon offen (rechts).", "sim")
        else:
            self.terminal.schreibe(f"[N3XTBYT3] Hinweis {self.sitzung.hinweis_stufe} steht rechts.", "sim")
            self.panel_scroll = 0

    def _speichern(self) -> None:
        if self._gespeichert:
            return
        self._gespeichert = True
        if self.stand.versuch_eintragen(self.szenario.id, self.sitzung.ergebnis()):
            try:
                self.stand.speichere()
                auswertung.schreibe(self.system_id, self.szenarien, self.stand)
            except OSError as e:
                print(f"Spielstand konnte nicht gespeichert werden: {e}")

    def naechstes(self) -> None:
        self._speichern()
        neu = auswahl.waehle(self.szenarien, self.stand, zuletzt=self.szenario.id)
        if neu is not None:
            self.app.wechsle(Spielansicht(self.app, self.system_id, neu, self.szenarien,
                                          self.allgemein, self.stand))

    def zur_liste(self) -> None:
        self._speichern()
        ergebnis, allgemein, stand = lade_alles(self.system_id)
        self.app.wechsle(Szenarioliste(self.app, self.system_id, ergebnis, allgemein, stand))

    def verlassen(self) -> None:
        self._speichern()

    def ausfuehren(self, befehl: str) -> None:
        antwort = self.sitzung.eingabe(befehl)
        if antwort.aktion == "leeren":
            self.terminal.leeren()
        for z in antwort.zeilen:
            self.terminal.schreibe(z.text, z.art)
        if antwort.warum and antwort.warum not in self.warnungen:
            self.warnungen.append(antwort.warum)
        if antwort.geloest_jetzt:
            self.panel_scroll = 0
            self._speichern_geloest()

    def _speichern_geloest(self) -> None:
        # Gelöst: sofort speichern, damit nichts verloren geht. Weitere Eingaben zählen nicht mehr.
        self._speichern()

    # ------------------------------------------------------------------ Ereignisse

    def ereignis(self, e):
        if knopf_klick(self.knoepfe, e):
            return
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_F1:
                self.hinweis()
                return
            if e.key == pygame.K_F2:
                self.naechstes()
                return
            if e.key == pygame.K_ESCAPE:
                self.zur_liste()
                return
            befehl = self.terminal.taste(e, self.sitzung.prompt())
            if befehl is not None:
                self.ausfuehren(befehl)
            self.blink = 0.0
        elif e.type == pygame.TEXTINPUT:
            self.terminal.text_eingabe(e.text)
            self.blink = 0.0
        elif e.type == pygame.MOUSEWHEEL:
            maus = pygame.mouse.get_pos()
            if self.panel_rect.collidepoint(maus):
                self.panel_scroll = max(0, self.panel_scroll - e.y * self.app.schriften.zeilen_hoehe * 2)
            else:
                self.terminal.blaettern(e.y * 3)

    def update(self, dt):
        self.blink += dt

    # ------------------------------------------------------------------ Zeichnen

    def zeichnen(self, f):
        s = self.app.schriften
        w, h = f.get_size()
        f.fill(FARBE["hintergrund"])
        kopf_h = int(s.zeilen_hoehe * 2)
        fuss_h = int(s.zeilen_hoehe * 1.4)
        panel_b = max(int(w * 0.36), 30 * s.zeichen_breite)
        panel_b = min(panel_b, w - 40 * s.zeichen_breite) if w > 70 * s.zeichen_breite else int(w * 0.4)

        self._kopf(f, pygame.Rect(0, 0, w, kopf_h))
        self.terminal_rect = pygame.Rect(0, kopf_h, w - panel_b, h - kopf_h - fuss_h)
        self.panel_rect = pygame.Rect(w - panel_b, kopf_h, panel_b, h - kopf_h - fuss_h)
        cursor_an = (self.blink % 1.0) < 0.6
        self.terminal.zeichnen(f, self.terminal_rect, s, self.sitzung.prompt(), cursor_an)
        pygame.draw.line(f, FARBE["linie"], self.panel_rect.topleft, self.panel_rect.bottomleft, 2)
        self._panel(f, self.panel_rect)
        self._fuss(f, pygame.Rect(0, h - fuss_h, w, fuss_h))

    def _kopf(self, f, rect):
        s = self.app.schriften
        pygame.draw.rect(f, FARBE["kopf"], rect)
        pygame.draw.line(f, FARBE["linie"], rect.bottomleft, rect.bottomright, 2)
        x = s.zeichen_breite
        y = rect.centery - s.mono_fett.get_linesize() // 2
        r = glow_text(f, s.mono_fett, "N3XTBYT3", FARBE["gruen"], (x, y), staerke=1)
        x = r.right + s.zeichen_breite
        rest = f" // {SYSTEME[self.system_id].name} // {self.sitzung.fenstertitel()}"
        f.blit(s.mono.render(rest, True, FARBE["gruen_hell"]), (x, y))
        sek = self.sitzung.sekunden()
        uhr = s.mono.render(f"{sek // 60:02d}:{sek % 60:02d}", True, FARBE["text_schwach"])
        rx = rect.right - s.zeichen_breite - uhr.get_width()
        f.blit(uhr, (rx, y))
        if not self.szenario.bestaetigt:
            tag = s.text_fett.render("  UNGEPRÜFT  ", True, FARBE["warnung_text"], FARBE["warnung"])
            rx -= tag.get_width() + s.zeichen_breite * 2
            f.blit(tag, (rx, rect.centery - tag.get_height() // 2))
        if self.sitzung.geloest:
            tag = s.text_fett.render("  GELÖST  ", True, FARBE["warnung_text"], FARBE["erfolg"])
            rx -= tag.get_width() + s.zeichen_breite
            f.blit(tag, (rx, rect.centery - tag.get_height() // 2))

    def _fuss(self, f, rect):
        s = self.app.schriften
        pygame.draw.rect(f, FARBE["kopf"], rect)
        pygame.draw.line(f, FARBE["linie_dunkel"], rect.topleft, rect.topright, 1)
        text = ("F1 Hinweis  ·  F2 Nächstes Szenario  ·  Esc Szenarioliste  ·  ↑↓ Befehlsverlauf  ·  "
                "Bild ↑↓ blättern  ·  Strg +/− Schrift  ·  F11 Vollbild")
        bild = s.klein.render(text, True, FARBE["text_schwach"])
        f.blit(bild, (s.zeichen_breite, rect.centery - bild.get_height() // 2))

    def _panel_bloecke(self, breite: int) -> list[tuple]:
        """Inhalt des Seitenbereichs als Liste von (Art, Daten)."""
        s = self.app.schriften
        sz = self.szenario
        bloecke: list[tuple] = []

        def absatz(text, font=None, farbe=None, einzug=0):
            font = font or s.text
            for zeile in umbrechen(text, font, breite - einzug):
                bloecke.append(("zeile", zeile, font, farbe or FARBE["text"], einzug))

        def ueberschrift(text, farbe=None):
            bloecke.append(("abstand", s.zeilen_hoehe // 2))
            bloecke.append(("ueberschrift", text, farbe or FARBE["magenta"]))

        absatz(sz.titel, s.zwischen, FARBE["gruen_hell"])
        bloecke.append(("info", sz))
        if not sz.bestaetigt:
            bloecke.append(("abstand", s.zeilen_hoehe // 3))
            absatz("Ungeprüft: Von Claude geschrieben, von dir noch nicht bestätigt. "
                   "Ausgaben können vom echten System abweichen – im Zweifel die Quelle lesen.",
                   s.klein, FARBE["warnung"])

        if self.sitzung.geloest:
            ueberschrift("GELÖST – ERKLÄRUNG", FARBE["erfolg"])
            absatz(sz.erklaerung)
            bloecke.append(("abstand", s.zeilen_hoehe // 3))
            absatz("Weiter mit F2 (nächstes Szenario) oder Esc (Liste).", s.klein, FARBE["erfolg"])

        ueberschrift("AUSGANGSLAGE")
        absatz(sz.ausgangslage)

        ueberschrift(f"HINWEISE ({self.sitzung.hinweis_stufe}/3)")
        if not self.sitzung.gezeigte_hinweise:
            absatz("Noch keiner geöffnet. Taste F1 oder Knopf unten – Stufe für Stufe.", s.klein,
                   FARBE["text_schwach"])
        stufen = ("Richtung", "Werkzeug", "Fast die Lösung")
        for i, hinweis in enumerate(self.sitzung.gezeigte_hinweise):
            absatz(f"{i + 1}. {stufen[i]}", s.text_fett, FARBE["sim"])
            absatz(hinweis, einzug=s.zeichen_breite)

        if self.warnungen:
            ueberschrift("ACHTUNG", FARBE["warnung"])
            for warnung in self.warnungen[-3:]:
                absatz(warnung, s.text, FARBE["warnung"])
                bloecke.append(("abstand", s.zeilen_hoehe // 4))

        ueberschrift("BEGRIFFE")
        for begriff, erklaerung in sz.begriffe.items():
            absatz(begriff, s.text_fett, FARBE["gruen"])
            absatz(erklaerung, einzug=s.zeichen_breite)

        ueberschrift("QUELLE")
        for q in sz.quelle:
            absatz(q, s.klein, FARBE["text_schwach"])
        if sz.eigen and sz.datei:
            absatz(f"Eigenes Szenario: {sz.datei}", s.klein, FARBE["text_schwach"])
        return bloecke

    def _panel(self, f, rect):
        s = self.app.schriften
        pygame.draw.rect(f, FARBE["panel"], rect.inflate(-2, 0).move(1, 0))
        rand = s.zeichen_breite * 2
        knopf_h = int(s.zeilen_hoehe * 1.7)
        knopf_bereich = knopf_h * 2 + rand * 2
        inhalt = pygame.Rect(rect.left + rand, rect.top + rand // 2, rect.width - 2 * rand,
                             rect.height - knopf_bereich - rand // 2)

        bloecke = self._panel_bloecke(inhalt.width)
        hoehen = []
        for b in bloecke:
            if b[0] == "zeile":
                hoehen.append(b[2].get_linesize())
            elif b[0] == "abstand":
                hoehen.append(b[1])
            elif b[0] == "ueberschrift":
                hoehen.append(s.mono_fett.get_linesize() + 6)
            elif b[0] == "info":
                hoehen.append(int(s.text.get_linesize() * 1.4))
        gesamt = sum(hoehen)
        self.panel_scroll = max(0, min(self.panel_scroll, max(0, gesamt - inhalt.height)))

        alt_clip = f.get_clip()
        f.set_clip(inhalt)
        y = inhalt.top - self.panel_scroll
        for b, hoehe in zip(bloecke, hoehen):
            if y + hoehe >= inhalt.top and y <= inhalt.bottom:
                if b[0] == "zeile":
                    _, text, font, farbe, einzug = b
                    if text:
                        f.blit(font.render(text, True, farbe), (inhalt.left + einzug, y))
                elif b[0] == "ueberschrift":
                    _, text, farbe = b
                    f.blit(s.mono_fett.render(text, True, farbe), (inhalt.left, y))
                    ly = y + s.mono_fett.get_linesize() + 1
                    pygame.draw.line(f, FARBE["linie_dunkel"], (inhalt.left, ly), (inhalt.right, ly), 1)
                elif b[0] == "info":
                    sz = b[1]
                    x = inhalt.left
                    iy = y + 4
                    x += etikett(f, s.klein, sz.kategorie, x, iy, FARBE["linie_dunkel"], FARBE["gruen_hell"]) + 8
                    x += schwierigkeit_zeichnen(f, x, iy + 3, sz.schwierigkeit, s.klein.get_linesize() - 6) + 8
                    if sz.bestaetigt:
                        etikett(f, s.klein, "bestätigt", x, iy, FARBE["bestaetigt"], FARBE["warnung_text"])
                    else:
                        etikett(f, s.klein, "UNGEPRÜFT", x, iy, FARBE["warnung"], FARBE["warnung_text"])
            y += hoehe
        f.set_clip(alt_clip)
        if gesamt > inhalt.height:
            anteil = inhalt.height / gesamt
            balken_h = max(20, int(inhalt.height * anteil))
            balken_y = inhalt.top + int((inhalt.height - balken_h) * (self.panel_scroll / max(1, gesamt - inhalt.height)))
            pygame.draw.rect(f, FARBE["linie_dunkel"], (rect.right - 6, balken_y, 4, balken_h), border_radius=2)

        # Knöpfe
        kb = (inhalt.width - rand) // 2
        ky = rect.bottom - knopf_bereich + rand // 2
        noch_hinweise = self.sitzung.hinweis_stufe < 3
        self.knoepfe = [
            Knopf(pygame.Rect(inhalt.left, ky, kb, knopf_h), "Hinweis (F1)", self.hinweis, noch_hinweise),
            Knopf(pygame.Rect(inhalt.left + kb + rand, ky, kb, knopf_h), "Nächstes (F2)", self.naechstes),
            Knopf(pygame.Rect(inhalt.left, ky + knopf_h + rand // 2, inhalt.width, knopf_h),
                  "Zur Szenarioliste (Esc)", self.zur_liste),
        ]
        maus = pygame.mouse.get_pos()
        for k in self.knoepfe:
            zeichne_knopf(f, k, s.text_fett, maus)
