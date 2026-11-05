"""Befehls-Training: kurze Abfragen „Welcher Befehl …?“ aus den Befehlen der Szenarien.

Jeder Befehl mit ``bedeutung`` wird zu einer Karte. Die Frage ist die Bedeutung plus das
Szenario, aus dem der Befehl stammt. Dazu kommen die Befehle aus dem Befehlsbuch, sobald ihre
Lektion im Grundkurs geschafft ist. Bewertung der Antwort:

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
from .szenario import Befehl, Szenario, _lies_befehle

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


def sammle_karten(szenarien: Sequence[Szenario], buch=None, stand=None, lektionen=None) -> list[Karte]:
    """Alle Befehle mit Bedeutung, ohne „falsche“ Befehle, doppelte zusammengefasst.

    Mit ``buch`` (Befehlsbuch) und ``stand`` (Spielstand) kommen die Befehle der geschafften
    Lektionen dazu; ``lektionen`` liefert dafür Nummer und Titel.
    """
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
    if buch is not None and stand is not None:
        from .systeme import SYSTEME
        system = SYSTEME[buch.system_id]
        vergleicher = Vergleicher(system)
        namen = {l.id: f"Grundkurs, Lektion {l.nr}" for l in (lektionen or [])}
        for e in buch.eintraege:
            if not stand.lektion(e.lektion)["fertig"]:
                continue
            herkunft = namen.get(e.lektion, "Grundkurs")
            schluessel = _schluessel(vergleicher, e.beispiel)
            if schluessel in karten:
                if herkunft not in karten[schluessel].szenarien:
                    karten[schluessel].szenarien.append(herkunft)
                continue
            fehler: list[str] = []
            roh = {"muster": e.muster, "faelle": [{"ausgabe": ""}], "bedeutung": e.was}
            if e.frage:
                roh["frage"] = e.frage
            befehl = _lies_befehle([roh], system, set(), "befehlsbuch", fehler)
            if befehl and not fehler:
                karten[schluessel] = Karte(schluessel, e.was, e.beispiel, befehl[0], [herkunft])
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
