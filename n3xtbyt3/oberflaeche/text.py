"""Text umbrechen – für Terminal (feste Breite) und Seitenbereich (Wortumbruch)."""

from __future__ import annotations

import pygame


def umbrechen_fest(text: str, spalten: int) -> list[str]:
    """Bricht nach einer festen Zeichenzahl um (wie ein echtes Terminal)."""
    spalten = max(1, spalten)
    if not text:
        return [""]
    zeilen = []
    for zeile in text.split("\n"):
        if not zeile:
            zeilen.append("")
            continue
        for i in range(0, len(zeile), spalten):
            zeilen.append(zeile[i:i + spalten])
    return zeilen


def umbrechen(text: str, font: pygame.font.Font, breite: int) -> list[str]:
    """Bricht an Wortgrenzen um, sodass jede Zeile höchstens ``breite`` Pixel breit ist."""
    ergebnis: list[str] = []
    for absatz in text.split("\n"):
        if not absatz.strip():
            ergebnis.append("")
            continue
        woerter = absatz.split(" ")
        zeile = ""
        for wort in woerter:
            versuch = wort if not zeile else zeile + " " + wort
            if font.size(versuch)[0] <= breite:
                zeile = versuch
                continue
            if zeile:
                ergebnis.append(zeile)
            # Wort ist allein zu lang: hart trennen
            while font.size(wort)[0] > breite and len(wort) > 1:
                n = len(wort)
                while n > 1 and font.size(wort[:n])[0] > breite:
                    n -= 1
                ergebnis.append(wort[:n])
                wort = wort[n:]
            zeile = wort
        ergebnis.append(zeile)
    return ergebnis


def umbrechen_woerter_fest(text: str, spalten: int, einzug: int = 0) -> list[str]:
    """Wortumbruch bei fester Zeichenbreite; Folgezeilen werden eingerückt."""
    spalten = max(einzug + 10, spalten)
    if len(text) <= spalten:
        return [text]
    zeilen: list[str] = []
    rest = text
    erste = True
    while rest:
        breite = spalten if erste else spalten - einzug
        if len(rest) <= breite:
            zeilen.append(rest if erste else " " * einzug + rest)
            break
        schnitt = rest.rfind(" ", 0, breite + 1)
        fuehrend = len(rest) - len(rest.lstrip(" "))
        if schnitt <= fuehrend:
            schnitt = breite
        teil, rest = rest[:schnitt].rstrip(), rest[schnitt:].lstrip()
        zeilen.append(teil if erste else " " * einzug + teil)
        erste = False
    return zeilen


def kuerzen(text: str, font: pygame.font.Font, breite: int) -> str:
    """Kürzt mit „…“, bis der Text höchstens ``breite`` Pixel breit ist."""
    if font.size(text)[0] <= breite:
        return text
    while text and font.size(text + "…")[0] > breite:
        text = text[:-1]
    return text + "…"


TRENNER = "  ·  "


def fuss_zeilen(text: str, font: pygame.font.Font, breite: int) -> list[str]:
    """Teilt eine Tastenleiste („F1 …  ·  F2 …“) an den Trennern auf Zeilen, die in ``breite`` passen."""
    zeilen: list[str] = []
    aktuell = ""
    for teil in text.split(TRENNER):
        versuch = teil if not aktuell else aktuell + TRENNER + teil
        if not aktuell or font.size(versuch)[0] <= breite:
            aktuell = versuch
        else:
            zeilen.append(aktuell)
            aktuell = teil
    zeilen.append(aktuell)
    return [kuerzen(z, font, breite) for z in zeilen]


def zeichne_fuss(flaeche: pygame.Surface, font: pygame.font.Font, text: str, farbe, unten: int,
                 rand: int = 0, max_zeilen: int = 3) -> int:
    """Zeichnet eine Tastenleiste mittig, unten bündig bei ``unten``. Gibt die Höhe zurück."""
    breite = flaeche.get_width()
    zeilen = fuss_zeilen(text, font, breite - 2 * rand)[:max_zeilen]
    y = unten
    for zeile in reversed(zeilen):
        bild = font.render(zeile, True, farbe)
        flaeche.blit(bild, bild.get_rect(midbottom=(breite // 2, y)))
        y -= font.get_linesize()
    return unten - y
