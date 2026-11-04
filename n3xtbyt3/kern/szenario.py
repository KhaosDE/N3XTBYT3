"""Szenarien und allgemeine Befehle laden und prüfen.

Format: ``daten/szenarien/SCHEMA.md``. Jede Datei wird vollständig geprüft;
alle gefundenen Fehler werden gesammelt und mit Dateiname gemeldet.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import pfade
from .befehle import Vergleicher, ist_cmdlet_name, zerlege
from .systeme import REIHENFOLGE, SYSTEME, System
from .zustand import ist_skalar, pruefe_aenderung, pruefe_bedingung

PRUEFSTATUS = ("ungeprueft", "bestaetigt")
AKTIONEN = ("leeren", "exit", "hilfe")  # außerdem "wechsel:<shell>"
_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

PFLICHTFELDER = (
    "id", "system", "titel", "kategorie", "schwierigkeit", "pruefstatus", "quelle",
    "datum", "ausgangslage", "zustand", "befehle", "ziel", "hinweise", "erklaerung",
    "begriffe", "loesung",
)
FREIE_FELDER = ("shell",)


class SzenarioFehler(Exception):
    """Ein Szenario oder eine Befehlsdatei ist fehlerhaft."""

    def __init__(self, datei: Path | str, meldungen: list[str]):
        self.datei = Path(datei)
        self.meldungen = meldungen
        text = "\n".join(f"  - {m}" for m in meldungen)
        super().__init__(f"Fehler in {self.datei}:\n{text}")


@dataclass
class Fall:
    ausgabe: str
    wenn: dict[str, Any] | None = None
    setze: dict[str, Any] | None = None
    fehler: bool = False
    aktion: str | None = None


@dataclass
class Befehl:
    muster: list[str]
    faelle: list[Fall]
    shells: tuple[str, ...]
    namen: frozenset[str]
    falsch: bool = False
    warum: str | None = None
    bedeutung: str | None = None
    vorbereitet: list = field(default_factory=list, repr=False)


@dataclass
class ShellFalle:
    shell: str
    name: str
    meldung: str


@dataclass
class Allgemein:
    """Befehle und Startwerte, die in jedem Szenario eines Systems gelten."""

    system: System
    zustand: dict[str, Any]
    prompt: dict[str, str]
    befehle: list[Befehl]
    shell_fallen: list[ShellFalle]
    datei: Path | None = None


@dataclass
class Szenario:
    id: str
    system: System
    titel: str
    kategorie: str
    schwierigkeit: int
    pruefstatus: str
    quelle: list[str]
    datum: str
    ausgangslage: str
    zustand: dict[str, Any]
    befehle: list[Befehl]
    ziel: list[dict[str, Any]]
    hinweise: list[str]
    erklaerung: str
    begriffe: dict[str, str]
    loesung: list[str]
    shell: str
    datei: Path | None = None
    eigen: bool = False  # liegt im Datenordner des Nutzers

    @property
    def bestaetigt(self) -> bool:
        return self.pruefstatus == "bestaetigt"


# --------------------------------------------------------------------------- Hilfen

def _text(wert: Any) -> str | None:
    """Text oder Liste von Zeilen → Text. Sonst None."""
    if isinstance(wert, str):
        return wert
    if isinstance(wert, list) and all(isinstance(z, str) for z in wert):
        return "\n".join(wert)
    return None


def _lies_json(datei: Path) -> Any:
    try:
        roh = datei.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise SzenarioFehler(datei, [f"Datei lässt sich nicht lesen: {e}"]) from None
    try:
        return json.loads(roh)
    except json.JSONDecodeError as e:
        raise SzenarioFehler(
            datei, [f"Kein gültiges JSON (Zeile {e.lineno}, Spalte {e.colno}): {e.msg}"]
        ) from None


def _standard_shells(system: System, muster: list[str]) -> tuple[str, ...]:
    if "powershell" in system.shell_ids:
        namen = [zerlege(m)[0][0] for m in muster if zerlege(m) and zerlege(m)[0]]
        if any(ist_cmdlet_name(n) for n in namen):
            return ("powershell",)
    return system.shell_ids


def _lies_befehle(roh: Any, system: System, bekannte: set[str], ort: str,
                  fehler: list[str]) -> list[Befehl]:
    if not isinstance(roh, list):
        fehler.append(f"{ort}: muss eine Liste sein.")
        return []
    vergleicher = Vergleicher(system)
    befehle: list[Befehl] = []
    for nr, eintrag in enumerate(roh, start=1):
        stelle = f"{ort}[{nr}]"
        if not isinstance(eintrag, dict):
            fehler.append(f"{stelle}: muss ein Objekt sein.")
            continue
        erlaubt = {"muster", "faelle", "shell", "falsch", "warum", "bedeutung"}
        for k in eintrag:
            if k not in erlaubt and not k.startswith("_"):
                fehler.append(f"{stelle}: unbekanntes Feld „{k}“.")
        muster = eintrag.get("muster")
        if isinstance(muster, str):
            muster = [muster]
        if (not isinstance(muster, list) or not muster
                or not all(isinstance(m, str) and m.strip() for m in muster)):
            fehler.append(f"{stelle}.muster: braucht mindestens eine Befehlszeile (Text).")
            continue
        for m in muster:
            if any(not abschnitt for abschnitt in zerlege(m)):
                fehler.append(f"{stelle}.muster: „{m}“ hat einen leeren Abschnitt (|).")
        shells = eintrag.get("shell")
        if shells is None:
            shells_t = _standard_shells(system, muster)
        else:
            if isinstance(shells, str):
                shells = [shells]
            if not isinstance(shells, list) or not shells or any(s not in system.shell_ids for s in shells):
                fehler.append(
                    f"{stelle}.shell: erlaubt sind {', '.join(system.shell_ids)} (Text oder Liste)."
                )
                shells_t = system.shell_ids
            else:
                shells_t = tuple(shells)
        falsch = eintrag.get("falsch", False)
        if not isinstance(falsch, bool):
            fehler.append(f"{stelle}.falsch: muss true oder false sein.")
            falsch = False
        warum = _text(eintrag["warum"]) if "warum" in eintrag else None
        if "warum" in eintrag and not warum:
            fehler.append(f"{stelle}.warum: muss Text sein.")
        if falsch and not warum:
            fehler.append(f"{stelle}: bei \"falsch\": true bitte „warum“ angeben (Erklärung für Tobi).")
        bedeutung = eintrag.get("bedeutung")
        if bedeutung is not None and (not isinstance(bedeutung, str) or not bedeutung.strip()):
            fehler.append(f"{stelle}.bedeutung: muss Text sein.")
            bedeutung = None
        faelle_roh = eintrag.get("faelle")
        if not isinstance(faelle_roh, list) or not faelle_roh:
            fehler.append(f"{stelle}.faelle: braucht mindestens einen Fall.")
            continue
        faelle: list[Fall] = []
        for fnr, f in enumerate(faelle_roh, start=1):
            fstelle = f"{stelle}.faelle[{fnr}]"
            if not isinstance(f, dict):
                fehler.append(f"{fstelle}: muss ein Objekt sein.")
                continue
            for k in f:
                if k not in {"wenn", "ausgabe", "setze", "fehler", "aktion"} and not k.startswith("_"):
                    fehler.append(f"{fstelle}: unbekanntes Feld „{k}“.")
            ausgabe = _text(f.get("ausgabe", ""))
            if ausgabe is None:
                fehler.append(f"{fstelle}.ausgabe: muss Text oder eine Liste von Zeilen sein.")
                ausgabe = ""
            wenn = f.get("wenn")
            if wenn is not None:
                fehler.extend(pruefe_bedingung(wenn, bekannte, f"{fstelle}.wenn"))
            setze = f.get("setze")
            if setze is not None:
                fehler.extend(pruefe_aenderung(setze, bekannte, f"{fstelle}.setze"))
            ist_fehler = f.get("fehler", False)
            if not isinstance(ist_fehler, bool):
                fehler.append(f"{fstelle}.fehler: muss true oder false sein.")
                ist_fehler = False
            aktion = f.get("aktion")
            if aktion is not None:
                gueltig = isinstance(aktion, str) and (
                    aktion in AKTIONEN
                    or (aktion.startswith("wechsel:") and aktion[8:] in system.shell_ids)
                )
                if not gueltig:
                    fehler.append(
                        f"{fstelle}.aktion: erlaubt sind leeren, exit, hilfe, wechsel:<shell>."
                    )
                    aktion = None
            faelle.append(Fall(ausgabe=ausgabe, wenn=wenn, setze=setze, fehler=ist_fehler, aktion=aktion))
        vorbereitet = [vergleicher.vorbereiten(m) for m in muster]
        namen = frozenset(v[0].name for v in vorbereitet if v)
        befehle.append(Befehl(
            muster=muster, faelle=faelle, shells=shells_t, namen=namen, falsch=falsch,
            warum=warum, bedeutung=bedeutung, vorbereitet=vorbereitet,
        ))
    return befehle


def _pruefe_zustand(roh: Any, ort: str, fehler: list[str]) -> dict[str, Any]:
    if not isinstance(roh, dict):
        fehler.append(f"{ort}: muss ein Objekt sein (Schlüssel und Startwerte).")
        return {}
    for k, v in roh.items():
        if not ist_skalar(v):
            fehler.append(f"{ort}.{k}: Startwert muss Text, Zahl, true/false oder null sein.")
    return dict(roh)


# --------------------------------------------------------------------------- Allgemein

def lade_allgemein(system_id: str, ordner: Path | None = None) -> Allgemein:
    """Lädt die allgemeinen Befehle eines Systems (daten/allgemein/<system>.json)."""
    system = SYSTEME[system_id]
    ordner = ordner or pfade.programmdaten() / "allgemein"
    datei = ordner / f"{system_id}.json"
    if not datei.exists():
        return Allgemein(system=system, zustand={}, prompt={}, befehle=[], shell_fallen=[], datei=None)
    roh = _lies_json(datei)
    fehler: list[str] = []
    if not isinstance(roh, dict):
        raise SzenarioFehler(datei, ["Die Datei muss ein JSON-Objekt enthalten."])
    for k in roh:
        if k not in {"system", "zustand", "prompt", "befehle", "shell_fallen"} and not k.startswith("_"):
            fehler.append(f"unbekanntes Feld „{k}“.")
    if roh.get("system") != system_id:
        fehler.append(f"„system“ muss „{system_id}“ sein.")
    zustand = _pruefe_zustand(roh.get("zustand", {}), "zustand", fehler)
    prompt = roh.get("prompt", {})
    if not isinstance(prompt, dict) or any(
        k not in system.shell_ids or not isinstance(v, str) for k, v in prompt.items()
    ):
        fehler.append(f"„prompt“: Objekt mit Text je Shell ({', '.join(system.shell_ids)}).")
        prompt = {}
    befehle = _lies_befehle(roh.get("befehle", []), system, set(zustand), "befehle", fehler)
    fallen: list[ShellFalle] = []
    for nr, f in enumerate(roh.get("shell_fallen", []), start=1):
        if (not isinstance(f, dict) or f.get("shell") not in system.shell_ids
                or not isinstance(f.get("name"), str) or not _text(f.get("meldung"))):
            fehler.append(f"shell_fallen[{nr}]: braucht shell, name und meldung.")
            continue
        fallen.append(ShellFalle(shell=f["shell"], name=f["name"], meldung=_text(f["meldung"]) or ""))
    if fehler:
        raise SzenarioFehler(datei, fehler)
    return Allgemein(system=system, zustand=zustand, prompt=prompt, befehle=befehle,
                     shell_fallen=fallen, datei=datei)


# --------------------------------------------------------------------------- Szenario

def pruefe_daten(roh: Any, allgemein: Allgemein | None = None,
                 erwartete_id: str | None = None,
                 erwartetes_system: str | None = None) -> tuple[Szenario | None, list[str]]:
    """Prüft ein eingelesenes Szenario. Gibt (Szenario, []) oder (None, Fehler) zurück."""
    fehler: list[str] = []
    if not isinstance(roh, dict):
        return None, ["Die Datei muss ein JSON-Objekt enthalten."]

    fehlend = [f for f in PFLICHTFELDER if f not in roh]
    if fehlend:
        fehler.append("Es fehlen Pflichtfelder: " + ", ".join(fehlend) + ".")
    for k in roh:
        if k not in PFLICHTFELDER and k not in FREIE_FELDER and not k.startswith("_"):
            fehler.append(f"Unbekanntes Feld „{k}“ (Tippfehler? Kommentare mit „_“ beginnen).")

    system_id = roh.get("system")
    if system_id not in SYSTEME:
        fehler.append(f"Unbekanntes System „{system_id}“. Erlaubt sind: {', '.join(REIHENFOLGE)}.")
        return None, fehler
    system = SYSTEME[system_id]
    if erwartetes_system and system_id != erwartetes_system:
        fehler.append(f"„system“ ist „{system_id}“, die Datei liegt aber im Ordner „{erwartetes_system}“.")
    if allgemein is None or allgemein.system.id != system_id:
        allgemein = lade_allgemein(system_id)

    sid = roh.get("id")
    if not isinstance(sid, str) or not _ID.match(sid):
        fehler.append("„id“: nur Kleinbuchstaben, Ziffern und Bindestriche, z. B. „win-dns-cache“.")
    elif erwartete_id and sid != erwartete_id:
        fehler.append(f"„id“ ist „{sid}“, der Dateiname sagt „{erwartete_id}“. Beides muss gleich sein.")

    for feld in ("titel", "kategorie"):
        if feld in roh and (not isinstance(roh[feld], str) or not roh[feld].strip()):
            fehler.append(f"„{feld}“: muss Text sein.")

    schwierigkeit = roh.get("schwierigkeit")
    if "schwierigkeit" in roh and (isinstance(schwierigkeit, bool) or schwierigkeit not in (1, 2, 3)):
        fehler.append("„schwierigkeit“: 1, 2 oder 3.")

    if "pruefstatus" in roh and roh["pruefstatus"] not in PRUEFSTATUS:
        fehler.append("„pruefstatus“: „ungeprueft“ oder „bestaetigt“.")

    quelle = roh.get("quelle")
    if isinstance(quelle, str):
        quelle = [quelle]
    if "quelle" in roh and (
        not isinstance(quelle, list) or not quelle
        or not all(isinstance(q, str) and q.startswith(("https://", "http://")) for q in quelle)
    ):
        fehler.append("„quelle“: eine Adresse (https://…) oder eine Liste davon.")
        quelle = []

    datum = roh.get("datum")
    if "datum" in roh:
        try:
            _dt.date.fromisoformat(datum)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            fehler.append("„datum“: Format JJJJ-MM-TT, z. B. 2026-11-04.")

    ausgangslage = _text(roh.get("ausgangslage"))
    if "ausgangslage" in roh and not ausgangslage:
        fehler.append("„ausgangslage“: Text oder Liste von Zeilen.")
    erklaerung = _text(roh.get("erklaerung"))
    if "erklaerung" in roh and not erklaerung:
        fehler.append("„erklaerung“: Text oder Liste von Zeilen.")

    zustand = _pruefe_zustand(roh.get("zustand", {}), "zustand", fehler)
    bekannte = set(allgemein.zustand) | set(zustand)

    befehle = _lies_befehle(roh.get("befehle", []), system, bekannte, "befehle", fehler)
    if "befehle" in roh and not befehle and not fehler:
        fehler.append("„befehle“: mindestens ein Befehl.")

    ziel = roh.get("ziel")
    if isinstance(ziel, dict):
        ziel = [ziel]
    if "ziel" in roh:
        if not isinstance(ziel, list) or not ziel:
            fehler.append("„ziel“: ein Objekt (oder eine Liste von Objekten, von denen eines reicht).")
            ziel = []
        else:
            for nr, z in enumerate(ziel, start=1):
                fehler.extend(pruefe_bedingung(z, bekannte, f"ziel[{nr}]"))

    hinweise = roh.get("hinweise")
    if "hinweise" in roh and (
        not isinstance(hinweise, list) or len(hinweise) != 3
        or not all(_text(h) for h in hinweise)
    ):
        fehler.append("„hinweise“: genau 3 Texte (Richtung → Werkzeug → fast die Lösung).")
        hinweise = []
    else:
        hinweise = [_text(h) or "" for h in (hinweise or [])]

    begriffe = roh.get("begriffe")
    if "begriffe" in roh and (
        not isinstance(begriffe, dict) or not begriffe
        or not all(isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip()
                   for k, v in begriffe.items())
    ):
        fehler.append("„begriffe“: Objekt „Begriff“: „kurze Erklärung“, mindestens einer.")
        begriffe = {}

    loesung = roh.get("loesung")
    if "loesung" in roh and (
        not isinstance(loesung, list) or not loesung
        or not all(isinstance(s, str) and s.strip() for s in loesung)
    ):
        fehler.append("„loesung“: Liste der Befehle, die das Szenario lösen.")
        loesung = []

    shell = roh.get("shell", system.start_shell)
    if shell not in system.shell_ids:
        fehler.append(f"„shell“: erlaubt sind {', '.join(system.shell_ids)}.")
        shell = system.start_shell

    if fehler:
        return None, fehler
    return Szenario(
        id=sid, system=system, titel=roh["titel"], kategorie=roh["kategorie"],
        schwierigkeit=schwierigkeit, pruefstatus=roh["pruefstatus"], quelle=quelle,
        datum=datum, ausgangslage=ausgangslage or "", zustand=zustand, befehle=befehle,
        ziel=ziel, hinweise=hinweise, erklaerung=erklaerung or "", begriffe=dict(begriffe),
        loesung=list(loesung), shell=shell,
    ), []


def lade_szenario(datei: Path, allgemein: Allgemein | None = None,
                  erwartetes_system: str | None = None, eigen: bool = False) -> Szenario:
    datei = Path(datei)
    roh = _lies_json(datei)
    szenario, fehler = pruefe_daten(roh, allgemein, erwartete_id=datei.stem,
                                    erwartetes_system=erwartetes_system)
    if fehler or szenario is None:
        raise SzenarioFehler(datei, fehler)
    szenario.datei = datei
    szenario.eigen = eigen
    return szenario


@dataclass
class Ladeergebnis:
    szenarien: list[Szenario]
    fehler: list[SzenarioFehler]


def szenario_ordner(system_id: str) -> list[tuple[Path, bool]]:
    """Ordner, aus denen Szenarien eines Systems geladen werden: (Pfad, eigen)."""
    return [
        (pfade.programmdaten() / "szenarien" / system_id, False),
        (pfade.datenordner() / "szenarien" / system_id, True),
    ]


def lade_system(system_id: str, ordner: list[tuple[Path, bool]] | None = None,
                allgemein: Allgemein | None = None) -> Ladeergebnis:
    """Lädt alle Szenarien eines Systems. Fehlerhafte Dateien werden gesammelt, nicht geladen."""
    if system_id not in SYSTEME:
        raise KeyError(f"Unbekanntes System „{system_id}“.")
    allgemein = allgemein or lade_allgemein(system_id)
    ergebnis = Ladeergebnis([], [])
    gesehen: dict[str, Path] = {}
    for pfad, eigen in (ordner if ordner is not None else szenario_ordner(system_id)):
        if not pfad.is_dir():
            continue
        for datei in sorted(pfad.glob("*.json")):
            try:
                s = lade_szenario(datei, allgemein, erwartetes_system=system_id, eigen=eigen)
            except SzenarioFehler as e:
                ergebnis.fehler.append(e)
                continue
            if s.id in gesehen:
                ergebnis.fehler.append(SzenarioFehler(
                    datei, [f"Die id „{s.id}“ gibt es schon in {gesehen[s.id]}."]))
                continue
            gesehen[s.id] = datei
            ergebnis.szenarien.append(s)
    return ergebnis
