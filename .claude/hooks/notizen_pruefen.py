#!/usr/bin/env python3
"""Notiz-Prüfung nach dem Standard KhaosDE (Fassung 21.11.2026).

Läuft als Stop-Hook am Ende jeder Antwort von Claude Code. Findet es einen
Verstoß, endet es mit Code 2: Claude Code hält dann nicht an, sondern bekommt
die Meldung und arbeitet weiter. In allen Repositorys von KhaosDE gleich –
nicht einzeln ändern.

Geprüft wird:
1. STAND.md gibt es und sie hat höchstens 150 Zeilen.
2. IDEEN.md gibt es; jede Idee (Überschrift „## …“) hat genau eine Zeile
   „Status: in Klärung“ oder „Status: bereit“ – erledigte Ideen sind gelöscht.
3. Wurde gegenüber origin/main etwas anderes als die Notizen geändert, sind
   auch STAND.md und SITZUNGEN.md geändert.
"""
import json
import os
import re
import subprocess
import sys

GRENZE_STAND = 150
ERLAUBTE_STATUS = ("in Klärung", "bereit")
NOTIZEN = {"STAND.md", "IDEEN.md", "SITZUNGEN.md"}


def lies_zeilen(pfad):
    with open(pfad, encoding="utf-8") as datei:
        return datei.read().splitlines()


def pruefe_stand(wurzel):
    pfad = os.path.join(wurzel, "STAND.md")
    if not os.path.isfile(pfad):
        return ["STAND.md fehlt."]
    anzahl = len(lies_zeilen(pfad))
    if anzahl > GRENZE_STAND:
        return [f"STAND.md hat {anzahl} Zeilen (höchstens {GRENZE_STAND}). Veraltetes "
                "löschen – nur aktueller Zustand, offene Punkte, nächste Schritte."]
    return []


def pruefe_ideen(wurzel):
    pfad = os.path.join(wurzel, "IDEEN.md")
    if not os.path.isfile(pfad):
        return ["IDEEN.md fehlt."]
    fehler = []
    idee, status_zahl, im_codeblock = None, 0, False

    def abschluss():
        if idee is not None and status_zahl != 1:
            fehler.append(f"IDEEN.md, Idee „{idee}“: braucht genau eine Zeile "
                          "„Status: in Klärung“ oder „Status: bereit“.")

    for nummer, zeile in enumerate(lies_zeilen(pfad), 1):
        if zeile.lstrip().startswith("```"):
            im_codeblock = not im_codeblock
            continue
        if im_codeblock:
            continue
        if zeile.startswith("## "):
            abschluss()
            idee, status_zahl = zeile[3:].strip(), 0
            continue
        treffer = re.match(r"^Status:\s*(.*?)\s*$", zeile)
        if treffer:
            status_zahl += 1
            wert = treffer.group(1).rstrip(".")
            if wert not in ERLAUBTE_STATUS:
                fehler.append(f"IDEEN.md, Zeile {nummer}: „Status: {wert}“. Erledigte oder "
                              "verworfene Ideen löschen (erledigt → Zeile in SITZUNGEN.md, "
                              "verworfen → Grund in docs/entscheidungen.md). Erlaubt: "
                              "„in Klärung“, „bereit“.")
    abschluss()
    return fehler


def git(wurzel, *argumente):
    ergebnis = subprocess.run(["git", "-C", wurzel, *argumente],
                              capture_output=True, text=True)
    return ergebnis.returncode, ergebnis.stdout


def geaenderte_dateien(wurzel):
    """Dateien, die sich gegenüber origin/main unterscheiden (eingecheckt oder nicht)."""
    code, basis = git(wurzel, "merge-base", "HEAD", "origin/main")
    if code != 0:
        return None  # kein origin/main bekannt – Prüfung 3 entfällt
    _, geaendert = git(wurzel, "diff", "--name-only", basis.strip())
    _, neu = git(wurzel, "ls-files", "--others", "--exclude-standard")
    return {zeile for zeile in (geaendert + neu).splitlines() if zeile}


def pruefe_protokoll(wurzel):
    dateien = geaenderte_dateien(wurzel)
    if not dateien or not (dateien - NOTIZEN):
        return []
    fehlt = [name for name in ("STAND.md", "SITZUNGEN.md") if name not in dateien]
    if not fehlt:
        return []
    return [f"Arbeit gegenüber main geändert, aber {' und '.join(fehlt)} nicht. Ist die "
            "Aufgabe fertig: STAND.md überschreiben, Zeile in SITZUNGEN.md anhängen, Idee aus "
            "IDEEN.md löschen – im selben Commit. Wartest du nur auf eine Antwort von Tobi, "
            "ist nichts zu tun."]


def main():
    try:
        eingabe = json.load(sys.stdin)
    except (ValueError, OSError):
        eingabe = {}
    if eingabe.get("stop_hook_active"):
        return 0  # nur einmal anhalten, sonst droht eine Schleife
    wurzel = os.environ.get("CLAUDE_PROJECT_DIR") or eingabe.get("cwd") or os.getcwd()
    fehler = pruefe_stand(wurzel) + pruefe_ideen(wurzel) + pruefe_protokoll(wurzel)
    if not fehler:
        return 0
    print("Notiz-Prüfung (Standard KhaosDE):", file=sys.stderr)
    for meldung in fehler:
        print(f"- {meldung}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
