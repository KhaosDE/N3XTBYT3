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
