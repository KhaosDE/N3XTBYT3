"""Jedes Szenario ist mit seinem hinterlegten Lösungsweg lösbar."""

import unittest

from n3xtbyt3.kern.sitzung import Sitzung
from n3xtbyt3.kern.systeme import REIHENFOLGE
from n3xtbyt3.kern.szenario import lade_allgemein, lade_system

from .hilfen import Datenordner


class LoesbarTest(unittest.TestCase):
    def test_jedes_szenario_ist_loesbar(self):
        with Datenordner():
            for system_id in REIHENFOLGE:
                allgemein = lade_allgemein(system_id)
                for szenario in lade_system(system_id, allgemein=allgemein).szenarien:
                    with self.subTest(szenario=szenario.id):
                        s = Sitzung(szenario, allgemein)
                        self.assertFalse(
                            any(s.zustand.erfuellt(z) for z in szenario.ziel),
                            "Das Ziel ist schon am Anfang erfüllt.")
                        for schritt in szenario.loesung:
                            antwort = s.eingabe(schritt)
                            self.assertIn(
                                antwort.art, ("treffer",),
                                f"Lösungsschritt „{schritt}“ wird nicht erkannt ({antwort.art}): "
                                + " / ".join(z.text for z in antwort.zeilen))
                        self.assertTrue(s.geloest, "Nach dem Lösungsweg ist das Ziel nicht erreicht.")

    def test_es_gibt_szenarien_fuer_windows(self):
        with Datenordner():
            self.assertGreaterEqual(len(lade_system("windows").szenarien), 1)


class SelbsttestTest(unittest.TestCase):
    def test_selbsttest_ohne_fehler(self):
        from n3xtbyt3.kern import selbsttest
        with Datenordner():
            anzahl, fehler = selbsttest.pruefe_alle()
        self.assertEqual(fehler, [])
        self.assertGreaterEqual(anzahl, 10)


if __name__ == "__main__":
    unittest.main()
