"""Spielstand je System als lesbare JSON-Datei im Datenordner.

Datei: ``spielstand_<system>.json``. Je Szenario werden gespeichert:
Versuche, gelöst ja/nein, benutzte Hinweisstufen, falsche und unbekannte Befehle,
Zeit – und ein kurzer Verlauf der letzten Versuche.
"""

from __future__ import annotations

import copy
from typing import Any, Iterable

from .dateien import lies_json, schreibe_json
from .lernkartei import Lernkartei

VERSION = 1
VERLAUF_MAX = 30

LEERER_EINTRAG: dict[str, Any] = {
    "versuche": 0,
    "geloest": False,
    "geloest_anzahl": 0,
    "hinweise_gesamt": 0,
    "hinweise_max": 0,
    "falsche_befehle": 0,
    "unbekannte_befehle": 0,
    "zeit_sekunden": 0,
    "zuletzt": None,
    "verlauf": [],
}


def dateiname(system_id: str) -> str:
    return f"spielstand_{system_id}.json"


class Spielstand:
    def __init__(self, system_id: str, daten: dict[str, Any] | None = None):
        self.system_id = system_id
        self.warnung: str | None = None
        self.daten: dict[str, Any] = {"version": VERSION, "system": system_id, "szenarien": {}}
        if daten and isinstance(daten.get("szenarien"), dict):
            self.daten["szenarien"] = daten["szenarien"]
            for k, v in daten.items():
                if k not in self.daten:
                    self.daten[k] = v  # z. B. Lernkartei aus späteren Versionen

    @classmethod
    def lade(cls, system_id: str) -> "Spielstand":
        daten, warnung = lies_json(dateiname(system_id))
        stand = cls(system_id, daten if isinstance(daten, dict) else None)
        stand.warnung = warnung
        return stand

    @property
    def kartei(self) -> Lernkartei:
        return Lernkartei(self.daten)

    def speichere(self) -> None:
        schreibe_json(dateiname(self.system_id), self.daten)

    # ------------------------------------------------------------------ Lesen

    def eintrag(self, szenario_id: str) -> dict[str, Any]:
        """Eintrag eines Szenarios (bei neuen Szenarien leer). Fehlende Felder werden ergänzt."""
        roh = self.daten["szenarien"].get(szenario_id)
        eintrag = copy.deepcopy(LEERER_EINTRAG)
        if isinstance(roh, dict):
            eintrag.update(roh)
        return eintrag

    def gesehen(self, szenario_id: str) -> bool:
        return szenario_id in self.daten["szenarien"]

    def anzahl_geloest(self, szenario_ids: Iterable[str]) -> int:
        return sum(1 for i in szenario_ids if self.eintrag(i)["geloest"])

    # ------------------------------------------------------------------ Schreiben

    def versuch_eintragen(self, szenario_id: str, ergebnis: dict[str, Any]) -> bool:
        """Trägt einen Versuch ein. Ein Versuch ohne Befehle und Hinweise zählt nicht.

        Gibt zurück, ob etwas eingetragen wurde.
        """
        if not ergebnis.get("geloest") and not ergebnis.get("befehle") and not ergebnis.get("hinweise"):
            return False
        e = self.eintrag(szenario_id)
        e["versuche"] += 1
        if ergebnis.get("geloest"):
            e["geloest"] = True
            e["geloest_anzahl"] += 1
        e["hinweise_gesamt"] += int(ergebnis.get("hinweise", 0))
        e["hinweise_max"] = max(e["hinweise_max"], int(ergebnis.get("hinweise", 0)))
        e["falsche_befehle"] += int(ergebnis.get("falsche_befehle", 0))
        e["unbekannte_befehle"] += int(ergebnis.get("unbekannte_befehle", 0))
        e["zeit_sekunden"] += int(ergebnis.get("sekunden", 0))
        e["zuletzt"] = ergebnis.get("datum")
        e["verlauf"] = (e["verlauf"] + [dict(ergebnis)])[-VERLAUF_MAX:]
        self.daten["szenarien"][szenario_id] = e
        self.kartei.szenario_ergebnis(szenario_id, ergebnis)
        return True
