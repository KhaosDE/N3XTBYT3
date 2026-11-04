"""Einfacher Texteditor (nano-Ersatz) ohne Oberfläche – nur Text und Cursor."""

from __future__ import annotations


class EditorPuffer:
    def __init__(self, pfad: str, inhalt: str, nur_lesen: bool = False, neu: bool = False):
        self.pfad = pfad
        self.zeilen: list[str] = inhalt.split("\n") if inhalt else [""]
        self.zeile = 0
        self.spalte = 0
        self.nur_lesen = nur_lesen
        self.neu = neu
        self.geaendert = False

    @property
    def text(self) -> str:
        return "\n".join(self.zeilen)

    def _begrenzen(self) -> None:
        self.zeile = max(0, min(self.zeile, len(self.zeilen) - 1))
        self.spalte = max(0, min(self.spalte, len(self.zeilen[self.zeile])))

    # ------------------------------------------------------------------ Bewegen

    def links(self) -> None:
        if self.spalte > 0:
            self.spalte -= 1
        elif self.zeile > 0:
            self.zeile -= 1
            self.spalte = len(self.zeilen[self.zeile])

    def rechts(self) -> None:
        if self.spalte < len(self.zeilen[self.zeile]):
            self.spalte += 1
        elif self.zeile < len(self.zeilen) - 1:
            self.zeile += 1
            self.spalte = 0

    def hoch(self, n: int = 1) -> None:
        self.zeile -= n
        self._begrenzen()

    def runter(self, n: int = 1) -> None:
        self.zeile += n
        self._begrenzen()

    def zeilenanfang(self) -> None:
        self.spalte = 0

    def zeilenende(self) -> None:
        self.spalte = len(self.zeilen[self.zeile])

    # ------------------------------------------------------------------ Ändern

    def einfuegen(self, text: str) -> None:
        if self.nur_lesen:
            return
        for i, teil in enumerate(text.replace("\r", "").split("\n")):
            if i:
                self.neue_zeile()
            z = self.zeilen[self.zeile]
            self.zeilen[self.zeile] = z[: self.spalte] + teil + z[self.spalte:]
            self.spalte += len(teil)
        self.geaendert = True

    def neue_zeile(self) -> None:
        if self.nur_lesen:
            return
        z = self.zeilen[self.zeile]
        self.zeilen[self.zeile] = z[: self.spalte]
        self.zeilen.insert(self.zeile + 1, z[self.spalte:])
        self.zeile += 1
        self.spalte = 0
        self.geaendert = True

    def rueckschritt(self) -> None:
        if self.nur_lesen:
            return
        if self.spalte > 0:
            z = self.zeilen[self.zeile]
            self.zeilen[self.zeile] = z[: self.spalte - 1] + z[self.spalte:]
            self.spalte -= 1
        elif self.zeile > 0:
            vorher = self.zeilen[self.zeile - 1]
            self.zeilen[self.zeile - 1] = vorher + self.zeilen.pop(self.zeile)
            self.zeile -= 1
            self.spalte = len(vorher)
        else:
            return
        self.geaendert = True

    def entfernen(self) -> None:
        if self.nur_lesen:
            return
        z = self.zeilen[self.zeile]
        if self.spalte < len(z):
            self.zeilen[self.zeile] = z[: self.spalte] + z[self.spalte + 1:]
        elif self.zeile < len(self.zeilen) - 1:
            self.zeilen[self.zeile] = z + self.zeilen.pop(self.zeile + 1)
        else:
            return
        self.geaendert = True

    def zeile_ausschneiden(self) -> None:
        """Wie Strg+K in nano: aktuelle Zeile entfernen."""
        if self.nur_lesen:
            return
        if len(self.zeilen) > 1:
            self.zeilen.pop(self.zeile)
        else:
            self.zeilen = [""]
        self._begrenzen()
        self.geaendert = True
