import json
import random
import unittest
from collections import Counter
from pathlib import Path

from n3xtbyt3.kern import auswahl, einstellungen, pfade
from n3xtbyt3.kern.spielstand import Spielstand
from n3xtbyt3.kern.szenario import pruefe_daten

from .hilfen import Datenordner, mini


def versuch(geloest=True, hinweise=0, falsch=0, befehle=3):
    return {"datum": "2026-11-04T10:00:00", "geloest": geloest, "hinweise": hinweise,
            "falsche_befehle": falsch, "unbekannte_befehle": 0, "befehle": befehle,
            "sekunden": 60, "falsch": [], "unbekannt": []}


class SpielstandTest(unittest.TestCase):
    def test_speichern_und_laden(self):
        with Datenordner() as ordner:
            stand = Spielstand.lade("windows")
            self.assertTrue(stand.versuch_eintragen("a", versuch(geloest=False, hinweise=2, falsch=1)))
            self.assertTrue(stand.versuch_eintragen("a", versuch(geloest=True, hinweise=1)))
            stand.speichere()
            datei = Path(ordner) / "spielstand_windows.json"
            self.assertTrue(datei.exists())
            roh = json.loads(datei.read_text(encoding="utf-8"))  # lesbares JSON
            self.assertEqual(roh["system"], "windows")
            e = Spielstand.lade("windows").eintrag("a")
            self.assertEqual(e["versuche"], 2)
            self.assertTrue(e["geloest"])
            self.assertEqual(e["geloest_anzahl"], 1)
            self.assertEqual(e["hinweise_max"], 2)
            self.assertEqual(e["hinweise_gesamt"], 3)
            self.assertEqual(e["falsche_befehle"], 1)
            self.assertEqual(e["zeit_sekunden"], 120)
            self.assertEqual(len(e["verlauf"]), 2)

    def test_je_system_eine_datei(self):
        with Datenordner() as ordner:
            for sid in ("windows", "linux"):
                stand = Spielstand.lade(sid)
                stand.versuch_eintragen("x", versuch())
                stand.speichere()
            self.assertTrue((Path(ordner) / "spielstand_linux.json").exists())
            self.assertTrue((Path(ordner) / "spielstand_windows.json").exists())

    def test_leerer_versuch_zaehlt_nicht(self):
        with Datenordner():
            stand = Spielstand.lade("windows")
            self.assertFalse(stand.versuch_eintragen("a", versuch(geloest=False, befehle=0)))
            self.assertFalse(stand.gesehen("a"))

    def test_kaputte_datei_wird_gesichert(self):
        with Datenordner() as ordner:
            (Path(ordner) / "spielstand_windows.json").write_text("{kaputt", encoding="utf-8")
            stand = Spielstand.lade("windows")
            self.assertIsNotNone(stand.warnung)
            self.assertEqual(stand.daten["szenarien"], {})
            self.assertTrue(list(Path(ordner).glob("spielstand_windows.defekt-*.json")))

    def test_schreiben_nur_im_datenordner(self):
        with Datenordner():
            with self.assertRaises(ValueError):
                pfade.im_datenordner("..", "ausserhalb.json")

    def test_einstellungen(self):
        with Datenordner():
            self.assertEqual(einstellungen.lade()["schriftgroesse"], 20)
            einstellungen.speichere({"schriftgroesse": 99, "vollbild": True})
            werte = einstellungen.lade()
            self.assertEqual(werte["schriftgroesse"], einstellungen.SCHRIFT_MAX)
            self.assertTrue(werte["vollbild"])


class AuswahlTest(unittest.TestCase):
    def szenarien(self, anzahl):
        liste = []
        for i in range(anzahl):
            s, fehler = pruefe_daten(mini(id=f"s{i}"))
            assert not fehler
            liste.append(s)
        return liste

    def test_gewichte(self):
        stand = Spielstand("windows")
        self.assertEqual(auswahl.gewicht(stand, "neu"), auswahl.GEWICHT_NEU)
        stand.versuch_eintragen("falsch", versuch(geloest=False))
        self.assertEqual(stand.kartei.szenario("falsch")["fach"], 1)
        self.assertEqual(auswahl.gewicht(stand, "falsch"), auswahl.GEWICHT_FAELLIG[1])
        stand.versuch_eintragen("sauber", versuch())
        self.assertEqual(stand.kartei.szenario("sauber")["fach"], 2)
        self.assertFalse(auswahl.faellig(stand, "sauber"))  # erst morgen wieder
        self.assertTrue(auswahl.faellig(stand, "falsch"))

    def test_falsch_geloeste_kommen_oefter(self):
        liste = self.szenarien(3)
        stand = Spielstand("windows")
        stand.versuch_eintragen("s0", versuch())                 # sauber gelöst → Fach 2, morgen
        stand.versuch_eintragen("s1", versuch(geloest=False))    # nicht gelöst → Fach 1, sofort
        stand.versuch_eintragen("s2", versuch(hinweise=3))       # mit Hilfe → bleibt Fach 1
        rng = random.Random(1)
        zaehler = Counter(auswahl.waehle(liste, stand, rng=rng).id for _ in range(300))
        self.assertEqual(zaehler["s0"], 0)  # nicht fällig, solange anderes fällig ist
        self.assertGreater(zaehler["s1"], 50)
        self.assertGreater(zaehler["s2"], 50)

    def test_nichts_faellig_niedrige_faecher_zuerst(self):
        liste = self.szenarien(2)
        stand = Spielstand("windows")
        for _ in range(3):
            stand.versuch_eintragen("s0", versuch())  # Fach 4
        stand.versuch_eintragen("s1", versuch())      # Fach 2
        rng = random.Random(3)
        zaehler = Counter(auswahl.waehle(liste, stand, rng=rng).id for _ in range(600))
        self.assertGreater(zaehler["s1"], zaehler["s0"])

    def test_nicht_zweimal_hintereinander(self):
        liste = self.szenarien(3)
        stand = Spielstand("windows")
        rng = random.Random(2)
        for _ in range(50):
            self.assertNotEqual(auswahl.waehle(liste, stand, zuletzt="s0", rng=rng).id, "s0")

    def test_einzelnes_und_leeres(self):
        liste = self.szenarien(1)
        stand = Spielstand("windows")
        self.assertEqual(auswahl.waehle(liste, stand, zuletzt="s0").id, "s0")
        self.assertIsNone(auswahl.waehle([], stand))


class LernkarteiTest(unittest.TestCase):
    def test_szenario_faecher(self):
        import datetime as dt
        stand = Spielstand("windows")
        k = stand.kartei
        tag = dt.date(2026, 11, 4)
        self.assertEqual(k.szenario_ergebnis("a", versuch(), am=tag)["fach"], 2)
        self.assertEqual(k.szenario("a")["faellig"], "2026-11-05")
        self.assertEqual(k.szenario_ergebnis("a", versuch(), am=tag)["fach"], 3)
        self.assertEqual(k.szenario("a")["faellig"], "2026-11-07")
        self.assertEqual(k.szenario_ergebnis("a", versuch(hinweise=1), am=tag)["fach"], 3)
        self.assertEqual(k.szenario_ergebnis("a", versuch(hinweise=2), am=tag)["fach"], 2)
        self.assertEqual(k.szenario_ergebnis("a", versuch(geloest=False), am=tag)["fach"], 1)
        self.assertTrue(k.ist_faellig(k.szenario("a"), am=tag))
        for _ in range(10):
            k.szenario_ergebnis("a", versuch(), am=tag)
        self.assertEqual(k.szenario("a")["fach"], 5)

    def test_befehl_faecher_und_speichern(self):
        with Datenordner():
            stand = Spielstand.lade("windows")
            k = stand.kartei
            self.assertEqual(k.befehl_ergebnis("x", "richtig")["fach"], 2)
            self.assertEqual(k.befehl_ergebnis("x", "halb")["fach"], 2)
            self.assertEqual(k.befehl_ergebnis("x", "falsch")["fach"], 1)
            stand.speichere()
            karte = Spielstand.lade("windows").kartei.befehl("x")
            self.assertEqual((karte["fach"], karte["richtig"], karte["falsch"]), (1, 1, 1))


if __name__ == "__main__":
    unittest.main()
