"""Simulierter Zustand eines Szenarios.

Der Zustand ist eine flache Tabelle aus Schlüssel und Wert, z. B.
``{"dienst_spooler": "Running", "frei_gb": 0.8, "admin": true}``.
Werte sind Text, Zahl, Wahrheitswert oder ``null``.

Bedingungen (``wenn`` und ``ziel``) vergleichen Schlüssel mit Werten:

* einfacher Wert: muss gleich sein, z. B. ``{"admin": true}``
* Vergleich: ``{"frei_gb": {">=": 10}}``; erlaubt sind
  ``nicht``, ``in``, ``<``, ``<=``, ``>``, ``>=``, ``enthaelt``, ``enthaelt_nicht``
  (prüfen, ob ein Text einen Teiltext enthält), ``zeile_enthaelt``, ``keine_zeile_enthaelt``
  (wie enthaelt, aber nur in Zeilen, die keine Kommentare sind – für Konfigurationsdateien)

Änderungen (``setze``) schreiben Werte; ``{"+": 1}`` bzw. ``{"-": 1}`` rechnen.
"""

from __future__ import annotations

import re
from typing import Any

VERGLEICHE = ("nicht", "in", "<", "<=", ">", ">=", "enthaelt", "enthaelt_nicht",
              "zeile_enthaelt", "keine_zeile_enthaelt")
RECHNUNGEN = ("+", "-")
SKALAR = (str, int, float, bool, type(None))

_PLATZHALTER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_.]*)\}")


def ist_skalar(wert: Any) -> bool:
    return isinstance(wert, SKALAR)


def _gleich(a: Any, b: Any) -> bool:
    # true == 1 soll nicht als gleich gelten.
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    return a == b


def _zahl(wert: Any) -> bool:
    return isinstance(wert, (int, float)) and not isinstance(wert, bool)


def bedingung_erfuellt(werte: dict[str, Any], bedingung: dict[str, Any]) -> bool:
    for schluessel, soll in bedingung.items():
        ist = werte.get(schluessel)
        if isinstance(soll, dict):
            (op, vergleich), = soll.items()
            if op == "nicht":
                if _gleich(ist, vergleich):
                    return False
            elif op == "in":
                if not any(_gleich(ist, v) for v in vergleich):
                    return False
            elif op == "enthaelt":
                if not isinstance(ist, str) or vergleich not in ist:
                    return False
            elif op == "enthaelt_nicht":
                if isinstance(ist, str) and vergleich in ist:
                    return False
            elif op in ("zeile_enthaelt", "keine_zeile_enthaelt"):
                gefunden = isinstance(ist, str) and any(
                    vergleich in z for z in ist.split("\n") if not z.lstrip().startswith(("#", ";")))
                if gefunden != (op == "zeile_enthaelt"):
                    return False
            else:
                if not (_zahl(ist) and _zahl(vergleich)):
                    return False
                if op == "<" and not ist < vergleich:
                    return False
                if op == "<=" and not ist <= vergleich:
                    return False
                if op == ">" and not ist > vergleich:
                    return False
                if op == ">=" and not ist >= vergleich:
                    return False
        elif not _gleich(ist, soll):
            return False
    return True


def pruefe_bedingung(bedingung: Any, bekannte: set[str], ort: str) -> list[str]:
    """Prüft eine Bedingung auf Form und bekannte Schlüssel. Gibt Fehlertexte zurück."""
    fehler: list[str] = []
    if not isinstance(bedingung, dict) or not bedingung:
        return [f"{ort}: muss ein nicht leeres Objekt sein, z. B. {{\"dienst\": \"Running\"}}."]
    for schluessel, soll in bedingung.items():
        if schluessel not in bekannte:
            fehler.append(f"{ort}: Schlüssel „{schluessel}“ steht nicht im „zustand“.")
        if isinstance(soll, dict):
            if len(soll) != 1 or next(iter(soll)) not in VERGLEICHE:
                fehler.append(
                    f"{ort}: Vergleich bei „{schluessel}“ muss genau einer von "
                    f"{', '.join(VERGLEICHE)} sein."
                )
                continue
            (op, wert), = soll.items()
            if op == "in":
                if not isinstance(wert, list) or not all(ist_skalar(v) for v in wert):
                    fehler.append(f"{ort}: „in“ bei „{schluessel}“ braucht eine Liste von Werten.")
            elif op == "nicht":
                if not ist_skalar(wert):
                    fehler.append(f"{ort}: „nicht“ bei „{schluessel}“ braucht einen einfachen Wert.")
            elif op in ("enthaelt", "enthaelt_nicht", "zeile_enthaelt", "keine_zeile_enthaelt"):
                if not isinstance(wert, str) or not wert:
                    fehler.append(f"{ort}: „{op}“ bei „{schluessel}“ braucht einen Text.")
            elif not _zahl(wert):
                fehler.append(f"{ort}: „{op}“ bei „{schluessel}“ braucht eine Zahl.")
        elif not ist_skalar(soll):
            fehler.append(f"{ort}: Wert bei „{schluessel}“ muss Text, Zahl, true/false oder null sein.")
    return fehler


def pruefe_aenderung(aenderung: Any, bekannte: set[str], ort: str) -> list[str]:
    fehler: list[str] = []
    if not isinstance(aenderung, dict) or not aenderung:
        return [f"{ort}: „setze“ muss ein nicht leeres Objekt sein."]
    for schluessel, wert in aenderung.items():
        if schluessel not in bekannte:
            fehler.append(f"{ort}: Schlüssel „{schluessel}“ steht nicht im „zustand“.")
        if isinstance(wert, dict):
            if len(wert) != 1 or next(iter(wert)) not in RECHNUNGEN or not _zahl(next(iter(wert.values()))):
                fehler.append(f"{ort}: Rechnung bei „{schluessel}“ muss {{\"+\": Zahl}} oder {{\"-\": Zahl}} sein.")
        elif not ist_skalar(wert):
            fehler.append(f"{ort}: Wert bei „{schluessel}“ muss Text, Zahl, true/false oder null sein.")
    return fehler


class Zustand:
    """Veränderlicher Zustand einer laufenden Sitzung."""

    def __init__(self, startwerte: dict[str, Any]):
        self.werte: dict[str, Any] = dict(startwerte)

    def __getitem__(self, schluessel: str) -> Any:
        return self.werte[schluessel]

    def get(self, schluessel: str, standard: Any = None) -> Any:
        return self.werte.get(schluessel, standard)

    def erfuellt(self, bedingung: dict[str, Any] | None) -> bool:
        if not bedingung:
            return True
        return bedingung_erfuellt(self.werte, bedingung)

    def setze(self, aenderung: dict[str, Any] | None) -> None:
        if not aenderung:
            return
        for schluessel, wert in aenderung.items():
            if isinstance(wert, dict):
                (op, zahl), = wert.items()
                alt = self.werte.get(schluessel) or 0
                neu = alt + zahl if op == "+" else alt - zahl
                if isinstance(neu, float):
                    neu = round(neu, 6)
                self.werte[schluessel] = neu
            else:
                self.werte[schluessel] = wert

    def fuelle(self, text: str) -> str:
        """Ersetzt {schluessel} durch den Wert aus dem Zustand. Unbekanntes bleibt stehen."""

        def ersetze(treffer: re.Match[str]) -> str:
            schluessel = treffer.group(1)
            if schluessel in self.werte:
                wert = self.werte[schluessel]
                if isinstance(wert, bool):
                    return "True" if wert else "False"
                return "" if wert is None else str(wert)
            return treffer.group(0)

        return _PLATZHALTER.sub(ersetze, text)
