"""Wo N3XTBYT3 seine Dateien findet und speichert.

* Programmdaten (mitgelieferte Szenarien): Ordner ``daten`` neben dem Paket,
  in der .exe im entpackten Programmordner.
* Datenordner (Spielstand, Einstellungen, eigene Szenarien):
  Windows ``%APPDATA%\\N3XTBYT3``, sonst ``~/.local/share/n3xtbyt3``.
  Mit der Umgebungsvariable ``N3XTBYT3_DATEN`` lässt er sich umlenken (für Tests).

Das Programm schreibt nur in den Datenordner.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def programmordner() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2]


def programmdaten() -> Path:
    return programmordner() / "daten"


def datenordner() -> Path:
    umgelenkt = os.environ.get("N3XTBYT3_DATEN")
    if umgelenkt:
        return Path(umgelenkt)
    if os.name == "nt":
        basis = os.environ.get("APPDATA")
        if basis:
            return Path(basis) / "N3XTBYT3"
        return Path.home() / "AppData" / "Roaming" / "N3XTBYT3"
    return Path.home() / ".local" / "share" / "n3xtbyt3"


def im_datenordner(*teile: str) -> Path:
    """Pfad im Datenordner. Verhindert, dass ein Pfad aus dem Ordner herausführt."""
    basis = datenordner().resolve()
    ziel = basis.joinpath(*teile).resolve()
    if ziel != basis and basis not in ziel.parents:
        raise ValueError(f"Pfad liegt außerhalb des Datenordners: {ziel}")
    return ziel
