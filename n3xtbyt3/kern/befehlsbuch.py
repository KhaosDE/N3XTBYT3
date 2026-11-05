"""Befehlsbuch und Lexikon – zum Nachschlagen, aus den Daten erzeugt.

* **Befehlsbuch** je System: ``daten/befehlsbuch/<system>.json`` mit Einträgen (Befehl, was er tut,
  Beispiel, wichtige Parameter, „Wann brauche ich das?“, Quelle) und der Sicht „Was tippe ich,
  wenn …?“ (Situationen). Jeder Eintrag nennt die Lektion, in der der Befehl vorkommt; ein Test
  prüft, dass jedes Beispiel dort in der Simulation funktioniert.
* **Lexikon** je System: alle Begriffe aus Lektionen und Szenarien, alphabetisch, mit Fundstellen.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from . import pfade
from .grundkurs import Lektion
from .szenario import Szenario, _fliesstext, _text

EINTRAG_FELDER = {"befehl", "was", "beispiel", "auch", "parameter", "wann", "lektion", "quelle", "vorher", "frage"}
SITUATION_FELDER = {"wenn", "befehle", "lektion", "vorher", "erklaerung"}


@dataclass
class Eintrag:
    befehl: str
    was: str
    beispiel: str
    wann: str
    lektion: str
    quelle: list[str]
    auch: list[str] = field(default_factory=list)       # weitere richtige Schreibweisen (z. B. Alias)
    parameter: dict[str, str] = field(default_factory=dict)
    vorher: list[str] = field(default_factory=list)     # nur für den Test: Befehle vor dem Beispiel
    frage: str | None = None                            # Frage im Befehls-Training (sonst „was“)

    @property
    def muster(self) -> list[str]:
        return [self.beispiel, *self.auch]


@dataclass
class Situation:
    wenn: str                 # „… ein Programm nicht mehr reagiert?“
    befehle: list[str]
    lektion: str
    erklaerung: str = ""
    vorher: list[str] = field(default_factory=list)


@dataclass
class Befehlsbuch:
    system_id: str
    eintraege: list[Eintrag]
    situationen: list[Situation]
    fehler: list[str]
    datei: Path | None = None


def datei(system_id: str) -> Path:
    return pfade.programmdaten() / "befehlsbuch" / f"{system_id}.json"


def _liste(wert: Any) -> list[str] | None:
    if isinstance(wert, str):
        return [wert]
    if isinstance(wert, list) and all(isinstance(x, str) and x.strip() for x in wert):
        return list(wert)
    return None


def pruefe(roh: Any, system_id: str) -> Befehlsbuch:
    fehler: list[str] = []
    buch = Befehlsbuch(system_id, [], [], fehler)
    if not isinstance(roh, dict):
        fehler.append("Die Datei muss ein JSON-Objekt enthalten.")
        return buch
    if roh.get("system") != system_id:
        fehler.append(f"„system“ muss „{system_id}“ sein.")
    for nr, e in enumerate(roh.get("befehle", []), start=1):
        ort = f"befehle[{nr}]"
        if not isinstance(e, dict):
            fehler.append(f"{ort}: muss ein Objekt sein.")
            continue
        for k in e:
            if k not in EINTRAG_FELDER and not k.startswith("_"):
                fehler.append(f"{ort}: unbekanntes Feld „{k}“.")
        fehlend = [k for k in ("befehl", "was", "beispiel", "wann", "lektion", "quelle") if not e.get(k)]
        if fehlend:
            fehler.append(f"{ort}: es fehlt {', '.join(fehlend)}.")
            continue
        quelle = _liste(e["quelle"])
        if not quelle or not all(q.startswith("https://") for q in quelle):
            fehler.append(f"{ort}.quelle: Adresse(n) der offiziellen Doku (https://…).")
            quelle = []
        parameter = e.get("parameter", {})
        if not isinstance(parameter, dict) or not all(isinstance(v, str) for v in parameter.values()):
            fehler.append(f"{ort}.parameter: Objekt „-Parameter“: „was er tut“.")
            parameter = {}
        auch = _liste(e.get("auch", [])) if e.get("auch") else []
        vorher = _liste(e.get("vorher", [])) if e.get("vorher") else []
        if auch is None or vorher is None:
            fehler.append(f"{ort}: „auch“ und „vorher“ sind Listen von Befehlen.")
        buch.eintraege.append(Eintrag(
            befehl=e["befehl"], was=_fliesstext(e["was"]) or "", beispiel=e["beispiel"],
            wann=_fliesstext(e["wann"]) or "", lektion=e["lektion"], quelle=quelle, auch=auch or [],
            parameter=dict(parameter), vorher=vorher or [], frage=e.get("frage")))
    for nr, s in enumerate(roh.get("situationen", []), start=1):
        ort = f"situationen[{nr}]"
        if not isinstance(s, dict):
            fehler.append(f"{ort}: muss ein Objekt sein.")
            continue
        for k in s:
            if k not in SITUATION_FELDER and not k.startswith("_"):
                fehler.append(f"{ort}: unbekanntes Feld „{k}“.")
        befehle = _liste(s.get("befehle"))
        if not s.get("wenn") or not befehle or not s.get("lektion"):
            fehler.append(f"{ort}: braucht „wenn“, „befehle“ und „lektion“.")
            continue
        buch.situationen.append(Situation(
            wenn=_text(s["wenn"]) or "", befehle=befehle, lektion=s["lektion"],
            erklaerung=_fliesstext(s.get("erklaerung", "")) or "", vorher=_liste(s.get("vorher", [])) or []))
    buch.eintraege.sort(key=lambda e: e.befehl.casefold())
    return buch


def lade(system_id: str, pfad: Path | None = None) -> Befehlsbuch:
    pfad = pfad or datei(system_id)
    if not pfad.exists():
        return Befehlsbuch(system_id, [], [], [])
    try:
        roh = json.loads(pfad.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as e:
        return Befehlsbuch(system_id, [], [], [f"{pfad.name} lässt sich nicht lesen: {e}"])
    buch = pruefe(roh, system_id)
    buch.datei = pfad
    return buch


def _passt(text: str, suche: str) -> bool:
    return suche.casefold() in text.casefold()


def suche_eintraege(buch: Befehlsbuch, text: str) -> list[Eintrag]:
    text = text.strip()
    if not text:
        return list(buch.eintraege)
    return [e for e in buch.eintraege
            if _passt(e.befehl, text) or _passt(e.was, text) or _passt(e.wann, text)
            or any(_passt(a, text) for a in e.auch) or _passt(e.beispiel, text)]


def suche_situationen(buch: Befehlsbuch, text: str) -> list[Situation]:
    text = text.strip()
    if not text:
        return list(buch.situationen)
    return [s for s in buch.situationen
            if _passt(s.wenn, text) or any(_passt(b, text) for b in s.befehle) or _passt(s.erklaerung, text)]


# --------------------------------------------------------------------------- Lexikon

@dataclass
class Begriff:
    name: str
    erklaerung: str
    vorkommen: list[str] = field(default_factory=list)


def lexikon(lektionen: Sequence[Lektion], szenarien: Sequence[Szenario]) -> list[Begriff]:
    """Alle Begriffe aus Lektionen (zuerst) und Szenarien, alphabetisch. Gleiche Namen werden
    zusammengefasst; die erste Erklärung gilt, alle Fundstellen werden gesammelt."""
    nach_name: dict[str, Begriff] = {}

    def dazu(name: str, erklaerung: str, ort: str) -> None:
        schluessel = name.strip().casefold()
        if not schluessel or erklaerung.strip() in ("", "-"):
            return
        b = nach_name.get(schluessel)
        if b is None:
            b = nach_name[schluessel] = Begriff(name.strip(), erklaerung.strip())
        if ort not in b.vorkommen:
            b.vorkommen.append(ort)

    for l in lektionen:
        for name, erklaerung in l.begriffe.items():
            dazu(name, erklaerung, f"Grundkurs, Lektion {l.nr}: {l.titel}")
    for sz in sorted(szenarien, key=lambda s: s.titel):
        for name, erklaerung in sz.begriffe.items():
            dazu(name, erklaerung, f"Szenario: {sz.titel}")
    return sorted(nach_name.values(), key=lambda b: b.name.casefold())


def suche_begriffe(begriffe: Sequence[Begriff], text: str) -> list[Begriff]:
    text = text.strip()
    if not text:
        return list(begriffe)
    # Treffer im Namen zuerst, dann in der Erklärung
    im_namen = [b for b in begriffe if _passt(b.name, text)]
    sonst = [b for b in begriffe if b not in im_namen and _passt(b.erklaerung, text)]
    return im_namen + sonst
