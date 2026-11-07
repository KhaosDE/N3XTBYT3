"""MCP-Server für N3XTBYT3 (Model Context Protocol, über stdin/stdout).

Damit kann Claude Desktop Spielstand und Auswertung lesen und Szenario-Entwürfe anlegen.
* Kein Netzwerk: Die Verbindung läuft nur über stdin/stdout mit dem Programm, das den Server startet.
* Nur lesend – bis auf ein Werkzeug: szenario_entwurf_anlegen schreibt eine neue Datei in den
  Datenordner (immer "pruefstatus": "ungeprueft", überschreibt nie eine vorhandene Datei).
* Der Server tut nichts von sich aus. Er antwortet nur, wenn Claude ein Werkzeug aufruft –
  also wenn Tobi im Chat danach fragt.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, TextIO

from n3xtbyt3.kern import auswertung, pfade
from n3xtbyt3.kern.dateien import schreibe_json
from n3xtbyt3.kern.sitzung import Sitzung
from n3xtbyt3.kern.spielstand import Spielstand
from n3xtbyt3.kern.systeme import REIHENFOLGE, SYSTEME
from n3xtbyt3.kern.szenario import lade_allgemein, lade_system, pruefe_daten

NAME = "n3xtbyt3"
VERSION = "1.0.0"
PROTOKOLLE = ("2025-06-18", "2025-03-26", "2024-11-05")

SYSTEM_PARAM = {
    "type": "object",
    "properties": {"system": {"type": "string", "enum": list(REIHENFOLGE),
                              "description": "windows, windows_server, linux oder linux_server"}},
    "required": ["system"],
}


class WerkzeugFehler(Exception):
    """Fehler, der als Werkzeug-Ergebnis (isError) an Claude zurückgeht."""


def _system(argumente: dict) -> str:
    sid = argumente.get("system")
    if sid not in SYSTEME:
        raise WerkzeugFehler(f"Unbekanntes System „{sid}“. Erlaubt: {', '.join(REIHENFOLGE)}.")
    return sid


def _json(daten: Any) -> str:
    return json.dumps(daten, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------- Werkzeuge

def systeme_uebersicht(argumente: dict) -> str:
    zeilen = ["# N3XTBYT3 – Übersicht", ""]
    for sid in REIHENFOLGE:
        ergebnis = lade_system(sid)
        stand = Spielstand.lade(sid)
        ids = [s.id for s in ergebnis.szenarien]
        versuche = sum(stand.eintrag(i)["versuche"] for i in ids)
        tickets = sum(1 for s in ergebnis.szenarien if s.ticket)
        zeilen.append(f"- {SYSTEME[sid].name} ({sid}): {len(ids)} Szenarien, davon {tickets} Tickets · "
                      f"{stand.anzahl_geloest(ids)} gelöst · {versuche} Versuche"
                      + (f" · {len(ergebnis.fehler)} fehlerhafte Datei(en)" if ergebnis.fehler else ""))
    zeilen += ["", f"Datenordner: {pfade.datenordner()}"]
    return "\n".join(zeilen)


def auswertung_lesen(argumente: dict) -> str:
    sid = _system(argumente)
    daten = auswertung.erstelle(sid, lade_system(sid).szenarien, Spielstand.lade(sid))
    if argumente.get("format") == "json":
        return _json(daten)
    return auswertung.als_markdown(daten)


def spielstand_lesen(argumente: dict) -> str:
    sid = _system(argumente)
    return _json(Spielstand.lade(sid).daten)


def szenarien_auflisten(argumente: dict) -> str:
    sid = _system(argumente)
    ergebnis = lade_system(sid)
    stand = Spielstand.lade(sid)
    liste = []
    for s in sorted(ergebnis.szenarien, key=lambda x: (x.kategorie, x.titel)):
        e = stand.eintrag(s.id)
        liste.append({
            "id": s.id, "titel": s.titel, "kategorie": s.kategorie, "schwierigkeit": s.schwierigkeit,
            "pruefstatus": s.pruefstatus, "eigen": s.eigen, "ticket": bool(s.ticket),
            "versuche": e["versuche"], "geloest": e["geloest"],
            "fach": stand.kartei.szenario(s.id)["fach"] if stand.gesehen(s.id) else None,
        })
    fehler = [str(f) for f in ergebnis.fehler]
    return _json({"system": sid, "szenarien": liste, "fehlerhafte_dateien": fehler})


def _finde_datei(szenario_id: str) -> Path:
    from n3xtbyt3.kern.szenario import _ID
    if not _ID.fullmatch(szenario_id):  # nur echte ids – kein Pfad aus den Szenario-Ordnern heraus
        raise WerkzeugFehler(f"Kein Szenario mit der id „{szenario_id}“ gefunden.")
    for sid in REIHENFOLGE:
        for ordner in (pfade.programmdaten() / "szenarien" / sid, pfade.datenordner() / "szenarien" / sid):
            datei = ordner / f"{szenario_id}.json"
            if datei.is_file():
                return datei
    raise WerkzeugFehler(f"Kein Szenario mit der id „{szenario_id}“ gefunden.")


def szenario_lesen(argumente: dict) -> str:
    sid = argumente.get("id")
    if not isinstance(sid, str) or not sid:
        raise WerkzeugFehler("Bitte „id“ angeben, z. B. win-dns-cache.")
    return _finde_datei(sid).read_text(encoding="utf-8")


def szenario_format(argumente: dict) -> str:
    schema = (pfade.programmdaten() / "szenarien" / "SCHEMA.md").read_text(encoding="utf-8")
    vorlage_datei = pfade.programmordner() / "vorlagen" / "szenario_vorlage.json"
    vorlage = vorlage_datei.read_text(encoding="utf-8") if vorlage_datei.is_file() else "(Vorlage nicht gefunden)"
    return (schema + "\n\n## Vorlage\n\n```json\n" + vorlage + "\n```\n\n"
            "Regeln für Entwürfe: nur erfundene Namen und private IP-Adressen (192.168.x.x, 10.x.x.x); "
            "Ausgaben nur, wenn sie zur offiziellen Doku passen – sonst kürzen oder \"sim\": true; "
            "\"pruefstatus\" ist immer \"ungeprueft\"; \"quelle\" ist eine Adresse der offiziellen Doku.")


def szenario_entwurf_anlegen(argumente: dict) -> str:
    daten = argumente.get("szenario")
    if isinstance(daten, str):
        try:
            daten = json.loads(daten)
        except json.JSONDecodeError as e:
            raise WerkzeugFehler(f"„szenario“ ist kein gültiges JSON: {e}") from None
    if not isinstance(daten, dict):
        raise WerkzeugFehler("„szenario“ muss ein JSON-Objekt sein (Format: Werkzeug szenario_format).")
    daten = dict(daten)
    daten["pruefstatus"] = "ungeprueft"  # Entwürfe von Claude sind immer ungeprüft
    szenario, fehler = pruefe_daten(daten)
    if fehler or szenario is None:
        raise WerkzeugFehler("Der Entwurf ist noch nicht gültig:\n" + "\n".join(f"- {f}" for f in fehler))
    sid, system_id = szenario.id, szenario.system.id
    for vorhanden in (pfade.programmdaten() / "szenarien" / system_id / f"{sid}.json",
                      pfade.datenordner() / "szenarien" / system_id / f"{sid}.json"):
        if vorhanden.exists():
            raise WerkzeugFehler(f"Es gibt schon ein Szenario „{sid}“ ({vorhanden}). Wähle eine andere id.")
    # Lösungsweg prüfen, bevor gespeichert wird
    sitzung = Sitzung(szenario, lade_allgemein(system_id))
    for schritt in szenario.loesung:
        antwort = sitzung.loesungsschritt(schritt)
        if antwort.art != "treffer":
            raise WerkzeugFehler(f"Der Lösungsweg klappt nicht: Schritt „{schritt}“ wird nicht erkannt ({antwort.art}).")
    if not sitzung.geloest:
        raise WerkzeugFehler("Der Lösungsweg erreicht das Ziel nicht. Prüfe „ziel“ und „setze“ in den Befehlen.")
    pfad = schreibe_json(f"szenarien/{system_id}/{sid}.json", daten)
    return (f"Entwurf gespeichert: {pfad}\n"
            f"Er erscheint in N3XTBYT3 unter {SYSTEME[system_id].name} mit den Markierungen „eigen“ und „ungeprüft“. "
            "Tobi prüft ihn und setzt bei Bedarf \"pruefstatus\": \"bestaetigt\".")


WERKZEUGE: dict[str, tuple[str, dict, Callable[[dict], str]]] = {
    "systeme_uebersicht": (
        "Kurzer Überblick über alle vier Systeme: Anzahl Szenarien, gelöst, Versuche. "
        "Nur aufrufen, wenn Tobi nach seinem Lernstand in N3XTBYT3 fragt.",
        {"type": "object", "properties": {}}, systeme_uebersicht),
    "auswertung_lesen": (
        "Auswertung eines Systems: Stärken, Schwächen nach Kategorie und Befehl, häufige Fehler, Empfehlung, "
        "Lernkartei-Fächer. Nur auf Tobis Nachfrage verwenden.",
        {"type": "object", "properties": {**SYSTEM_PARAM["properties"],
                                          "format": {"type": "string", "enum": ["markdown", "json"],
                                                     "description": "markdown (Standard) oder json"}},
         "required": ["system"]}, auswertung_lesen),
    "spielstand_lesen": (
        "Roher Spielstand eines Systems (JSON): Versuche je Szenario mit Hinweisen, falschen und unbekannten Eingaben.",
        SYSTEM_PARAM, spielstand_lesen),
    "szenarien_auflisten": (
        "Alle Szenarien eines Systems mit id, Titel, Kategorie, Prüfstatus und Lernstand; dazu fehlerhafte Dateien.",
        SYSTEM_PARAM, szenarien_auflisten),
    "szenario_lesen": (
        "Die vollständige JSON-Datei eines Szenarios (nach id, z. B. win-dns-cache).",
        {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}, szenario_lesen),
    "szenario_format": (
        "Beschreibung des Szenario-Formats (SCHEMA.md) und die Vorlage. Vor dem Anlegen eines Entwurfs lesen.",
        {"type": "object", "properties": {}}, szenario_format),
    "szenario_entwurf_anlegen": (
        "Legt einen neuen Szenario-Entwurf im Datenordner an (immer ungeprüft, überschreibt nichts). "
        "Prüft Format und Lösungsweg vorher. Nur verwenden, wenn Tobi ausdrücklich ein neues Szenario möchte.",
        {"type": "object", "properties": {"szenario": {"type": "object",
                                                       "description": "Das Szenario als JSON-Objekt (Format siehe szenario_format)"}},
         "required": ["szenario"]}, szenario_entwurf_anlegen),
}


# ---------------------------------------------------------------------- Protokoll

def _antwort(nachricht_id: Any, ergebnis: Any = None, fehler: dict | None = None) -> dict:
    a: dict[str, Any] = {"jsonrpc": "2.0", "id": nachricht_id}
    if fehler is not None:
        a["error"] = fehler
    else:
        a["result"] = ergebnis
    return a


def bearbeite(nachricht: Any) -> dict | None:
    """Bearbeitet eine JSON-RPC-Nachricht. Gibt die Antwort zurück (None bei Benachrichtigungen)."""
    if not isinstance(nachricht, dict) or nachricht.get("jsonrpc") != "2.0" or "method" not in nachricht:
        return _antwort(nachricht.get("id") if isinstance(nachricht, dict) else None,
                        fehler={"code": -32600, "message": "Invalid Request"})
    methode = nachricht["method"]
    nid = nachricht.get("id")
    params = nachricht.get("params") or {}
    if nid is None:  # Benachrichtigung, z. B. notifications/initialized
        return None
    if not isinstance(params, dict):
        return _antwort(nid, fehler={"code": -32602, "message": "Invalid params"})
    if methode == "initialize":
        gewuenscht = params.get("protocolVersion")
        version = gewuenscht if gewuenscht in PROTOKOLLE else PROTOKOLLE[0]
        return _antwort(nid, {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": NAME, "version": VERSION},
            "instructions": ("N3XTBYT3 ist Tobis Lern-Simulator für Systemwartung. Nutze die Werkzeuge nur, wenn Tobi "
                             "im Chat nach seinem Lernstand, seiner Auswertung oder einem neuen Szenario fragt."),
        })
    if methode == "ping":
        return _antwort(nid, {})
    if methode == "tools/list":
        return _antwort(nid, {"tools": [
            {"name": name, "description": beschreibung, "inputSchema": schema}
            for name, (beschreibung, schema, _) in WERKZEUGE.items()
        ]})
    if methode == "tools/call":
        name = params.get("name")
        argumente = params.get("arguments") or {}
        if not isinstance(argumente, dict):
            return _antwort(nid, fehler={"code": -32602, "message": "Invalid params: arguments muss ein Objekt sein"})
        if name not in WERKZEUGE:
            return _antwort(nid, fehler={"code": -32602, "message": f"Unbekanntes Werkzeug: {name}"})
        try:
            text = WERKZEUGE[name][2](argumente)
            return _antwort(nid, {"content": [{"type": "text", "text": text}], "isError": False})
        except WerkzeugFehler as e:
            return _antwort(nid, {"content": [{"type": "text", "text": str(e)}], "isError": True})
        except Exception as e:  # noqa: BLE001 – Fehler sauber an Claude melden statt abzustürzen
            return _antwort(nid, {"content": [{"type": "text", "text": f"Interner Fehler: {type(e).__name__}: {e}"}],
                                  "isError": True})
    return _antwort(nid, fehler={"code": -32601, "message": f"Method not found: {methode}"})


def lauf(eingabe: TextIO = sys.stdin, ausgabe: TextIO = sys.stdout) -> None:
    """Liest Nachrichten zeilenweise (JSON) und schreibt Antworten zeilenweise."""
    for zeile in eingabe:
        zeile = zeile.strip()
        if not zeile:
            continue
        try:
            nachricht = json.loads(zeile)
        except json.JSONDecodeError:
            antwort = _antwort(None, fehler={"code": -32700, "message": "Parse error"})
        else:
            antwort = bearbeite(nachricht)
        if antwort is not None:
            ausgabe.write(json.dumps(antwort, ensure_ascii=False) + "\n")
            ausgabe.flush()


def main() -> None:
    # Ein- und Ausgabe als UTF-8, auch unter Windows
    for strom in (sys.stdin, sys.stdout):
        if hasattr(strom, "reconfigure"):
            strom.reconfigure(encoding="utf-8")
    lauf()
