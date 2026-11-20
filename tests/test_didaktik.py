"""Lernprinzip (CLAUDE.md, IDEEN.md „Lernprinzip“, freigegeben 20.11.2026).

Alles, was eine Aufgabe verlangt, ist vorher erklärt; jede Erklärung nach einem Schritt erklärt wirklich
(mindestens zwei Sätze); Szenarien nutzen nur Erklärtes. Ausnahmen nur über `suchaufgabe` (ab Lektion 3,
höchstens eine je Lektion, Text nennt das Suchwerkzeug) und `absichtlich_unbekannt`.
"""

import importlib.util
import unittest
from pathlib import Path

from tests.hilfen import Datenordner


def _werkzeug():
    pfad = Path(__file__).resolve().parent.parent / "werkzeuge" / "didaktikpruefung.py"
    spec = importlib.util.spec_from_file_location("didaktikpruefung", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


class DidaktikTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with Datenordner():
            werkzeug = _werkzeug()
            cls.grundkurs, wissen = werkzeug.pruefe_grundkurs()
            cls.szenarien = werkzeug.pruefe_szenarien(wissen)

    @staticmethod
    def _liste(befunde):
        return "\n".join(f"{ort} {wo}: {art}: {inhalt[:100]}" for ort, wo, art, inhalt in befunde)

    def test_grundkurs_erklaert_alles_vorher(self):
        self.assertEqual(self.grundkurs, [], "\n" + self._liste(self.grundkurs))

    def test_szenarien_nutzen_nur_erklaertes(self):
        self.assertEqual(self.szenarien, [], "\n" + self._liste(self.szenarien))


if __name__ == "__main__":
    unittest.main()
