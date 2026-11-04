"""Lernkartei: Szenarien und Befehle wandern durch fünf Fächer.

Jede Karte liegt in einem Fach (1–5). Je höher das Fach, desto länger dauert es,
bis die Karte wieder dran ist (Wiederholung in wachsenden Abständen):

    Fach 1: sofort · 2: nach 1 Tag · 3: nach 3 Tagen · 4: nach 7 Tagen · 5: nach 14 Tagen

Szenario-Karten nach einem Versuch:
    gelöst ohne Hinweis und mit höchstens 2 falschen Befehlen → ein Fach weiter
    gelöst mit 1 Hinweis (oder mehr falschen Befehlen)          → Fach bleibt
    gelöst mit 2 oder 3 Hinweisen                                → ein Fach zurück
    nicht gelöst                                                 → zurück in Fach 1

Befehls-Karten (Befehls-Training):
    richtig → ein Fach weiter · halb richtig → Fach bleibt · falsch → zurück in Fach 1

Gespeichert wird alles im Spielstand des Systems unter ``lernkartei``.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any

FAECHER = 5
ABSTAND_TAGE = {1: 0, 2: 1, 3: 3, 4: 7, 5: 14}


def heute() -> _dt.date:
    return _dt.date.today()


def _datum(text: str | None) -> _dt.date | None:
    try:
        return _dt.date.fromisoformat(text) if text else None
    except ValueError:
        return None


class Lernkartei:
    """Sicht auf den Teil ``lernkartei`` im Spielstand (wird direkt dort geändert)."""

    def __init__(self, spielstand_daten: dict[str, Any]):
        kartei = spielstand_daten.setdefault("lernkartei", {})
        self.szenarien: dict[str, dict] = kartei.setdefault("szenarien", {})
        self.befehle: dict[str, dict] = kartei.setdefault("befehle", {})

    # ------------------------------------------------------------------ Karten

    @staticmethod
    def _karte(ablage: dict[str, dict], schluessel: str) -> dict:
        karte = ablage.get(schluessel)
        if not isinstance(karte, dict):
            return {"fach": 1, "faellig": None, "richtig": 0, "falsch": 0, "zuletzt": None}
        karte = dict(karte)
        karte.setdefault("fach", 1)
        karte.setdefault("faellig", None)
        karte.setdefault("richtig", 0)
        karte.setdefault("falsch", 0)
        karte.setdefault("zuletzt", None)
        return karte

    def szenario(self, szenario_id: str) -> dict:
        return self._karte(self.szenarien, szenario_id)

    def befehl(self, schluessel: str) -> dict:
        return self._karte(self.befehle, schluessel)

    @staticmethod
    def ist_faellig(karte: dict, am: _dt.date | None = None) -> bool:
        faellig = _datum(karte.get("faellig"))
        return faellig is None or faellig <= (am or heute())

    @staticmethod
    def _verschieben(karte: dict, neues_fach: int, am: _dt.date, gut: bool | None) -> dict:
        karte["fach"] = max(1, min(FAECHER, neues_fach))
        karte["faellig"] = (am + _dt.timedelta(days=ABSTAND_TAGE[karte["fach"]])).isoformat()
        karte["zuletzt"] = am.isoformat()
        if gut is True:
            karte["richtig"] += 1
        elif gut is False:
            karte["falsch"] += 1
        return karte

    # ------------------------------------------------------------------ Ergebnisse

    def szenario_ergebnis(self, szenario_id: str, ergebnis: dict, am: _dt.date | None = None) -> dict:
        am = am or heute()
        karte = self.szenario(szenario_id)
        hinweise = int(ergebnis.get("hinweise", 0))
        falsch = int(ergebnis.get("falsche_befehle", 0))
        if not ergebnis.get("geloest"):
            karte = self._verschieben(karte, 1, am, False)
        elif hinweise == 0 and falsch <= 2:
            karte = self._verschieben(karte, karte["fach"] + 1, am, True)
        elif hinweise <= 1:
            karte = self._verschieben(karte, karte["fach"], am, True)
        else:
            karte = self._verschieben(karte, karte["fach"] - 1, am, True)
        self.szenarien[szenario_id] = karte
        return karte

    def befehl_ergebnis(self, schluessel: str, bewertung: str, am: _dt.date | None = None) -> dict:
        """bewertung: "richtig", "halb" oder "falsch"."""
        am = am or heute()
        karte = self.befehl(schluessel)
        if bewertung == "richtig":
            karte = self._verschieben(karte, karte["fach"] + 1, am, True)
        elif bewertung == "halb":
            karte = self._verschieben(karte, karte["fach"], am, None)
        else:
            karte = self._verschieben(karte, 1, am, False)
        self.befehle[schluessel] = karte
        return karte
