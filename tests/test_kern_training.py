import json
import random
import unittest
from collections import Counter
from pathlib import Path

from n3xtbyt3.kern import auswertung, training
from n3xtbyt3.kern.befehle import Vergleicher
from n3xtbyt3.kern.spielstand import Spielstand
from n3xtbyt3.kern.systeme import SYSTEME
from n3xtbyt3.kern.szenario import lade_system, pruefe_daten

from .hilfen import Datenordner, mini


def szenario_mit_bedeutung():
    daten = mini()
    daten["befehle"][0]["bedeutung"] = "Status eines Dienstes anzeigen"
    daten["befehle"][1]["bedeutung"] = "Einen Dienst starten"
    daten["befehle"][2]["bedeutung"] = "Neustart"  # falsch → keine Karte
    s, fehler = pruefe_daten(daten)
    assert not fehler
    return s


class TrainingTest(unittest.TestCase):
    def setUp(self):
        self.sz = szenario_mit_bedeutung()
        self.karten = training.sammle_karten([self.sz])
        self.v = Vergleicher(SYSTEME["windows"])

    def test_karten(self):
        self.assertEqual([k.bedeutung for k in self.karten],
                         ["Status eines Dienstes anzeigen", "Einen Dienst starten"])
        self.assertEqual(self.karten[0].beispiel, "Get-Service Testdienst")
        self.assertIn("Testszenario", training.frage_text(self.karten[0]))

    def test_doppelte_zusammengefasst(self):
        zweites, _ = pruefe_daten({**mini(id="test-zwei"), "titel": "Zweites",
                                   "befehle": mini()["befehle"][:1]})
        zweites.befehle[0].bedeutung = "Status eines Dienstes anzeigen"
        karten = training.sammle_karten([self.sz, zweites])
        self.assertEqual(len(karten), 2)
        self.assertEqual(karten[0].szenarien, ["Testszenario", "Zweites"])

    def test_bewerten(self):
        karte = self.karten[1]
        self.assertEqual(training.bewerte(karte, "start-service -name testdienst", self.v), "richtig")
        self.assertEqual(training.bewerte(karte, "Start-Service Anderer", self.v), "halb")
        self.assertEqual(training.bewerte(karte, "Restart-Service Testdienst", self.v), "falsch")
        self.assertEqual(training.bewerte(karte, "", self.v), "falsch")

    def test_auswahl_bevorzugt_falsche(self):
        stand = Spielstand("windows")
        kartei = stand.kartei
        kartei.befehl_ergebnis(self.karten[0].schluessel, "richtig")  # Fach 2, morgen fällig
        rng = random.Random(4)
        zaehler = Counter(training.waehle_karte(self.karten, kartei, rng=rng).schluessel for _ in range(100))
        self.assertEqual(zaehler[self.karten[0].schluessel], 0)

    def test_alle_mitgelieferten_haben_fragen(self):
        with Datenordner():
            karten = training.sammle_karten(lade_system("windows").szenarien)
        self.assertGreaterEqual(len(karten), 20)


class AuswertungTest(unittest.TestCase):
    def test_auswertung_schreiben(self):
        sz = szenario_mit_bedeutung()
        with Datenordner() as ordner:
            stand = Spielstand.lade("windows")
            stand.versuch_eintragen(sz.id, {
                "datum": "2026-11-04T10:00:00", "geloest": False, "hinweise": 3,
                "falsche_befehle": 2, "unbekannte_befehle": 1, "befehle": 5, "sekunden": 300,
                "falsch": ["shutdown /r /t 0", "Get-Service Falsch"], "unbekannt": ["format C:"]})
            karte = training.sammle_karten([sz])[0]
            stand.kartei.befehl_ergebnis(karte.schluessel, "falsch")
            daten = auswertung.schreibe("windows", [sz], stand)
            self.assertTrue((Path(ordner) / "auswertung_windows.json").exists())
            md = (Path(ordner) / "auswertung_windows.md").read_text(encoding="utf-8")
            json.loads((Path(ordner) / "auswertung_windows.json").read_text(encoding="utf-8"))
        self.assertEqual(daten["kategorien"][0]["bewertung"], "schwach")
        self.assertTrue(any("zuletzt nicht gelöst" in s for s in daten["schwaechen"]))
        self.assertTrue(any("Wiederholen" in e for e in daten["empfehlung"]))
        self.assertEqual(daten["haeufige_fehler"]["unbekannt"][0]["befehl"], "format")
        self.assertIn("# Auswertung Windows", md)
        self.assertIn("Get-Service Testdienst", md)

    def test_leere_auswertung(self):
        sz = szenario_mit_bedeutung()
        daten = auswertung.erstelle("windows", [sz], Spielstand("windows"))
        self.assertEqual(daten["kategorien"][0]["bewertung"], "noch nicht geübt")
        self.assertTrue(any("Neu ausprobieren" in e for e in daten["empfehlung"]))
        auswertung.als_markdown(daten)


class AbnahmeM2Test(unittest.TestCase):
    """Abnahme M2 (PLAN.md), soweit automatisch prüfbar."""

    def test_windows_server_durchlauf(self):
        from n3xtbyt3.kern import auswahl
        from n3xtbyt3.kern.sitzung import Sitzung
        from n3xtbyt3.kern.szenario import lade_allgemein

        with Datenordner():
            allgemein = lade_allgemein("windows_server")
            szenarien = lade_system("windows_server", allgemein=allgemein).szenarien
            self.assertGreaterEqual(len(szenarien), 15)
            stand = Spielstand.lade("windows_server")
            schwach = szenarien[0]
            # Mehrere Durchläufe: alle anderen sauber gelöst, eines zweimal nicht gelöst
            for sz in szenarien[1:]:
                s = Sitzung(sz, allgemein)
                for schritt in sz.loesung:
                    s.eingabe(schritt)
                stand.versuch_eintragen(sz.id, s.ergebnis())
            for _ in range(2):
                s = Sitzung(schwach, allgemein)
                s.eingabe("Get-Process")
                s.naechster_hinweis()
                stand.versuch_eintragen(schwach.id, s.ergebnis())
            daten = auswertung.erstelle("windows_server", szenarien, stand)
            self.assertTrue(any(schwach.titel in t for t in daten["schwaechen"]), daten["schwaechen"])
            self.assertTrue(any(schwach.kategorie in t for t in daten["schwaechen"]))
            self.assertTrue(any(schwach.titel in e for e in daten["empfehlung"]))
            # Das nicht gelöste Szenario kommt sichtbar öfter wieder
            rng = random.Random(5)
            zaehler = Counter(auswahl.waehle(szenarien, stand, rng=rng).id for _ in range(200))
            self.assertEqual(zaehler.most_common(1)[0][0], schwach.id)


if __name__ == "__main__":
    unittest.main()
