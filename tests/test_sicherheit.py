"""Sicherheitstest: N3XTBYT3 ist eine reine Simulation.

In den Paketen n3xtbyt3 und n3xtbyt3_mcp dürfen keine Werkzeuge vorkommen, mit denen echte Befehle
ausgeführt oder Netzwerkverbindungen aufgebaut werden.

Einzige Ausnahme (Entscheidung Tobi, 05.11.2026): das Selbst-Update im eigenen Paket n3xtbyt3_update.
Es darf nur die Releases dieses Repositorys abfragen – das prüft tests/test_update.py.
"""

import re
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
PAKET = WURZEL / "n3xtbyt3"
PAKETE = [PAKET, WURZEL / "n3xtbyt3_mcp"]

VERBOTEN = [
    r"\bsubprocess\b",
    r"\bos\.system\b",
    r"\bos\.popen\b",
    r"\bos\.spawn\w*",
    r"\bos\.exec\w*",
    r"\bsocket\b",
    r"\burllib\b",
    r"\bhttp\.client\b",
    r"\brequests\b",
    r"\bwebbrowser\b",
    r"\bctypes\b",
]


class SicherheitTest(unittest.TestCase):
    def test_keine_systemaufrufe_und_kein_netzwerk(self):
        dateien = sorted(d for paket in PAKETE for d in paket.rglob("*.py"))
        self.assertTrue(dateien, "Keine Python-Dateien gefunden.")
        funde = []
        for datei in dateien:
            text = datei.read_text(encoding="utf-8")
            for muster in VERBOTEN:
                for treffer in re.finditer(muster, text):
                    zeile = text.count("\n", 0, treffer.start()) + 1
                    funde.append(f"{datei.relative_to(WURZEL)}:{zeile}: {treffer.group(0)}")
        self.assertEqual(funde, [], "Verbotene Aufrufe gefunden:\n" + "\n".join(funde))


if __name__ == "__main__":
    unittest.main()
