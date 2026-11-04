"""Farben und Schriften – dunkel, grün, Neon (angelehnt an Shellbreaker)."""

from __future__ import annotations

from pathlib import Path

import pygame

SCHRIFTORDNER = Path(__file__).resolve().parent / "schriften"

FARBE = {
    "hintergrund": (4, 8, 7),
    "terminal": (6, 12, 9),
    "panel": (9, 17, 15),
    "kopf": (8, 22, 15),
    "linie": (0, 255, 136),
    "linie_dunkel": (0, 90, 52),
    "gruen": (61, 255, 122),
    "gruen_hell": (170, 255, 196),
    "gruen_dunkel": (24, 120, 60),
    "prompt": (0, 230, 92),
    "ausgabe": (120, 235, 150),
    "eingabe": (200, 255, 215),
    "fehler": (255, 96, 96),
    "sim": (64, 200, 255),
    "erfolg": (255, 230, 90),
    "magenta": (255, 80, 210),
    "text": (205, 230, 215),
    "text_schwach": (120, 150, 135),
    "warnung": (255, 166, 48),
    "warnung_text": (20, 10, 0),
    "bestaetigt": (61, 255, 122),
    "aus": (70, 90, 80),
    "auswahl": (0, 60, 36),
}

ZEILENART_FARBE = {
    "eingabe": "eingabe",
    "ausgabe": "ausgabe",
    "fehler": "fehler",
    "sim": "sim",
    "erfolg": "erfolg",
}


def _font(datei: str, groesse: int, ersatz: str, fett: bool = False) -> pygame.font.Font:
    pfad = SCHRIFTORDNER / datei
    if pfad.exists():
        return pygame.font.Font(str(pfad), groesse)
    return pygame.font.SysFont(ersatz, groesse, bold=fett)


class Schriften:
    """Alle Schriften in einer Grundgröße (einstellbar)."""

    def __init__(self, groesse: int):
        self.groesse = groesse
        mono = "consolas,dejavusansmono,liberationmono,couriernew,monospace"
        sans = "segoeui,dejavusans,arial,sans"
        self.mono = _font("DejaVuSansMono.ttf", groesse, mono)
        self.mono_fett = _font("DejaVuSansMono-Bold.ttf", groesse, mono, True)
        self.text = _font("DejaVuSans.ttf", max(10, int(groesse * 0.92)), sans)
        self.text_fett = _font("DejaVuSans-Bold.ttf", max(10, int(groesse * 0.92)), sans, True)
        self.klein = _font("DejaVuSans.ttf", max(9, int(groesse * 0.78)), sans)
        self.klein_mono = _font("DejaVuSansMono.ttf", max(9, int(groesse * 0.78)), mono)
        self.zwischen = _font("DejaVuSansMono-Bold.ttf", int(groesse * 1.25), mono, True)
        self.titel = _font("DejaVuSansMono-Bold.ttf", int(groesse * 3.2), mono, True)
        self.zeichen_breite = max(1, self.mono.size("M")[0])
        self.zeilen_hoehe = self.mono.get_linesize()


def glow_text(flaeche: pygame.Surface, font: pygame.font.Font, text: str,
              farbe: tuple[int, int, int], pos: tuple[int, int], staerke: int = 2,
              mitte: bool = False) -> pygame.Rect:
    """Text mit leichtem Neon-Schein."""
    bild = font.render(text, True, farbe)
    schein = font.render(text, True, tuple(c // 3 for c in farbe))
    x, y = pos
    if mitte:
        x -= bild.get_width() // 2
    for dx in range(-staerke, staerke + 1):
        for dy in range(-staerke, staerke + 1):
            if dx or dy:
                flaeche.blit(schein, (x + dx, y + dy))
    return flaeche.blit(bild, (x, y))
