"""Eingaben zerlegen und mit den Befehlsmustern der Szenarien vergleichen.

Ein Muster ist eine Befehlszeile, wie sie im echten System eingegeben würde, z. B.
``taskkill /IM EXCEL.EXE /F``. Eine Eingabe passt, wenn

* die Wörter genau übereinstimmen, oder
* der Befehlsname und die Wörter vor der ersten Option gleich sind und die Optionen
  (eine Option samt den Werten dahinter) in beliebiger Reihenfolge vorkommen.
  ``taskkill /F /IM EXCEL.EXE`` passt also auch.

Unter Windows zählt Groß-/Kleinschreibung nicht, unter Linux schon.
Ein ``*`` im Muster steht für genau ein beliebiges Wort.
Pipes (``|``) trennen Abschnitte, die einzeln und der Reihe nach verglichen werden.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .systeme import System

PLATZHALTER = "*"
_VERB_NOMEN = re.compile(r"^[A-Za-z]+-[A-Za-z]+$")


def zerlege(text: str) -> list[list[str]]:
    """Teilt eine Eingabe in Abschnitte (getrennt durch |) und Wörter.

    Anführungszeichen (" und ') fassen Wörter mit Leerzeichen zusammen und werden
    entfernt. Ein Backslash ist ein normales Zeichen (Windows-Pfade).
    """
    abschnitte: list[list[str]] = [[]]
    wort: list[str] = []
    hat_wort = False
    quote: str | None = None
    for zeichen in text:
        if quote:
            if zeichen == quote:
                quote = None
            else:
                wort.append(zeichen)
            continue
        if zeichen in ("\"", "'"):
            quote = zeichen
            hat_wort = True
        elif zeichen.isspace():
            if hat_wort:
                abschnitte[-1].append("".join(wort))
                wort, hat_wort = [], False
        elif zeichen == "|":
            if hat_wort:
                abschnitte[-1].append("".join(wort))
                wort, hat_wort = [], False
            abschnitte.append([])
        else:
            wort.append(zeichen)
            hat_wort = True
    if hat_wort:
        abschnitte[-1].append("".join(wort))
    return abschnitte


def befehlsname(text: str) -> str:
    """Das erste Wort einer Eingabe (oder leerer Text)."""
    abschnitte = zerlege(text)
    if abschnitte and abschnitte[0]:
        return abschnitte[0][0]
    return ""


def ist_cmdlet_name(name: str) -> bool:
    """PowerShell-Befehle heißen Verb-Nomen, z. B. Get-Service."""
    return bool(_VERB_NOMEN.match(name))


@dataclass(frozen=True)
class _Abschnitt:
    woerter: tuple[str, ...]
    name: str
    positionen: tuple[str, ...]
    einheiten: tuple[tuple[str, ...], ...]


class Vergleicher:
    """Vergleicht Eingaben und Muster nach den Regeln eines Systems."""

    def __init__(self, system: System):
        self.system = system

    def norm(self, wort: str) -> str:
        return wort.casefold() if self.system.gross_klein_egal else wort

    def norm_name(self, name: str) -> str:
        name = self.norm(name)
        # Unter Windows ist "ipconfig.exe" dasselbe Programm wie "ipconfig".
        if self.system.gross_klein_egal and name.endswith(".exe") and len(name) > 4:
            name = name[:-4]
        return name

    def _ist_option(self, wort: str) -> bool:
        return len(wort) > 1 and wort[0] in self.system.options_zeichen

    def _abschnitt(self, woerter: list[str]) -> _Abschnitt:
        normiert = [self.norm(w) for w in woerter]
        if normiert:
            normiert[0] = self.norm_name(woerter[0])
        name = normiert[0] if normiert else ""
        rest = normiert[1:]
        positionen: list[str] = []
        einheiten: list[list[str]] = []
        for wort in rest:
            if self._ist_option(wort):
                einheiten.append([wort])
            elif einheiten:
                einheiten[-1].append(wort)
            else:
                positionen.append(wort)
        return _Abschnitt(tuple(normiert), name, tuple(positionen), tuple(tuple(e) for e in einheiten))

    def vorbereiten(self, text: str) -> tuple[_Abschnitt, ...]:
        return tuple(self._abschnitt(a) for a in zerlege(text))

    @staticmethod
    def _folge_passt(muster: tuple[str, ...], eingabe: tuple[str, ...]) -> bool:
        if len(muster) != len(eingabe):
            return False
        return all(m == PLATZHALTER or m == e for m, e in zip(muster, eingabe))

    def _abschnitt_passt(self, muster: _Abschnitt, eingabe: _Abschnitt) -> bool:
        if self._folge_passt(muster.woerter, eingabe.woerter):
            return True
        if muster.name != eingabe.name:
            return False
        if not self._folge_passt(muster.positionen, eingabe.positionen):
            return False
        if len(muster.einheiten) != len(eingabe.einheiten):
            return False
        frei = list(eingabe.einheiten)
        for einheit in muster.einheiten:
            for i, kandidat in enumerate(frei):
                if self._folge_passt(einheit, kandidat):
                    del frei[i]
                    break
            else:
                return False
        return True

    def passt(self, muster: tuple[_Abschnitt, ...], eingabe: tuple[_Abschnitt, ...]) -> bool:
        if len(muster) != len(eingabe):
            return False
        return all(self._abschnitt_passt(m, e) for m, e in zip(muster, eingabe))
