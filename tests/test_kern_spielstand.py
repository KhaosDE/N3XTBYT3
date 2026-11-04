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
        self.assertEqual(auswahl.gewicht(stand.eintrag("neu")), 5.0)
        stand.versuch_eintragen("falsch", versuch(geloest=False))
        self.assertEqual(auswahl.gewicht(stand.eintrag("falsch")), 6.0)
        stand.versuch_eintragen("sauber", versuch())
        self.assertEqual(auswahl.gewicht(stand.eintrag("sauber")), 1.0)
        stand.versuch_eintragen("hilfe", versuch(hinweise=3, falsch=2))
        self.assertEqual(auswahl.gewicht(stand.eintrag("hilfe")), 5.0)

    def test_ungeloeste_kommen_oefter(self):
        liste = self.szenarien(2)
        stand = Spielstand("windows")
        stand.versuch_eintragen("s0", versuch())                 # sauber gelöst
        stand.versuch_eintragen("s1", versuch(geloest=False))    # nicht gelöst
        rng = random.Random(1)
        zaehler = Counter(auswahl.waehle(liste, stand, rng=rng).id for _ in range(700))
        self.assertGreater(zaehler["s1"], zaehler["s0"] * 3)

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


if __name__ == "__main__":
    unittest.main()
