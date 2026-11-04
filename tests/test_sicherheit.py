"""Sicherheitstest: N3XTBYT3 ist eine reine Simulation.

Im Paket n3xtbyt3 dürfen keine Werkzeuge vorkommen, mit denen echte Befehle
ausgeführt oder Netzwerkverbindungen aufgebaut werden.
"""

import re
import unittest
from pathlib import Path

PAKET = Path(__file__).resolve().parents[1] / "n3xtbyt3"

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
        dateien = sorted(PAKET.rglob("*.py"))
        self.assertTrue(dateien, "Keine Python-Dateien gefunden.")
        funde = []
        for datei in dateien:
            text = datei.read_text(encoding="utf-8")
            for muster in VERBOTEN:
                for treffer in re.finditer(muster, text):
                    zeile = text.count("\n", 0, treffer.start()) + 1
                    funde.append(f"{datei.relative_to(PAKET.parent)}:{zeile}: {treffer.group(0)}")
        self.assertEqual(funde, [], "Verbotene Aufrufe gefunden:\n" + "\n".join(funde))


if __name__ == "__main__":
    unittest.main()
