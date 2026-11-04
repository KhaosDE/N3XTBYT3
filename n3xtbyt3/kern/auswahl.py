"""Szenarioauswahl: zufällig, ungelöste und schwache Szenarien kommen öfter dran."""

from __future__ import annotations

import random
from typing import Sequence

from .spielstand import Spielstand
from .szenario import Szenario


def gewicht(eintrag: dict) -> float:
    """Je höher, desto eher kommt das Szenario dran.

    * nie gespielt: 5
    * noch nie gelöst oder letzter Versuch nicht gelöst: 6
    * gelöst: 1, plus 1 je Hinweisstufe und 0,5 je falschem Befehl (höchstens 3) im
      letzten Versuch – wer Hilfe brauchte, übt es bald wieder.
    """
    if eintrag["versuche"] == 0:
        return 5.0
    letzter = eintrag["verlauf"][-1] if eintrag["verlauf"] else {}
    if not eintrag["geloest"] or not letzter.get("geloest", False):
        return 6.0
    schwach = int(letzter.get("hinweise", 0)) + 0.5 * min(int(letzter.get("falsche_befehle", 0)), 3)
    return 1.0 + schwach


def waehle(szenarien: Sequence[Szenario], spielstand: Spielstand,
           zuletzt: str | None = None, rng: random.Random | None = None) -> Szenario | None:
    """Wählt das nächste Szenario. Das gerade gespielte kommt nicht direkt noch einmal."""
    if not szenarien:
        return None
    rng = rng or random.Random()
    kandidaten = [s for s in szenarien if s.id != zuletzt] or list(szenarien)
    gewichte = [gewicht(spielstand.eintrag(s.id)) for s in kandidaten]
    return rng.choices(kandidaten, weights=gewichte, k=1)[0]
