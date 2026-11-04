"""Szenarioauswahl nach der Lernkartei.

* Fällige Karten kommen zuerst dran: Fach 1 (falsch oder nicht gelöst) am häufigsten,
  höhere Fächer seltener. Nie gespielte Szenarien zählen als fällig.
* Ist nichts fällig, kommen Karten aus niedrigen Fächern eher dran als aus hohen.
* Das gerade gespielte Szenario kommt nicht direkt noch einmal.
"""

from __future__ import annotations

import random
from typing import Sequence

from .lernkartei import Lernkartei
from .spielstand import Spielstand
from .szenario import Szenario

GEWICHT_FAELLIG = {1: 8.0, 2: 4.0, 3: 2.5, 4: 1.5, 5: 1.0}
GEWICHT_NEU = 5.0


def gewicht(stand: Spielstand, szenario_id: str, kartei: Lernkartei | None = None) -> float:
    """Gewicht eines Szenarios für die Zufallsauswahl unter den fälligen Karten."""
    kartei = kartei or stand.kartei
    if not stand.gesehen(szenario_id):
        return GEWICHT_NEU
    return GEWICHT_FAELLIG[kartei.szenario(szenario_id)["fach"]]


def faellig(stand: Spielstand, szenario_id: str) -> bool:
    if not stand.gesehen(szenario_id):
        return True
    kartei = stand.kartei
    return kartei.ist_faellig(kartei.szenario(szenario_id))


def waehle(szenarien: Sequence[Szenario], spielstand: Spielstand,
           zuletzt: str | None = None, rng: random.Random | None = None) -> Szenario | None:
    if not szenarien:
        return None
    rng = rng or random.Random()
    kandidaten = [s for s in szenarien if s.id != zuletzt] or list(szenarien)
    kartei = spielstand.kartei
    dran = [s for s in kandidaten if faellig(spielstand, s.id)]
    if dran:
        gewichte = [gewicht(spielstand, s.id, kartei) for s in dran]
        return rng.choices(dran, weights=gewichte, k=1)[0]
    gewichte = [1.0 / kartei.szenario(s.id)["fach"] for s in kandidaten]
    return rng.choices(kandidaten, weights=gewichte, k=1)[0]
