"""Befehls-Training: kurze Abfragen „Welcher Befehl …?“ aus den Befehlen der Szenarien.

Jeder Befehl mit ``bedeutung`` wird zu einer Karte. Die Frage ist die Bedeutung plus das
Szenario, aus dem der Befehl stammt. Bewertung der Antwort:

* richtig – passt zu einem Muster des Befehls (wie im Szenario)
* halb    – richtiger Befehlsname, aber andere Parameter
* falsch  – anderer Befehl

Die Karten liegen in der Lernkartei (Fächer 1–5) des Systems.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Sequence

from .befehle import Vergleicher
from .lernkartei import Lernkartei
from .szenario import Befehl, Szenario

GEWICHT = {1: 8.0, 2: 4.0, 3: 2.5, 4: 1.5, 5: 1.0}


@dataclass
class Karte:
    schluessel: str
    bedeutung: str
    beispiel: str
    befehl: Befehl
    szenarien: list[str] = field(default_factory=list)  # Titel

    @property
    def shells(self) -> tuple[str, ...]:
        return self.befehl.shells


def _schluessel(vergleicher: Vergleicher, muster: str) -> str:
    abschnitte = vergleicher.vorbereiten(muster)
    return " | ".join(" ".join(a.woerter) for a in abschnitte)


def sammle_karten(szenarien: Sequence[Szenario]) -> list[Karte]:
    """Alle Befehle mit Bedeutung, ohne „falsche“ Befehle, doppelte zusammengefasst."""
    karten: dict[str, Karte] = {}
    for sz in szenarien:
        vergleicher = Vergleicher(sz.system)
        for b in sz.befehle:
            if not b.bedeutung or b.falsch:
                continue
            schluessel = _schluessel(vergleicher, b.muster[0])
            if schluessel in karten:
                if sz.titel not in karten[schluessel].szenarien:
                    karten[schluessel].szenarien.append(sz.titel)
                continue
            karten[schluessel] = Karte(schluessel, b.bedeutung, b.muster[0], b, [sz.titel])
    return list(karten.values())


def bewerte(karte: Karte, eingabe: str, vergleicher: Vergleicher) -> str:
    eingabe = eingabe.strip()
    if not eingabe:
        return "falsch"
    vorbereitet = vergleicher.vorbereiten(eingabe)
    if any(vergleicher.passt(m, vorbereitet) for m in karte.befehl.vorbereitet):
        return "richtig"
    if vorbereitet and vorbereitet[0].name in karte.befehl.namen:
        return "halb"
    return "falsch"


def waehle_karte(karten: Sequence[Karte], kartei: Lernkartei, zuletzt: str | None = None,
                 rng: random.Random | None = None) -> Karte | None:
    if not karten:
        return None
    rng = rng or random.Random()
    kandidaten = [k for k in karten if k.schluessel != zuletzt] or list(karten)
    faellig = [k for k in kandidaten if kartei.ist_faellig(kartei.befehl(k.schluessel))]
    auswahl = faellig or kandidaten
    gewichte = [GEWICHT[kartei.befehl(k.schluessel)["fach"]] for k in auswahl]
    return rng.choices(auswahl, weights=gewichte, k=1)[0]


def frage_text(karte: Karte) -> str:
    namen = {"powershell": "PowerShell", "cmd": "cmd", "bash": "Bash"}
    shells = " oder ".join(namen.get(s, s) for s in karte.shells)
    herkunft = karte.szenarien[0] if len(karte.szenarien) == 1 else ", ".join(karte.szenarien[:2]) + " …"
    text = karte.befehl.frage or karte.bedeutung
    return f"Welcher Befehl? {text}\n(Shell: {shells} · aus: {herkunft})"
