"""Grundbausteine der Oberfläche: Ansicht, Knopf, Matrix-Regen."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

import pygame

from .stil import FARBE

if TYPE_CHECKING:
    from .app import App


class Ansicht:
    """Ein Bildschirm (Menü, Szenarioliste, Spiel)."""

    def __init__(self, app: "App"):
        self.app = app

    def ereignis(self, e: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def zeichnen(self, flaeche: pygame.Surface) -> None:
        pass

    def verlassen(self) -> None:
        """Wird aufgerufen, bevor die Ansicht wechselt oder das Programm endet."""

    def schrift_geaendert(self) -> None:
        pass


@dataclass
class Knopf:
    rect: pygame.Rect
    text: str
    aktion: Callable[[], None]
    aktiv: bool = True


def zeichne_knopf(flaeche: pygame.Surface, knopf: Knopf, font: pygame.font.Font,
                  maus: tuple[int, int]) -> None:
    ueber = knopf.aktiv and knopf.rect.collidepoint(maus)
    rand = FARBE["linie"] if knopf.aktiv else FARBE["aus"]
    pygame.draw.rect(flaeche, FARBE["auswahl"] if ueber else FARBE["panel"], knopf.rect, border_radius=4)
    pygame.draw.rect(flaeche, rand, knopf.rect, width=2, border_radius=4)
    farbe = FARBE["gruen_hell"] if knopf.aktiv else FARBE["aus"]
    bild = font.render(knopf.text, True, farbe)
    flaeche.blit(bild, bild.get_rect(center=knopf.rect.center))


def knopf_klick(knoepfe: list[Knopf], e: pygame.event.Event) -> bool:
    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
        for k in knoepfe:
            if k.aktiv and k.rect.collidepoint(e.pos):
                k.aktion()
                return True
    return False


class MatrixRegen:
    """Fallende Zeichen im Hintergrund – dezent, damit Text lesbar bleibt."""

    ZEICHEN = "0123456789ABCDEF<>/\\|=+*#$%"

    def __init__(self, font: pygame.font.Font, groesse: tuple[int, int], dichte: float = 0.6):
        self.font = font
        self.zb = max(1, font.size("M")[0])
        self.zh = font.get_linesize()
        self.breite, self.hoehe = groesse
        stufen = [(0, 255, 120), (0, 160, 75), (0, 95, 45), (0, 55, 28)]
        self.glyphen = {
            (z, i): font.render(z, True, farbe) for z in self.ZEICHEN for i, farbe in enumerate(stufen)
        }
        self.spalten = []
        rng = random.Random(7)
        anzahl = int(self.breite / (self.zb * 1.6) * dichte)
        for _ in range(max(1, anzahl)):
            self.spalten.append(self._neue_spalte(rng, start=True))
        self.rng = rng

    def _neue_spalte(self, rng: random.Random, start: bool = False) -> dict:
        laenge = rng.randint(6, 18)
        return {
            "x": rng.randrange(0, max(1, self.breite), self.zb),
            "y": rng.uniform(-self.hoehe, self.hoehe) if start else rng.uniform(-self.zh * laenge, 0),
            "v": rng.uniform(60, 180),
            "zeichen": [rng.choice(self.ZEICHEN) for _ in range(laenge)],
        }

    def update(self, dt: float) -> None:
        for i, s in enumerate(self.spalten):
            s["y"] += s["v"] * dt
            if self.rng.random() < 0.05:
                s["zeichen"][self.rng.randrange(len(s["zeichen"]))] = self.rng.choice(self.ZEICHEN)
            if s["y"] - len(s["zeichen"]) * self.zh > self.hoehe:
                self.spalten[i] = self._neue_spalte(self.rng)

    def zeichnen(self, flaeche: pygame.Surface) -> None:
        for s in self.spalten:
            n = len(s["zeichen"])
            for j, z in enumerate(s["zeichen"]):
                y = s["y"] - j * self.zh
                if -self.zh < y < self.hoehe:
                    stufe = 0 if j == 0 else min(3, 1 + j * 3 // n)
                    flaeche.blit(self.glyphen[(z, stufe)], (s["x"], y))
