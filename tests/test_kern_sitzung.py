import unittest

from n3xtbyt3.kern.sitzung import ERFOLG, FEHLER, SIM, Sitzung
from n3xtbyt3.kern.szenario import lade_allgemein, pruefe_daten

from .hilfen import mini


class Uhr:
    def __init__(self):
        self.t = 100.0

    def __call__(self):
        return self.t


def sitzung(daten=None, uhr=None):
    szenario, fehler = pruefe_daten(daten or mini())
    assert not fehler, fehler
    return Sitzung(szenario, lade_allgemein(szenario.system.id), uhr=uhr or Uhr())


class SitzungTest(unittest.TestCase):
    def test_loesen(self):
        s = sitzung()
        a = s.eingabe("Get-Service Testdienst")
        self.assertEqual(a.art, "treffer")
        self.assertEqual(a.zeilen[0].text, "Stopped  Testdienst")
        self.assertFalse(s.geloest)
        a = s.eingabe("start-service -name testdienst")
        self.assertTrue(a.geloest_jetzt)
        self.assertTrue(s.geloest)
        self.assertTrue(any(z.art == ERFOLG for z in a.zeilen))
        self.assertEqual(s.eingabe("Get-Service Testdienst").zeilen[0].text, "Running  Testdienst")

    def test_leere_eingabe(self):
        s = sitzung()
        self.assertEqual(s.eingabe("   ").art, "leer")
        self.assertEqual(s.anzahl_befehle, 0)

    def test_unbekannter_befehl(self):
        s = sitzung()
        a = s.eingabe("format C:")
        self.assertEqual(a.art, "unbekannt")
        self.assertTrue(all(z.art == SIM for z in a.zeilen))
        self.assertIn("In dieser Simulation nicht vorhanden", a.zeilen[0].text)
        self.assertEqual(s.unbekannte, ["format C:"])

    def test_bekannter_befehl_falsche_parameter(self):
        s = sitzung()
        a = s.eingabe("Get-Service Falsch")
        self.assertEqual(a.art, "nicht_erkannt")
        self.assertIn("nicht in dieser Form", a.zeilen[0].text)

    def test_falle(self):
        s = sitzung()
        a = s.eingabe("shutdown /r /t 0")
        self.assertEqual(a.art, "falsch")
        self.assertIn("Holzhammer", a.warum)
        self.assertEqual(s.ergebnis()["falsche_befehle"], 1)

    def test_tippfehler_vorschlag(self):
        s = sitzung()
        a = s.eingabe("hostnam")
        self.assertIn("Meintest du", "\n".join(z.text for z in a.zeilen))

    def test_cmdlet_in_cmd(self):
        s = sitzung(mini(shell="cmd"))
        a = s.eingabe("Get-Service Testdienst")
        self.assertEqual(a.art, "falsch")
        text = "\n".join(z.text for z in a.zeilen)
        self.assertIn("PowerShell", text)
        self.assertIn("is not recognized", text)

    def test_shell_wechsel(self):
        s = sitzung()
        self.assertEqual(s.shell, "powershell")
        self.assertTrue(s.prompt().startswith("PS "))
        s.eingabe("cmd")
        self.assertEqual(s.shell, "cmd")
        self.assertEqual(s.prompt(), "C:\\Windows\\system32>")
        self.assertEqual(s.eingabe("sc query Testdienst").zeilen[0].text, "SERVICE_NAME: Testdienst")
        s.eingabe("exit")
        self.assertEqual(s.shell, "powershell")
        a = s.eingabe("exit")
        self.assertEqual(s.shell, "powershell")
        self.assertIn("Esc", a.zeilen[-1].text)

    def test_sc_falle_in_powershell(self):
        s = sitzung()
        a = s.eingabe("sc query Testdienst")
        self.assertEqual(a.art, "falsch")
        self.assertIn("Set-Content", a.warum)
        self.assertEqual(s.eingabe("sc.exe query Testdienst").art, "falsch")  # nur in cmd hinterlegt

    def test_allgemeine_befehle(self):
        s = sitzung()
        self.assertEqual(s.eingabe("hostname").zeilen[0].text, "PC-BUERO-07")
        self.assertEqual(s.eingabe("cls").aktion, "leeren")
        hilfe = "\n".join(z.text for z in s.eingabe("help").zeilen)
        self.assertIn("F1", hilfe)
        self.assertNotIn("Start-Service", hilfe)  # verrät die Lösung nicht

    def test_hinweise_stufenweise(self):
        s = sitzung()
        self.assertEqual(s.naechster_hinweis(), "Richtung")
        self.assertEqual(s.naechster_hinweis(), "Werkzeug")
        self.assertEqual(s.naechster_hinweis(), "Fast die Lösung")
        self.assertIsNone(s.naechster_hinweis())
        self.assertEqual(s.hinweis_stufe, 3)

    def test_zeit_und_ergebnis(self):
        uhr = Uhr()
        s = sitzung(uhr=uhr)
        uhr.t += 42
        s.eingabe("Start-Service Testdienst")
        uhr.t += 100  # nach dem Lösen zählt die Zeit nicht weiter
        e = s.ergebnis()
        self.assertTrue(e["geloest"])
        self.assertEqual(e["sekunden"], 42)
        self.assertEqual(e["befehle"], 1)

    def test_fehlerausgabe(self):
        daten = mini()
        daten["befehle"][0]["faelle"][0]["fehler"] = True
        s = sitzung(daten)
        self.assertEqual(s.eingabe("Get-Service Testdienst").zeilen[0].art, FEHLER)


class LinuxTest(unittest.TestCase):
    def test_gross_klein(self):
        daten = mini(system="linux", befehle=[
            {"muster": ["systemctl start testdienst"], "faelle": [{"setze": {"dienst": "Running"}}]}
        ], loesung=["systemctl start testdienst"])
        s = sitzung(daten)
        a = s.eingabe("Systemctl start testdienst")
        self.assertEqual(a.art, "unbekannt")
        self.assertIn("Groß- und Kleinschreibung", "\n".join(z.text for z in a.zeilen))
        self.assertTrue(s.eingabe("systemctl start testdienst").geloest_jetzt)


if __name__ == "__main__":
    unittest.main()
