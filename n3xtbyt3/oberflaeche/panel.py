"""Seitenbereich aus Textblöcken mit Blättern – für Lektion, Befehlsbuch und Lexikon."""

from __future__ import annotations

import pygame

from .stil import FARBE, Schriften
from .text import umbrechen


class Bloecke:
    """Sammelt Zeilen (umgebrochen), Überschriften, Abstände und Etiketten für eine feste Breite."""

    def __init__(self, s: Schriften, breite: int):
        self.s = s
        self.breite = breite
        self.liste: list[tuple] = []

    def absatz(self, text: str, font=None, farbe=None, einzug: int = 0) -> None:
        font = font or self.s.text
        for zeile in umbrechen(text, font, max(10, self.breite - einzug)):
            self.liste.append(("zeile", zeile, font, farbe or FARBE["text"], einzug))

    def ueberschrift(self, text: str, farbe=None) -> None:
        self.abstand(self.s.zeilen_hoehe // 2)
        zeilen = umbrechen(text, self.s.mono_fett, max(10, self.breite))
        for i, zeile in enumerate(zeilen):
            self.liste.append(("ueberschrift", zeile, farbe or FARBE["magenta"], i == len(zeilen) - 1))

    def abstand(self, hoehe: int) -> None:
        self.liste.append(("abstand", hoehe))

    def etiketten(self, eintraege: list[tuple[str, tuple, tuple]]) -> None:
        """Eine Zeile kleiner Etiketten: (Text, Hintergrund, Schrift)."""
        self.liste.append(("etiketten", eintraege))

    def kasten(self, zeilen: list[tuple[str, object, tuple]], rand=None) -> None:
        """Hervorgehobener Kasten, z. B. „Tippe: …“. zeilen: (Text, Schrift, Farbe)."""
        innen = self.breite - 2 * self.s.zeichen_breite
        gebrochen = []
        for text, font, farbe in zeilen:
            for z in umbrechen(text, font, max(10, innen)):
                gebrochen.append((z, font, farbe))
        self.liste.append(("kasten", gebrochen, rand or FARBE["linie"]))

    # ------------------------------------------------------------------ Höhe und Zeichnen

    def _hoehe(self, b: tuple) -> int:
        s = self.s
        if b[0] == "zeile":
            return b[2].get_linesize()
        if b[0] == "abstand":
            return b[1]
        if b[0] == "ueberschrift":
            return s.mono_fett.get_linesize() + (6 if b[3] else 0)
        if b[0] == "etiketten":
            return int(s.klein.get_linesize() * 1.5)
        if b[0] == "kasten":
            return sum(font.get_linesize() for _, font, _ in b[1]) + s.zeilen_hoehe
        return 0

    def gesamt(self) -> int:
        return sum(self._hoehe(b) for b in self.liste)

    def zeichnen(self, f: pygame.Surface, rect: pygame.Rect, scroll: int) -> int:
        """Zeichnet die Blöcke in rect, ab ``scroll`` Pixeln. Gibt den begrenzten Scrollwert zurück."""
        s = self.s
        gesamt = self.gesamt()
        scroll = max(0, min(scroll, max(0, gesamt - rect.height)))
        alt_clip = f.get_clip()
        f.set_clip(rect)
        y = rect.top - scroll
        for b in self.liste:
            hoehe = self._hoehe(b)
            if y + hoehe >= rect.top and y <= rect.bottom:
                if b[0] == "zeile":
                    _, text, font, farbe, einzug = b
                    if text:
                        f.blit(font.render(text, True, farbe), (rect.left + einzug, y))
                elif b[0] == "ueberschrift":
                    _, text, farbe, letzte = b
                    f.blit(s.mono_fett.render(text, True, farbe), (rect.left, y))
                    if letzte:
                        ly = y + s.mono_fett.get_linesize() + 1
                        pygame.draw.line(f, FARBE["linie_dunkel"], (rect.left, ly), (rect.right, ly), 1)
                elif b[0] == "etiketten":
                    x = rect.left
                    for text, hinter, vorder in b[1]:
                        bild = s.klein.render(f" {text} ", True, vorder)
                        r = pygame.Rect(x, y + 3, bild.get_width() + 4, bild.get_height())
                        pygame.draw.rect(f, hinter, r, border_radius=3)
                        f.blit(bild, (x + 2, y + 3))
                        x += r.width + s.zeichen_breite
                elif b[0] == "kasten":
                    _, zeilen, rand = b
                    kasten = pygame.Rect(rect.left, y + s.zeilen_hoehe // 4, rect.width, hoehe - s.zeilen_hoehe // 2)
                    pygame.draw.rect(f, FARBE["auswahl"], kasten, border_radius=5)
                    pygame.draw.rect(f, rand, kasten, width=2, border_radius=5)
                    ty = kasten.top + s.zeilen_hoehe // 4
                    for text, font, farbe in zeilen:
                        f.blit(font.render(text, True, farbe), (kasten.left + s.zeichen_breite, ty))
                        ty += font.get_linesize()
            y += hoehe
        f.set_clip(alt_clip)
        if gesamt > rect.height:
            anteil = rect.height / gesamt
            balken_h = max(20, int(rect.height * anteil))
            balken_y = rect.top + int((rect.height - balken_h) * (scroll / max(1, gesamt - rect.height)))
            pygame.draw.rect(f, FARBE["linie_dunkel"], (rect.right + 4, balken_y, 4, balken_h), border_radius=2)
        return scroll
