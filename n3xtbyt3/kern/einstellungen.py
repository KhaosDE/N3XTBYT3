"""Einstellungen (Schriftgröße, Vollbild, Selbst-Update) im Datenordner."""

from __future__ import annotations

from typing import Any

from .dateien import lies_json, schreibe_json

DATEI = "einstellungen.json"
SCHRIFT_MIN = 12
SCHRIFT_MAX = 40
STANDARD: dict[str, Any] = {"schriftgroesse": 20, "vollbild": False, "auto_update": True}


def lade() -> dict[str, Any]:
    daten, _warnung = lies_json(DATEI)
    werte = dict(STANDARD)
    if isinstance(daten, dict):
        groesse = daten.get("schriftgroesse")
        if isinstance(groesse, int) and not isinstance(groesse, bool):
            werte["schriftgroesse"] = max(SCHRIFT_MIN, min(SCHRIFT_MAX, groesse))
        if isinstance(daten.get("vollbild"), bool):
            werte["vollbild"] = daten["vollbild"]
        if isinstance(daten.get("auto_update"), bool):
            werte["auto_update"] = daten["auto_update"]
    return werte


def speichere(werte: dict[str, Any]) -> None:
    schreibe_json(DATEI, {k: werte.get(k, v) for k, v in STANDARD.items()})
