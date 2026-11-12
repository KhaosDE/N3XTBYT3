"""Didaktikprüfung des Grundkurses: Verlangt eine Aufgabe einen Befehl, der vorher nie vorgeführt wurde?

Ein Befehl gilt als vorgeführt, wenn er im Mitmachen-Teil dieser oder einer früheren Lektion
vorkommt oder im vorausgesetzten Kurs (Linux vor Linux Server, Windows vor Windows Server).
Aufruf im Projektordner: python werkzeuge/didaktikpruefung.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("N3XTBYT3_DATEN", tempfile.mkdtemp())

from n3xtbyt3.kern import grundkurs as gk  # noqa: E402
from n3xtbyt3.kern.szenario import lade_allgemein  # noqa: E402

VORAUSGESETZT = {"linux_server": "linux", "windows_server": "windows"}


def befehlsname(text):
    woerter = text.strip().split()
    i = 0
    while i < len(woerter) and woerter[i] == "sudo":
        i += 1
    if i >= len(woerter):
        return None
    name = woerter[i].lower()
    return name[:-4] if name.endswith(".exe") else name


def namen(befehle):
    ergebnis = set()
    for befehl in befehle:
        if isinstance(befehl, str):
            for teil in befehl.split("|"):
                name = befehlsname(teil)
                if name:
                    ergebnis.add(name)
    return ergebnis


def vorgefuehrt(lektion):
    ergebnis = set()
    for schritt in lektion.mitmachen:
        ergebnis |= namen(schritt.eingabe)
    return ergebnis


def luecken():
    kurse = {sid: gk.lade_kurs(sid, allgemein=lade_allgemein(sid)).lektionen
             for sid in ["windows", "windows_server", "linux", "linux_server"]}
    gefunden = []
    for sid, lektionen in kurse.items():
        bekannt = set()
        for lektion in kurse.get(VORAUSGESETZT.get(sid), []):
            bekannt |= vorgefuehrt(lektion)
        for lektion in lektionen:
            bekannt |= vorgefuehrt(lektion)
            for nr, aufgabe in enumerate(lektion.aufgaben, 1):
                loesung = aufgabe.loesung or aufgabe.eingabe
                verlangt = namen(aufgabe.eingabe) | namen(loesung)
                if verlangt and not (verlangt & bekannt):
                    gefunden.append((lektion.id, nr, sorted(verlangt), aufgabe.text))
    return gefunden


if __name__ == "__main__":
    liste = luecken()
    for lektion_id, nr, verlangt, text in liste:
        print(f"{lektion_id:22} Aufgabe {nr}: {verlangt}  –  {text[:90]}")
    print(f"\nLücken gesamt: {len(liste)}")
