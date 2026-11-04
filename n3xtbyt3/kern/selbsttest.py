"""Selbsttest: Lädt alle Szenarien und spielt ihre Lösungswege durch.

Läuft ohne Fenster, z. B. ``N3XTBYT3.exe --selbsttest`` oder
``python -m n3xtbyt3 --selbsttest``. Damit lässt sich prüfen, ob in der fertigen
Programmdatei alle Szenarien mitgeliefert und lösbar sind.
"""

from __future__ import annotations

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
    return anzahl, fehler


def main() -> int:
    """Führt den Selbsttest aus. Ergebnis: Ausgabe, Datei selbsttest.txt im Datenordner, Exit-Code."""
    anzahl, fehler = pruefe_alle()
    if fehler:
        zeilen = [f"Selbsttest: {len(fehler)} Fehler bei {anzahl} Szenarien"] + [f" - {f}" for f in fehler]
    else:
        zeilen = [f"Selbsttest: {anzahl} Szenarien geladen und gelöst – alles in Ordnung."]
    text = "\n".join(zeilen) + "\n"
    print(text, end="")
    try:
        schreibe_text("selbsttest.txt", text)
    except OSError:
        pass
    return 1 if fehler else 0
