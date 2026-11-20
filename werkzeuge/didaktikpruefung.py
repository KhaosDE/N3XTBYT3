"""Didaktikprüfung: Ist alles, was eine Aufgabe verlangt, vorher erklärt worden?

Prüft Grundkurs und Szenarien. „Erklärt“ heißt: Befehl bzw. Zusatz (Option, Schalter) steht vorher in
einem erklärenden Text (Erklären-Absatz, Begriffe, Erklärung nach einem Mitmach-Schritt oder nach einer
früheren Aufgabe). Hinweise (F1) und die Erklärung nach der eigenen Aufgabe zählen nicht.
"""
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("N3XTBYT3_DATEN", tempfile.mkdtemp())

from n3xtbyt3.kern import grundkurs as gk  # noqa: E402
from n3xtbyt3.kern.szenario import lade_allgemein, lade_system  # noqa: E402

SYSTEME = ["windows", "windows_server", "linux", "linux_server"]
VORAUSGESETZT = {"linux_server": "linux", "windows_server": "windows"}
KURZE_ERKLAERUNG = 40
SCHALTER_WIN = re.compile(r"^/[A-Za-z?]{1,3}$")
SCHALTER = re.compile(r"^--?[A-Za-z][\w-]*")


def teile(befehl, windows):
    """Befehlsnamen und Zusätze eines Befehls (über Pipes hinweg)."""
    namen, zusaetze = set(), set()
    for stueck in befehl.split("|"):
        woerter = stueck.strip().split()
        while woerter and woerter[0] == "sudo":
            woerter = woerter[1:]
        if not woerter:
            continue
        name = woerter[0].lower()
        namen.add(name[:-4] if name.endswith(".exe") else name)
        for wort in woerter[1:]:
            treffer = SCHALTER.match(wort)
            if treffer:
                zusaetze.add(treffer.group(0).split("=")[0].lower())
            elif windows and SCHALTER_WIN.match(wort):
                zusaetze.add(wort.lower())
    return namen, zusaetze


def text(wert):
    if isinstance(wert, list):
        return " ".join(str(x) for x in wert)
    if isinstance(wert, dict):
        return " ".join(f"{k} {v}" for k, v in wert.items())
    return str(wert or "")


def kommt_vor(wort, wissen):
    muster = r"(?<![\w-])" + re.escape(wort) + r"(?![\w-])"
    return re.search(muster, wissen, re.IGNORECASE) is not None


def fehlend(befehle, wissen, windows):
    luecken = []
    for befehl in befehle:
        if not isinstance(befehl, str):
            continue
        namen, zusaetze = teile(befehl, windows)
        luecken += [n for n in sorted(namen) if not kommt_vor(n, wissen)]
        luecken += [z for z in sorted(zusaetze) if not kommt_vor(z, wissen)]
    return sorted(set(luecken))


def pruefe_grundkurs():
    befunde = []
    kurse = {sid: gk.lade_kurs(sid, allgemein=lade_allgemein(sid)).lektionen for sid in SYSTEME}
    wissen_je_system = {}
    for sid in SYSTEME:
        windows = sid.startswith("windows")
        wissen = wissen_je_system.get(VORAUSGESETZT.get(sid), "")
        for lektion in kurse[sid]:
            wissen += " " + text(lektion.erklaeren) + " " + text(lektion.begriffe)
            for nr, schritt in enumerate(lektion.mitmachen, 1):
                danach = text(schritt.danach)
                if len(danach) < KURZE_ERKLAERUNG:
                    befunde.append((lektion.id, f"Mitmachen {nr}", "Erklärung danach fehlt/zu knapp", danach))
                luecken = fehlend(schritt.eingabe[:1], wissen + " " + danach, windows)
                if luecken:
                    befunde.append((lektion.id, f"Mitmachen {nr}", "Befehl/Zusatz nirgends erklärt",
                                    ", ".join(luecken)))
                wissen += " " + danach
            for nr, aufgabe in enumerate(lektion.aufgaben, 1):
                loesung = aufgabe.loesung or aufgabe.eingabe[:1]
                luecken = fehlend(loesung, wissen, windows)
                if luecken:
                    befunde.append((lektion.id, f"Aufgabe {nr}", "vorher nicht erklärt", ", ".join(luecken)))
                danach = text(aufgabe.danach)
                if len(danach) < KURZE_ERKLAERUNG:
                    befunde.append((lektion.id, f"Aufgabe {nr}", "Erklärung danach fehlt/zu knapp", danach))
                wissen += " " + danach
        wissen_je_system[sid] = wissen
    return befunde, wissen_je_system


def pruefe_szenarien(wissen_je_system):
    befunde = []
    for sid in SYSTEME:
        windows = sid.startswith("windows")
        for szenario in lade_system(sid, allgemein=lade_allgemein(sid)).szenarien:
            erklaerung = text(szenario.erklaerung)
            if len(erklaerung) < KURZE_ERKLAERUNG:
                befunde.append((szenario.id, "Szenario", "Erklärung fehlt/zu knapp", erklaerung))
            wissen = wissen_je_system[sid] + " " + erklaerung + " " + text(szenario.begriffe)
            luecken = fehlend(szenario.loesung, wissen, windows)
            if luecken:
                befunde.append((szenario.id, "Szenario", "weder im Grundkurs noch im Szenario erklärt",
                                ", ".join(luecken)))
    return befunde


if __name__ == "__main__":
    grundkurs, wissen = pruefe_grundkurs()
    szenarien = pruefe_szenarien(wissen)
    for titel, liste in (("GRUNDKURS", grundkurs), ("SZENARIEN", szenarien)):
        print(f"\n===== {titel}: {len(liste)} Befunde")
        for ort, wo, art, inhalt in liste:
            print(f"{ort:26} {wo:12} {art}: {inhalt[:90]}")
