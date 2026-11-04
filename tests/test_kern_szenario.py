import json
import tempfile
import unittest
from pathlib import Path

from n3xtbyt3.kern.szenario import (
    SzenarioFehler, lade_allgemein, lade_system, lade_szenario, pruefe_daten,
)
from n3xtbyt3.kern.systeme import REIHENFOLGE

from .hilfen import Datenordner, mini


class PruefungTest(unittest.TestCase):
    def fehler(self, daten):
        szenario, fehler = pruefe_daten(daten)
        return fehler

    def test_mini_ist_gueltig(self):
        szenario, fehler = pruefe_daten(mini())
        self.assertEqual(fehler, [])
        self.assertEqual(szenario.id, "test-mini")
        self.assertEqual(szenario.shell, "powershell")
        self.assertEqual(szenario.quelle, [mini()["quelle"]])

    def test_fehlendes_pflichtfeld(self):
        fehler = self.fehler(mini(hinweise=None))
        self.assertTrue(any("hinweise" in f for f in fehler), fehler)

    def test_unbekanntes_system(self):
        fehler = self.fehler(mini(system="macos"))
        self.assertTrue(any("Unbekanntes System" in f for f in fehler), fehler)

    def test_unbekanntes_feld(self):
        self.assertTrue(self.fehler(mini(hinweis=["x"])))
        self.assertEqual(self.fehler(mini(_kommentar="erlaubt")), [])

    def test_schwierigkeit_und_pruefstatus(self):
        self.assertTrue(self.fehler(mini(schwierigkeit=4)))
        self.assertTrue(self.fehler(mini(schwierigkeit=True)))
        self.assertTrue(self.fehler(mini(pruefstatus="geprueft")))

    def test_quelle_muss_adresse_sein(self):
        self.assertTrue(self.fehler(mini(quelle="Microsoft")))

    def test_datum(self):
        self.assertTrue(self.fehler(mini(datum="04.11.2026")))

    def test_drei_hinweise(self):
        self.assertTrue(self.fehler(mini(hinweise=["a", "b"])))

    def test_unbekannter_zustandsschluessel(self):
        self.assertTrue(self.fehler(mini(ziel={"dienstt": "Running"})))
        daten = mini()
        daten["befehle"][1]["faelle"][0]["setze"] = {"gibtsnicht": 1}
        self.assertTrue(self.fehler(daten))

    def test_allgemeine_schluessel_sind_bekannt(self):
        self.assertEqual(self.fehler(mini(ziel={"admin": True})), [])

    def test_falsch_braucht_warum(self):
        daten = mini()
        del daten["befehle"][2]["warum"]
        self.assertTrue(self.fehler(daten))

    def test_falsche_shell(self):
        daten = mini()
        daten["befehle"][0]["shell"] = "bash"
        self.assertTrue(self.fehler(daten))

    def test_cmdlets_standardmaessig_nur_powershell(self):
        szenario, _ = pruefe_daten(mini())
        self.assertEqual(szenario.befehle[0].shells, ("powershell",))
        self.assertEqual(szenario.befehle[2].shells, ("powershell", "cmd"))

    def test_id_und_dateiname(self):
        with tempfile.TemporaryDirectory() as tmp:
            datei = Path(tmp) / "anderer-name.json"
            datei.write_text(json.dumps(mini()), encoding="utf-8")
            with self.assertRaises(SzenarioFehler) as ctx:
                lade_szenario(datei)
            self.assertIn("Dateiname", str(ctx.exception))

    def test_kaputtes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            datei = Path(tmp) / "test-mini.json"
            datei.write_text('{"id": "test-mini",', encoding="utf-8")
            with self.assertRaises(SzenarioFehler) as ctx:
                lade_szenario(datei)
            self.assertIn("Kein gültiges JSON", str(ctx.exception))


class LadenTest(unittest.TestCase):
    def test_alle_mitgelieferten_szenarien_laden(self):
        """Jede Szenario-Datei im Repository lädt fehlerfrei."""
        with Datenordner():
            for system_id in REIHENFOLGE:
                ergebnis = lade_system(system_id)
                self.assertEqual(ergebnis.fehler, [], "\n".join(str(f) for f in ergebnis.fehler))

    def test_allgemeine_befehle_laden(self):
        for system_id in REIHENFOLGE:
            lade_allgemein(system_id)

    def test_eigene_szenarien_aus_dem_datenordner(self):
        with Datenordner() as ordner:
            eigen = Path(ordner) / "szenarien" / "windows"
            eigen.mkdir(parents=True)
            (eigen / "test-mini.json").write_text(json.dumps(mini()), encoding="utf-8")
            (eigen / "kaputt.json").write_text("{", encoding="utf-8")
            ergebnis = lade_system("windows")
            ids = {s.id: s for s in ergebnis.szenarien}
            self.assertIn("test-mini", ids)
            self.assertTrue(ids["test-mini"].eigen)
            self.assertEqual(len(ergebnis.fehler), 1)
            self.assertIn("kaputt.json", str(ergebnis.fehler[0]))

    def test_doppelte_id(self):
        with Datenordner() as ordner:
            eigen = Path(ordner) / "szenarien" / "windows"
            eigen.mkdir(parents=True)
            (eigen / "win-dns-cache.json").write_text(
                json.dumps(mini(id="win-dns-cache")), encoding="utf-8")
            ergebnis = lade_system("windows")
            self.assertTrue(any("gibt es schon" in str(f) for f in ergebnis.fehler))


if __name__ == "__main__":
    unittest.main()
