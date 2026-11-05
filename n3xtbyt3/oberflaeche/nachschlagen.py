"""Befehlsbuch (F4) und Lexikon (F5): Einblendungen zum Nachschlagen, von überall erreichbar."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ..kern import befehlsbuch as bb
from ..kern import grundkurs as gk
from ..kern.spielstand import Spielstand
from ..kern.systeme import SYSTEME
from ..kern.szenario import lade_system
from .basis import Ansicht
from .panel import Bloecke
from .stil import FARBE, glow_text

if TYPE_CHECKING:
    from .app import App


def _kuerzen(text: str, font: pygame.font.Font, breite: int) -> str:
    if font.size(text)[0] <= breite:
        return text
    while text and font.size(text + "…")[0] > breite:
        text = text[:-1]
    return text + "…"


class Nachschlagen(Ansicht):
    """Grundgerüst: Suchzeile, Liste links, Einzelheiten rechts, optional Reiter (Tab)."""

    art = ""
    titel = ""
    reiter: tuple[str, ...] = ()

    def __init__(self, app: "App", system_id: str):
        super().__init__(app)
        self.system_id = system_id
        self.suche = ""
        self.reiter_nr = 0
        self.auswahl = 0
        self.oben = 0
        self.detail_scroll = 0
        self.detail_rect = pygame.Rect(0, 0, 0, 0)
        self.rects: list[tuple[pygame.Rect, int]] = []

    # Unterklassen
    def eintraege(self) -> list:
        return []

    def zeilentext(self, eintrag) -> tuple[str, tuple | None]:
        return str(eintrag), None

    def detail(self, b: Bloecke, eintrag) -> None:
        pass

    def leer_text(self) -> str:
        return "Nichts gefunden."

    # ------------------------------------------------------------------ Ereignisse

    def schliessen(self) -> None:
        self.app.overlay = None

    def ereignis(self, e):
        anzahl = len(self.eintraege())
        if e.type == pygame.TEXTINPUT:
            self.suche += e.text
            self.auswahl = self.oben = self.detail_scroll = 0
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                if self.suche:
                    self.suche = ""
                    self.auswahl = self.oben = 0
                else:
                    self.schliessen()
            elif e.key == pygame.K_BACKSPACE:
                self.suche = self.suche[:-1]
                self.auswahl = self.oben = self.detail_scroll = 0
            elif e.key == pygame.K_TAB and self.reiter:
                self.reiter_nr = (self.reiter_nr + 1) % len(self.reiter)
                self.auswahl = self.oben = self.detail_scroll = 0
            elif e.key == pygame.K_UP and anzahl:
                self.auswahl = (self.auswahl - 1) % anzahl
                self.detail_scroll = 0
            elif e.key == pygame.K_DOWN and anzahl:
                self.auswahl = (self.auswahl + 1) % anzahl
                self.detail_scroll = 0
            elif e.key == pygame.K_PAGEDOWN:
                self.detail_scroll += self.app.schriften.zeilen_hoehe * 8
            elif e.key == pygame.K_PAGEUP:
                self.detail_scroll = max(0, self.detail_scroll - self.app.schriften.zeilen_hoehe * 8)
        elif e.type == pygame.MOUSEWHEEL:
            if self.detail_rect.collidepoint(pygame.mouse.get_pos()):
                self.detail_scroll = max(0, self.detail_scroll - e.y * self.app.schriften.zeilen_hoehe * 2)
            elif anzahl:
                self.auswahl = max(0, min(anzahl - 1, self.auswahl - e.y))
                self.detail_scroll = 0
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for r, i in self.rects:
                if r.collidepoint(e.pos):
                    self.auswahl = i
                    self.detail_scroll = 0

    # ------------------------------------------------------------------ Zeichnen

    def zeichnen(self, f):
        s = self.app.schriften
        w, h = f.get_size()
        schleier = pygame.Surface((w, h), pygame.SRCALPHA)
        schleier.fill((0, 0, 0, 200))
        f.blit(schleier, (0, 0))
        rand = max(s.zeichen_breite * 2, int(min(w, h) * 0.03))
        rahmen = pygame.Rect(rand, rand, w - 2 * rand, h - 2 * rand)
        pygame.draw.rect(f, FARBE["panel"], rahmen, border_radius=8)
        pygame.draw.rect(f, FARBE["linie"], rahmen, width=2, border_radius=8)
        innen = rahmen.inflate(-s.zeichen_breite * 4, -s.zeilen_hoehe)
        y = innen.top
        glow_text(f, s.zwischen, f"{self.titel} // {SYSTEME[self.system_id].name}", FARBE["gruen"], (innen.left, y))
        hinweis = s.klein.render(f"Esc schließt  ·  {self.art_taste} auch", True, FARBE["text_schwach"])
        f.blit(hinweis, (innen.right - hinweis.get_width(), y + s.zeilen_hoehe // 3))
        y += s.zwischen.get_linesize() + s.zeilen_hoehe // 3

        if self.reiter:
            x = innen.left
            for i, name in enumerate(self.reiter):
                aktiv = i == self.reiter_nr
                bild = s.text_fett.render(f"  {name}  ", True, FARBE["warnung_text"] if aktiv else FARBE["text"],
                                          FARBE["gruen"] if aktiv else FARBE["auswahl"])
                f.blit(bild, (x, y))
                x += bild.get_width() + s.zeichen_breite
            tab = s.klein.render("Tab: wechseln", True, FARBE["text_schwach"])
            f.blit(tab, (x + s.zeichen_breite, y + (bild.get_height() - tab.get_height()) // 2))
            y += bild.get_height() + s.zeilen_hoehe // 3

        such = pygame.Rect(innen.left, y, innen.width, int(s.zeilen_hoehe * 1.5))
        pygame.draw.rect(f, FARBE["terminal"], such, border_radius=4)
        pygame.draw.rect(f, FARBE["linie_dunkel"], such, width=1, border_radius=4)
        text = s.mono.render("Suche: " + self.suche, True, FARBE["eingabe"])
        f.blit(text, (such.left + s.zeichen_breite, such.centery - text.get_height() // 2))
        cx = such.left + s.zeichen_breite + text.get_width()
        pygame.draw.rect(f, FARBE["gruen"], (cx, such.top + 5, s.zeichen_breite, such.height - 10))
        if not self.suche:
            tipp = s.klein.render("einfach lostippen – Backspace löscht, Esc leert", True, FARBE["text_schwach"])
            f.blit(tipp, (cx + s.zeichen_breite * 2, such.centery - tipp.get_height() // 2))
        y = such.bottom + s.zeilen_hoehe // 2

        eintraege = self.eintraege()
        self.auswahl = min(self.auswahl, max(0, len(eintraege) - 1))
        listen_b = int(innen.width * 0.36)
        liste = pygame.Rect(innen.left, y, listen_b, innen.bottom - y)
        self.detail_rect = pygame.Rect(liste.right + s.zeichen_breite * 3, y,
                                       innen.right - liste.right - s.zeichen_breite * 3 - 10, innen.bottom - y)
        pygame.draw.line(f, FARBE["linie_dunkel"], (liste.right + s.zeichen_breite, y),
                         (liste.right + s.zeichen_breite, innen.bottom), 1)

        zeile_h = int(s.text.get_linesize() * 1.35)
        sichtbar = max(1, liste.height // zeile_h)
        if self.auswahl < self.oben:
            self.oben = self.auswahl
        elif self.auswahl >= self.oben + sichtbar:
            self.oben = self.auswahl - sichtbar + 1
        self.rects = []
        if not eintraege:
            f.blit(s.text.render(self.leer_text(), True, FARBE["aus"]), (liste.left, liste.top))
        for i in range(self.oben, min(len(eintraege), self.oben + sichtbar)):
            r = pygame.Rect(liste.left, liste.top + (i - self.oben) * zeile_h, liste.width, zeile_h - 2)
            self.rects.append((r, i))
            gewaehlt = i == self.auswahl
            if gewaehlt:
                pygame.draw.rect(f, FARBE["auswahl"], r, border_radius=3)
                pygame.draw.rect(f, FARBE["linie"], r, width=1, border_radius=3)
            text, markierung = self.zeilentext(eintraege[i])
            x = r.left + s.zeichen_breite // 2
            if markierung:
                zeichen, farbe = markierung
                f.blit(s.text_fett.render(zeichen, True, farbe), (x, r.top + (r.height - s.text.get_linesize()) // 2))
                x += s.zeichen_breite * 2
            bild = s.text.render(_kuerzen(text, s.text, r.right - x - 4), True,
                                 FARBE["gruen_hell"] if gewaehlt else FARBE["text"])
            f.blit(bild, (x, r.top + (r.height - bild.get_height()) // 2))
        if len(eintraege) > sichtbar:
            zahl = s.klein.render(f"{self.auswahl + 1}/{len(eintraege)} · ↑↓", True, FARBE["text_schwach"])
            f.blit(zahl, (liste.right - zahl.get_width(), innen.bottom - zahl.get_height()))

        if eintraege:
            b = Bloecke(s, self.detail_rect.width)
            self.detail(b, eintraege[self.auswahl])
            self.detail_scroll = b.zeichnen(f, self.detail_rect, self.detail_scroll)

    @property
    def art_taste(self) -> str:
        return "F4" if self.art == "befehlsbuch" else "F5"


class Befehlsbuchansicht(Nachschlagen):
    art = "befehlsbuch"
    titel = "BEFEHLSBUCH"
    reiter = ("Befehle A–Z", "Was tippe ich, wenn …?")

    def __init__(self, app: "App", system_id: str):
        super().__init__(app, system_id)
        self.buch = bb.lade(system_id)
        self.kurse = gk.alle_kurse()
        self.stand = Spielstand.lade(system_id)

    def eintraege(self) -> list:
        if self.reiter_nr == 0:
            return bb.suche_eintraege(self.buch, self.suche)
        return bb.suche_situationen(self.buch, self.suche)

    def leer_text(self) -> str:
        if not self.buch.eintraege:
            return "Für dieses System gibt es noch kein Befehlsbuch."
        return "Nichts gefunden – anderes Wort probieren."

    def _gelernt(self, lektion_id: str) -> bool:
        return self.stand.lektion(lektion_id)["fertig"]

    def zeilentext(self, eintrag):
        if isinstance(eintrag, bb.Eintrag):
            gelernt = self._gelernt(eintrag.lektion)
            return f"{eintrag.befehl}  –  {eintrag.was}", ("✓" if gelernt else "·",
                                                          FARBE["gruen"] if gelernt else FARBE["aus"])
        return "… " + eintrag.wenn.lstrip("… "), None

    def _lektion_zeile(self, b: Bloecke, lektion_id: str) -> None:
        s = self.app.schriften
        l = gk.finde_lektion(self.kurse, lektion_id)
        if l is None:
            return
        if self._gelernt(lektion_id):
            b.absatz(f"✓ Gelernt in Lektion {l.nr}: {l.titel}", s.text, FARBE["gruen"])
        else:
            b.absatz(f"Kommt in Lektion {l.nr}: {l.titel} (Grundkurs)", s.text, FARBE["text_schwach"])

    def detail(self, b: Bloecke, eintrag) -> None:
        s = self.app.schriften
        if isinstance(eintrag, bb.Situation):
            b.absatz("Was tippe ich, wenn", s.klein, FARBE["text_schwach"])
            b.absatz(eintrag.wenn, s.zwischen, FARBE["gruen_hell"])
            b.ueberschrift("SO GEHT'S")
            b.kasten([(z, s.mono_fett, FARBE["gruen"]) for z in eintrag.befehle])
            if eintrag.erklaerung:
                b.absatz(eintrag.erklaerung)
            b.ueberschrift("GEÜBT IN")
            self._lektion_zeile(b, eintrag.lektion)
            return
        e = eintrag
        b.absatz(e.befehl, s.zwischen, FARBE["gruen_hell"])
        b.absatz(e.was)
        b.ueberschrift("BEISPIEL")
        b.kasten([(e.beispiel, s.mono_fett, FARBE["gruen"])])
        if e.auch:
            b.absatz("Geht auch: " + "  ·  ".join(e.auch), s.klein_mono, FARBE["text_schwach"])
        if e.parameter:
            b.ueberschrift("WICHTIGE ZUSÄTZE (PARAMETER)")
            for name, text in e.parameter.items():
                b.absatz(name, s.mono_fett, FARBE["gruen"])
                b.absatz(text, einzug=s.zeichen_breite * 2)
        b.ueberschrift("WANN BRAUCHE ICH DAS?")
        b.absatz(e.wann)
        b.ueberschrift("GRUNDKURS")
        self._lektion_zeile(b, e.lektion)
        b.ueberschrift("QUELLE")
        for q in e.quelle:
            b.absatz(q, s.klein, FARBE["text_schwach"])


class Lexikonansicht(Nachschlagen):
    art = "lexikon"
    titel = "LEXIKON"

    def __init__(self, app: "App", system_id: str):
        super().__init__(app, system_id)
        lektionen = gk.lade_kurs(system_id).lektionen
        szenarien = lade_system(system_id).szenarien
        self.begriffe = bb.lexikon(lektionen, szenarien)

    def eintraege(self) -> list:
        return bb.suche_begriffe(self.begriffe, self.suche)

    def zeilentext(self, eintrag):
        return eintrag.name, None

    def detail(self, b: Bloecke, eintrag) -> None:
        s = self.app.schriften
        b.absatz(eintrag.name, s.zwischen, FARBE["gruen_hell"])
        b.absatz(eintrag.erklaerung)
        b.ueberschrift("KOMMT VOR IN")
        for ort in eintrag.vorkommen:
            b.absatz("· " + ort, s.text, FARBE["text_schwach"])
