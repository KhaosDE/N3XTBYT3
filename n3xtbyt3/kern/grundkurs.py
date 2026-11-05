"""Grundkurs: geführte Lektionen „von den Babyschuhen an“.

Eine Lektion liegt als Datei ``daten/grundkurs/<system>/<nr>-<id>.json`` vor (Format:
``daten/grundkurs/SCHEMA.md``). Sie läuft auf derselben Befehlsauswertung wie die Szenarien:
Aus der Lektion wird ein Szenario gebaut und in einer normalen Sitzung gespielt.

Ablauf einer Lektion:

1. **Erklären** – ein kurzer Absatz (steht rechts oben).
2. **Mitmachen** – rechts steht genau, was zu tippen ist; nach jedem Schritt eine Erklärung.
3. **Selbst probieren** – Aufgaben ohne vorgegebenen Befehl, mit drei Hinweisstufen (F1).
4. **Das kannst du jetzt** – Zusammenfassung.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import pfade
from .befehle import Vergleicher
from .sitzung import Antwort, Sitzung
from .systeme import REIHENFOLGE, SYSTEME
from .szenario import Allgemein, Szenario, SzenarioFehler, _fliesstext, _lies_json, _text, lade_allgemein, pruefe_daten
from .zustand import pruefe_bedingung

_DATEINAME = re.compile(r"^(\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.json$")
FELDER = {
    "id", "system", "titel", "pruefstatus", "quelle", "datum", "erklaeren", "begriffe",
    "mitmachen", "aufgaben", "fertig",
    # frei:
    "shell", "zustand", "dateien", "befehle", "rechner", "szenario", "voraussetzung",
}
PFLICHT = ("id", "system", "titel", "pruefstatus", "quelle", "datum", "erklaeren", "begriffe",
           "mitmachen", "aufgaben", "fertig")
FERTIG_SCHLUESSEL = "lektion_fertig"


@dataclass
class Schritt:
    text: str                      # Anleitung (Mitmachen) bzw. Aufgabe (Selbst probieren)
    eingabe: list[str]             # Befehle, die den Schritt erfüllen; der erste ist die Vorgabe
    danach: str                    # Erklärung, nachdem der Schritt geschafft ist
    ziel: dict[str, Any] | None = None   # erfüllt den Schritt ebenfalls (z. B. Ordner gewechselt)
    wenn: dict[str, Any] | None = None   # muss zusätzlich zur Eingabe gelten (z. B. im richtigen Ordner)
    hinweise: list[str] = field(default_factory=list)   # nur Aufgaben: genau 3
    loesung: list[Any] = field(default_factory=list)    # nur Aufgaben (für den Test); Standard: eingabe[0]
    vorbereitet: list = field(default_factory=list, repr=False)


@dataclass
class Lektion:
    id: str
    system_id: str
    nr: int
    titel: str
    erklaeren: str
    begriffe: dict[str, str]
    mitmachen: list[Schritt]
    aufgaben: list[Schritt]
    fertig: list[str]
    quelle: list[str]
    pruefstatus: str
    datum: str
    szenario: Szenario
    voraussetzung: str | None = None
    basis_szenario: str | None = None
    datei: Path | None = None

    @property
    def bestaetigt(self) -> bool:
        return self.pruefstatus == "bestaetigt"

    @property
    def befehle_gelernt(self) -> list[str]:
        """Die Befehle, die in der Lektion vorkommen (Vorgaben aus Mitmachen und Aufgaben)."""
        gesehen: list[str] = []
        for s in [*self.mitmachen, *self.aufgaben]:
            if s.eingabe and s.eingabe[0] not in gesehen:
                gesehen.append(s.eingabe[0])
        return gesehen


@dataclass
class Kursergebnis:
    lektionen: list[Lektion]
    fehler: list[SzenarioFehler]


# --------------------------------------------------------------------------- Laden und prüfen

def kurs_ordner(system_id: str) -> Path:
    return pfade.programmdaten() / "grundkurs" / system_id


def _basis_szenario(system_id: str, szenario_id: str) -> dict[str, Any] | None:
    datei = pfade.programmdaten() / "szenarien" / system_id / f"{szenario_id}.json"
    if not datei.exists():
        return None
    roh = _lies_json(datei)
    return roh if isinstance(roh, dict) else None


def _schritte(roh: Any, ort: str, aufgaben: bool, vergleicher: Vergleicher, bekannte: set[str],
              fehler: list[str]) -> list[Schritt]:
    if not isinstance(roh, list) or not roh:
        fehler.append(f"„{ort}“: Liste mit mindestens einem Schritt.")
        return []
    schritte: list[Schritt] = []
    textfeld = "aufgabe" if aufgaben else "text"
    erlaubt = {textfeld, "eingabe", "danach", "ziel", "wenn"} | ({"hinweise", "loesung"} if aufgaben else set())
    for nr, r in enumerate(roh, start=1):
        stelle = f"{ort}[{nr}]"
        if not isinstance(r, dict):
            fehler.append(f"{stelle}: muss ein Objekt sein.")
            continue
        for k in r:
            if k not in erlaubt and not k.startswith("_"):
                fehler.append(f"{stelle}: unbekanntes Feld „{k}“ (erlaubt: {', '.join(sorted(erlaubt))}).")
        text = _fliesstext(r.get(textfeld))
        if not text:
            fehler.append(f"{stelle}.{textfeld}: Text fehlt.")
        eingabe = r.get("eingabe", [])
        if isinstance(eingabe, str):
            eingabe = [eingabe]
        if not isinstance(eingabe, list) or not all(isinstance(e, str) and e.strip() for e in eingabe):
            fehler.append(f"{stelle}.eingabe: Befehl (Text) oder Liste von Befehlen.")
            eingabe = []
        ziel = r.get("ziel")
        if ziel is not None:
            fehler.extend(pruefe_bedingung(ziel, bekannte, f"{stelle}.ziel"))
        wenn = r.get("wenn")
        if wenn is not None:
            fehler.extend(pruefe_bedingung(wenn, bekannte, f"{stelle}.wenn"))
            if not eingabe:
                fehler.append(f"{stelle}.wenn: gilt zusätzlich zur „eingabe“ – ohne Eingabe bitte „ziel“ nehmen.")
        if not eingabe and ziel is None:
            fehler.append(f"{stelle}: braucht „eingabe“ oder „ziel“ (woran man erkennt, dass er geschafft ist).")
        if not aufgaben and not eingabe:
            fehler.append(f"{stelle}.eingabe: Beim Mitmachen muss feststehen, was getippt wird.")
        danach = _fliesstext(r.get("danach"))
        if not danach:
            fehler.append(f"{stelle}.danach: Erklärung nach dem Schritt fehlt.")
        hinweise: list[str] = []
        loesung: list[Any] = []
        if aufgaben:
            hinweise = r.get("hinweise")
            if not isinstance(hinweise, list) or len(hinweise) != 3 or not all(_text(h) for h in hinweise):
                fehler.append(f"{stelle}.hinweise: genau 3 Texte (Richtung → Werkzeug → fast die Lösung).")
                hinweise = []
            else:
                hinweise = [_text(h) or "" for h in hinweise]
            loesung = r.get("loesung", eingabe[:1])
            if not isinstance(loesung, list) or not loesung or not all(
                    isinstance(x, str) or (isinstance(x, dict) and set(x) <= {"speichern", "inhalt"}) for x in loesung):
                fehler.append(f"{stelle}.loesung: Liste der Befehle, die die Aufgabe lösen.")
                loesung = []
        schritte.append(Schritt(text=text or "", eingabe=list(eingabe), danach=danach or "", ziel=ziel, wenn=wenn,
                                hinweise=hinweise, loesung=list(loesung),
                                vorbereitet=[vergleicher.vorbereiten(e) for e in eingabe]))
    return schritte


def pruefe_lektion(roh: Any, nr: int, allgemein: Allgemein | None = None,
                   erwartete_id: str | None = None,
                   erwartetes_system: str | None = None) -> tuple[Lektion | None, list[str]]:
    fehler: list[str] = []
    if not isinstance(roh, dict):
        return None, ["Die Datei muss ein JSON-Objekt enthalten."]
    fehlend = [f for f in PFLICHT if f not in roh]
    if fehlend:
        fehler.append("Es fehlen Pflichtfelder: " + ", ".join(fehlend) + ".")
    for k in roh:
        if k not in FELDER and not k.startswith("_"):
            fehler.append(f"Unbekanntes Feld „{k}“ (Tippfehler? Kommentare mit „_“ beginnen).")
    system_id = roh.get("system")
    if system_id not in SYSTEME:
        return None, fehler + [f"Unbekanntes System „{system_id}“. Erlaubt sind: {', '.join(REIHENFOLGE)}."]
    if erwartetes_system and system_id != erwartetes_system:
        fehler.append(f"„system“ ist „{system_id}“, die Datei liegt aber im Ordner „{erwartetes_system}“.")
    lid = roh.get("id")
    if erwartete_id and lid != erwartete_id:
        fehler.append(f"„id“ ist „{lid}“, der Dateiname sagt „{erwartete_id}“. Beides muss gleich sein.")
    if allgemein is None or allgemein.system.id != system_id:
        allgemein = lade_allgemein(system_id)

    # Grundlage: ein vorhandenes Szenario (für die geführte Fehlersuche) und/oder eigene Daten
    basis: dict[str, Any] = {}
    basis_id = roh.get("szenario")
    if basis_id is not None:
        basis = _basis_szenario(system_id, basis_id) if isinstance(basis_id, str) else None
        if basis is None:
            fehler.append(f"„szenario“: Es gibt kein Szenario „{basis_id}“ für {SYSTEME[system_id].name}.")
            basis = {}
    eigene_befehle = roh.get("befehle", [])
    if not isinstance(eigene_befehle, list):
        fehler.append("„befehle“: muss eine Liste sein.")
        eigene_befehle = []
    zustand = roh.get("zustand", {})
    if not isinstance(zustand, dict):
        fehler.append("„zustand“: muss ein Objekt sein.")
        zustand = {}
    dateien = roh.get("dateien")
    if dateien is not None and not isinstance(dateien, dict):
        fehler.append("„dateien“: muss ein Objekt sein.")
        dateien = None
    alle_dateien = {**(basis.get("dateien") or {}), **(dateien or {})}
    szenario_roh: dict[str, Any] = {
        "id": lid if isinstance(lid, str) else "lektion",
        "system": system_id,
        "titel": roh.get("titel") or "Lektion",
        "kategorie": "Grundkurs",
        "schwierigkeit": 1,
        "pruefstatus": roh.get("pruefstatus", "ungeprueft"),
        "quelle": roh.get("quelle", []),
        "datum": roh.get("datum", ""),
        "ausgangslage": roh.get("erklaeren") or "-",
        "zustand": {**(basis.get("zustand") or {}), **zustand, FERTIG_SCHLUESSEL: False},
        "befehle": [*eigene_befehle, *(basis.get("befehle") or [])],
        "ziel": {FERTIG_SCHLUESSEL: True},
        "hinweise": ["-", "-", "-"],
        "erklaerung": "-",
        "begriffe": roh.get("begriffe") or {"-": "-"},
        "loesung": ["-"],
    }
    if alle_dateien:
        szenario_roh["dateien"] = alle_dateien
    for feld in ("rechner", "shell"):
        if feld in roh:
            szenario_roh[feld] = roh[feld]
        elif feld in basis:
            szenario_roh[feld] = basis[feld]
    szenario, sz_fehler = pruefe_daten(szenario_roh, allgemein, befehle_pflicht=False)
    fehler.extend(sz_fehler)
    if szenario is None:
        return None, fehler

    erklaeren = _fliesstext(roh.get("erklaeren"))
    if not erklaeren:
        fehler.append("„erklaeren“: ein kurzer Absatz (Text oder Liste von Zeilen).")
    begriffe = roh.get("begriffe")
    if not isinstance(begriffe, dict) or not all(
            isinstance(k, str) and isinstance(v, str) and v.strip() for k, v in begriffe.items()):
        fehler.append("„begriffe“: Objekt „Begriff“: „kurze Erklärung“ (darf leer sein: {}).")
        begriffe = {}
    vergleicher = Vergleicher(szenario.system)
    bekannte = set(allgemein.zustand) | set(szenario.zustand)
    for r in szenario.rechner.values():
        bekannte |= {f"{r.name}:{k}" for k in set(r.allgemein.zustand) | set(r.zustand)}
    mitmachen = _schritte(roh.get("mitmachen"), "mitmachen", False, vergleicher, bekannte, fehler)
    aufgaben = _schritte(roh.get("aufgaben"), "aufgaben", True, vergleicher, bekannte, fehler)
    fertig = roh.get("fertig")
    if isinstance(fertig, str):
        fertig = [fertig]
    if not isinstance(fertig, list) or not fertig or not all(isinstance(f, str) and f.strip() for f in fertig):
        fehler.append("„fertig“: Liste „Das kannst du jetzt“ (mindestens ein Punkt).")
        fertig = []
    voraussetzung = roh.get("voraussetzung")
    if voraussetzung is not None and not isinstance(voraussetzung, str):
        fehler.append("„voraussetzung“: id einer Lektion (Text).")
        voraussetzung = None
    if fehler:
        return None, fehler
    return Lektion(
        id=lid, system_id=system_id, nr=nr, titel=roh["titel"], erklaeren=erklaeren or "",
        begriffe=dict(begriffe), mitmachen=mitmachen, aufgaben=aufgaben, fertig=list(fertig),
        quelle=szenario.quelle, pruefstatus=szenario.pruefstatus, datum=szenario.datum,
        szenario=szenario, voraussetzung=voraussetzung,
        basis_szenario=basis_id if isinstance(basis_id, str) else None,
    ), []


def lade_kurs(system_id: str, ordner: Path | None = None, allgemein: Allgemein | None = None) -> Kursergebnis:
    """Alle Lektionen eines Systems, nach Nummer sortiert. Fehlerhafte Dateien werden gesammelt."""
    ordner = ordner or kurs_ordner(system_id)
    ergebnis = Kursergebnis([], [])
    if not ordner.is_dir():
        return ergebnis
    try:
        allgemein = allgemein or lade_allgemein(system_id)
    except SzenarioFehler as e:
        ergebnis.fehler.append(e)
        return ergebnis
    nummern: dict[int, Path] = {}
    for datei in sorted(ordner.glob("*.json")):
        treffer = _DATEINAME.match(datei.name)
        if not treffer:
            ergebnis.fehler.append(SzenarioFehler(datei, ["Dateiname: <nr>-<id>.json, z. B. 01-gk-win-konsole.json."]))
            continue
        nr, lid = int(treffer.group(1)), treffer.group(2)
        if nr in nummern:
            ergebnis.fehler.append(SzenarioFehler(datei, [f"Die Nummer {nr:02d} hat schon {nummern[nr].name}."]))
            continue
        try:
            roh = _lies_json(datei)
        except SzenarioFehler as e:
            ergebnis.fehler.append(e)
            continue
        lektion, fehler = pruefe_lektion(roh, nr, allgemein, erwartete_id=lid, erwartetes_system=system_id)
        if fehler or lektion is None:
            ergebnis.fehler.append(SzenarioFehler(datei, fehler))
            continue
        lektion.datei = datei
        nummern[nr] = datei
        ergebnis.lektionen.append(lektion)
    ergebnis.lektionen.sort(key=lambda l: l.nr)
    return ergebnis


def alle_kurse() -> dict[str, Kursergebnis]:
    return {sid: lade_kurs(sid) for sid in REIHENFOLGE}


def finde_lektion(kurse: dict[str, Kursergebnis], lektion_id: str) -> Lektion | None:
    for kurs in kurse.values():
        for l in kurs.lektionen:
            if l.id == lektion_id:
                return l
    return None


def lektion_name(lektion: Lektion, system_id: str | None = None) -> str:
    """„Lektion 6“ – mit Systemname, wenn die Lektion zu einem anderen System gehört."""
    if system_id and system_id != lektion.system_id:
        return f"{SYSTEME[lektion.system_id].name}-Lektion {lektion.nr}"
    return f"Lektion {lektion.nr}"


# --------------------------------------------------------------------------- Tippfehler

def tipp(eingabe: str, erwartet: str, vergleicher: Vergleicher) -> str:
    """Freundlicher Hinweis, warum die Eingabe nicht die erwartete war."""
    getippt = eingabe.strip()
    if not getippt:
        return f"Tippe: {erwartet}"
    if re.sub(r"\s+", "", getippt) == re.sub(r"\s+", "", erwartet) or \
            vergleicher.norm(re.sub(r"\s+", "", getippt)) == vergleicher.norm(re.sub(r"\s+", "", erwartet)):
        return (f"Fast! Achte auf die Leerzeichen: Zwischen Befehl und Zusatz steht genau ein Leerzeichen. "
                f"Richtig ist: {erwartet}")
    if not vergleicher.system.gross_klein_egal and getippt.casefold() == erwartet.casefold():
        return f"Fast! Linux unterscheidet Groß- und Kleinschreibung. Richtig ist: {erwartet}"
    if difflib.SequenceMatcher(None, vergleicher.norm(getippt), vergleicher.norm(erwartet)).ratio() >= 0.7:
        return f"Fast! Vergleiche Zeichen für Zeichen – du hast „{getippt}“ getippt. Richtig ist: {erwartet}"
    return f"Das war ein anderer Befehl. Für diesen Schritt tippe: {erwartet}"


# --------------------------------------------------------------------------- Ablauf

@dataclass
class LektionsAntwort:
    antwort: Antwort
    geschafft: bool = False         # der aktuelle Schritt ist erledigt
    tipp: str | None = None         # Tippfehler-Hinweis (Mitmachen)
    erklaerung: str | None = None   # „danach“ des erledigten Schritts
    teil_neu: str | None = None     # "aufgaben" oder "fertig", wenn ein neuer Teil beginnt


class Lektionslauf:
    """Eine Lektion wird gespielt: Mitmachen → Selbst probieren → Fertig."""

    def __init__(self, lektion: Lektion, allgemein: Allgemein):
        self.lektion = lektion
        self.sitzung = Sitzung(lektion.szenario, allgemein)
        self.teil = "mitmachen" if lektion.mitmachen else ("aufgaben" if lektion.aufgaben else "fertig")
        self.index = 0
        self.hinweis_stufe = 0          # der aktuellen Aufgabe
        self.hinweise_gesamt = 0
        self.erledigt: list[tuple[Schritt, str]] = []   # (Schritt, Erklärung) in der Reihenfolge
        self.letzter_tipp: str | None = None

    @property
    def schritte(self) -> list[Schritt]:
        return self.lektion.mitmachen if self.teil == "mitmachen" else self.lektion.aufgaben

    @property
    def schritt(self) -> Schritt | None:
        if self.teil == "fertig":
            return None
        return self.schritte[self.index]

    @property
    def fertig(self) -> bool:
        return self.teil == "fertig"

    def _passt(self, schritt: Schritt, text: str) -> bool:
        vorbereitet = self.sitzung.vergleicher.vorbereiten(text)
        return any(self.sitzung.vergleicher.passt(m, vorbereitet) for m in schritt.vorbereitet)

    def _geschafft(self, schritt: Schritt, text: str, antwort: Antwort) -> bool:
        # Richtig getippt zählt nur, wenn der Befehl hier auch lief (nicht z. B. in der falschen Shell).
        if antwort.art == "treffer" and self._passt(schritt, text) and (
                schritt.wenn is None or self.sitzung._erfuellt(schritt.wenn, self.sitzung.haupt)):
            return True
        return schritt.ziel is not None and self.sitzung._erfuellt(schritt.ziel, self.sitzung.haupt)

    def _weiter(self) -> str | None:
        """Zum nächsten Schritt. Gibt den neuen Teil zurück, wenn einer beginnt."""
        self.index += 1
        self.hinweis_stufe = 0
        self.letzter_tipp = None
        if self.index < len(self.schritte):
            return None
        self.index = 0
        if self.teil == "mitmachen" and self.lektion.aufgaben:
            self.teil = "aufgaben"
        else:
            self.teil = "fertig"
        return self.teil

    def eingabe(self, text: str) -> LektionsAntwort:
        antwort = self.sitzung.eingabe(text)
        schritt = self.schritt
        if schritt is None or not text.strip():
            return LektionsAntwort(antwort)
        if self._geschafft(schritt, text, antwort):
            self.erledigt.append((schritt, schritt.danach))
            neu = self._weiter()
            return LektionsAntwort(antwort, geschafft=True, erklaerung=schritt.danach, teil_neu=neu)
        hinweis = None
        if self._passt(schritt, text) and antwort.art != "treffer":
            hinweis = "Richtig getippt – aber so geht es hier nicht. Lies die blaue Meldung im Terminal."
        elif self._passt(schritt, text) and schritt.wenn is not None:
            hinweis = "Der Befehl stimmt – aber noch nicht am richtigen Ort. Lies die Aufgabe noch einmal genau."
        elif self.teil == "mitmachen":
            hinweis = tipp(text, schritt.eingabe[0], self.sitzung.vergleicher)
        self.letzter_tipp = hinweis
        return LektionsAntwort(antwort, tipp=hinweis)

    def datei_speichern(self, pfad: str, inhalt: str) -> LektionsAntwort:
        antwort = self.sitzung.datei_speichern(pfad, inhalt)
        schritt = self.schritt
        if schritt is not None and schritt.ziel is not None and self.sitzung._erfuellt(schritt.ziel, self.sitzung.haupt):
            self.erledigt.append((schritt, schritt.danach))
            neu = self._weiter()
            return LektionsAntwort(antwort, geschafft=True, erklaerung=schritt.danach, teil_neu=neu)
        return LektionsAntwort(antwort)

    def loesungsschritt(self, schritt: Any) -> LektionsAntwort:
        if isinstance(schritt, dict):
            return self.datei_speichern(self.sitzung.fs.absolut(schritt["speichern"]), schritt["inhalt"])
        return self.eingabe(schritt)

    def naechster_hinweis(self) -> str | None:
        """Mitmachen: die Vorgabe noch einmal. Aufgaben: nächste von drei Hinweisstufen."""
        schritt = self.schritt
        if schritt is None:
            return None
        if self.teil == "mitmachen":
            return f"Tippe genau: {schritt.eingabe[0]}"
        if self.hinweis_stufe >= len(schritt.hinweise):
            return None
        self.hinweis_stufe += 1
        self.hinweise_gesamt += 1
        return schritt.hinweise[self.hinweis_stufe - 1]

    @property
    def gezeigte_hinweise(self) -> list[str]:
        schritt = self.schritt
        if schritt is None or self.teil != "aufgaben":
            return []
        return schritt.hinweise[: self.hinweis_stufe]

    def ergebnis(self) -> dict[str, Any]:
        return {
            "datum": self.sitzung.begonnen.isoformat(),
            "fertig": self.fertig,
            "hinweise": self.hinweise_gesamt,
            "befehle": self.sitzung.anzahl_befehle,
            "sekunden": self.sitzung.sekunden(),
        }


# --------------------------------------------------------------------------- Fortschritt

def fortschritt(stand, lektionen: list[Lektion]) -> tuple[int, Lektion | None]:
    """(Anzahl fertiger Lektionen, nächste offene Lektion oder None)."""
    fertig = [l for l in lektionen if stand.lektion(l.id)["fertig"]]
    offen = next((l for l in lektionen if not stand.lektion(l.id)["fertig"]), None)
    return len(fertig), offen

