"""Lesbare JSON-Dateien im Datenordner lesen und sicher schreiben."""

from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path
from typing import Any

from . import pfade


def schreibe_json(name: str, daten: Any) -> Path:
    """Schreibt ``daten`` als lesbares JSON in den Datenordner.

    Erst in eine Zwischendatei, dann umbenennen – so bleibt bei einem Absturz die
    alte Datei heil.
    """
    ziel = pfade.im_datenordner(name)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    zwischen = ziel.with_name(ziel.name + ".neu")
    with open(zwischen, "w", encoding="utf-8", newline="\n") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(zwischen, ziel)
    return ziel


def schreibe_text(name: str, text: str) -> Path:
    ziel = pfade.im_datenordner(name)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    zwischen = ziel.with_name(ziel.name + ".neu")
    with open(zwischen, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(zwischen, ziel)
    return ziel


def lies_json(name: str) -> tuple[Any | None, str | None]:
    """Liest eine JSON-Datei aus dem Datenordner.

    Rückgabe: (Daten, Warnung). Fehlt die Datei: (None, None). Ist sie kaputt, wird sie
    zur Sicherheit umbenannt und (None, Warnung) zurückgegeben.
    """
    pfad = pfade.im_datenordner(name)
    if not pfad.exists():
        return None, None
    try:
        return json.loads(pfad.read_text(encoding="utf-8-sig")), None
    except (OSError, json.JSONDecodeError) as e:
        stempel = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        sicherung = pfad.with_name(f"{pfad.stem}.defekt-{stempel}{pfad.suffix}")
        try:
            os.replace(pfad, sicherung)
            ort = f" Die alte Datei liegt jetzt unter {sicherung.name}."
        except OSError:
            ort = ""
        return None, f"{pfad.name} ließ sich nicht lesen ({e}).{ort}"
