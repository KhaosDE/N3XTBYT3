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


def lies_json_genau(name: str) -> tuple[Any | None, str | None, bool]:
    """Liest eine JSON-Datei aus dem Datenordner.

    Rückgabe: (Daten, Warnung, nicht_ueberschreiben).

    * Fehlt die Datei: (None, None, False).
    * Ist der Inhalt kaputt (kein JSON, falsche Zeichenkodierung): Die Datei wird zur Sicherheit
      umbenannt (…defekt-<Zeit>.json) und (None, Warnung, False) zurückgegeben.
    * Lässt sie sich gerade nicht lesen (z. B. von einem anderen Programm gesperrt) oder klappt das
      Umbenennen nicht: (None, Warnung, True) – dann darf sie nicht überschrieben werden, sonst wäre
      der alte Inhalt verloren.
    """
    pfad = pfade.im_datenordner(name)
    if not pfad.exists():
        return None, None, False
    try:
        roh = pfad.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as e:
        fehler: Exception = e
    except OSError as e:
        return None, (f"{pfad.name} ließ sich gerade nicht lesen ({e}). Zum Schutz wird nichts gespeichert – "
                      "bitte das Programm neu starten."), True
    else:
        try:
            return json.loads(roh), None, False
        except json.JSONDecodeError as e:
            fehler = e
    stempel = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    sicherung = pfad.with_name(f"{pfad.stem}.defekt-{stempel}{pfad.suffix}")
    try:
        os.replace(pfad, sicherung)
    except OSError:
        return None, (f"{pfad.name} ist beschädigt ({fehler}) und ließ sich nicht sichern. Zum Schutz wird "
                      "nichts gespeichert."), True
    return None, f"{pfad.name} ließ sich nicht lesen ({fehler}). Die alte Datei liegt jetzt unter {sicherung.name}.", False


def lies_json(name: str) -> tuple[Any | None, str | None]:
    """Wie lies_json_genau, ohne die Angabe zum Überschreiben (für Einstellungen)."""
    daten, warnung, _ = lies_json_genau(name)
    return daten, warnung
