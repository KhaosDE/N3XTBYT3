"""Selbsttest: Lädt alle Szenarien und Lektionen und spielt ihre Lösungswege durch.

Läuft ohne Fenster, z. B. ``N3XTBYT3.exe --selbsttest`` oder
``python -m n3xtbyt3 --selbsttest``. Damit lässt sich prüfen, ob in der fertigen
Programmdatei alle Szenarien mitgeliefert und lösbar sind.
"""

from __future__ import annotations

from . import grundkurs
from .dateien import schreibe_text
from .sitzung import Sitzung
from .systeme import REIHENFOLGE
from .szenario import SzenarioFehler, lade_allgemein, lade_system


def pruefe_alle() -> tuple[int, list[str]]:
    """Gibt (Anzahl geprüfter Szenarien, Fehlermeldungen) zurück."""
    fehler: list[str] = []
    anzahl = 0
    for system_id in REIHENFOLGE:
        try:
            allgemein = lade_allgemein(system_id)
        except SzenarioFehler as e:
            fehler.append(str(e))
            continue
        ergebnis = lade_system(system_id, allgemein=allgemein)
        fehler.extend(str(f) for f in ergebnis.fehler)
        for szenario in ergebnis.szenarien:
            anzahl += 1
            sitzung = Sitzung(szenario, allgemein)
            for schritt in szenario.loesung:
                antwort = sitzung.loesungsschritt(schritt)
                if antwort.art != "treffer":
                    fehler.append(f"{szenario.id}: Lösungsschritt „{schritt}“ nicht erkannt ({antwort.art}).")
                    break
            if not sitzung.geloest:
                fehler.append(f"{szenario.id}: Nach dem Lösungsweg nicht gelöst.")
        kurs = grundkurs.lade_kurs(system_id, allgemein=allgemein)
        fehler.extend(str(f) for f in kurs.fehler)
        for lektion in kurs.lektionen:
            anzahl += 1
            fehler.extend(pruefe_lektion(lektion, allgemein))
    return anzahl, fehler


def pruefe_lektion(lektion: grundkurs.Lektion, allgemein) -> list[str]:
    """Spielt eine Lektion mit Vorgaben und Lösungen durch. Gibt Fehlermeldungen zurück."""
    lauf = grundkurs.Lektionslauf(lektion, allgemein)
    for schritt in [s.eingabe[0] for s in lektion.mitmachen] + [x for a in lektion.aufgaben for x in a.loesung]:
        antwort = lauf.loesungsschritt(schritt)
        if antwort.antwort.art != "treffer":
            return [f"{lektion.id}: Schritt „{schritt}“ nicht erkannt ({antwort.antwort.art})."]
    return [] if lauf.fertig else [f"{lektion.id}: Nach allen Schritten nicht fertig."]


def main() -> int:
    """Führt den Selbsttest aus. Ergebnis: Ausgabe, Datei selbsttest.txt im Datenordner, Exit-Code."""
    anzahl, fehler = pruefe_alle()
    if fehler:
        zeilen = [f"Selbsttest: {len(fehler)} Fehler bei {anzahl} Szenarien und Lektionen"] + [f" - {f}" for f in fehler]
    else:
        zeilen = [f"Selbsttest: {anzahl} Szenarien und Lektionen geladen und gelöst – alles in Ordnung."]
    text = "\n".join(zeilen) + "\n"
    print(text, end="")
    try:
        schreibe_text("selbsttest.txt", text)
    except OSError:
        pass
    return 1 if fehler else 0
