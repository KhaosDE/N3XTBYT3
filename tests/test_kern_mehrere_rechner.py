import unittest

from n3xtbyt3.kern.sitzung import ERFOLG, Sitzung
from n3xtbyt3.kern.szenario import lade_allgemein, pruefe_daten

from .hilfen import mini


def zwei_rechner(**extra):
    daten = mini(
        id="test-zwei-rechner", zustand={"dienst": "Stopped", "webseite_geht": False},
        befehle=[
            {"muster": ["Test-NetConnection srv-web01 -Port 80"], "faelle": [
                {"wenn": {"srv-web01:nginx": "active"}, "ausgabe": "TcpTestSucceeded : True"},
                {"ausgabe": "TcpTestSucceeded : False"}]},
        ],
        rechner={
            "srv-web01": {
                "system": "linux_server",
                "zustand": {"nginx": "inactive"},
                "dateien": {"/etc/nginx/nginx.conf": "worker_processes auto;"},
                "befehle": [{"muster": ["systemctl start nginx"], "faelle": [
                    {"wenn": {"root": False}, "sim": True, "ausgabe": "sudo!"},
                    {"setze": {"nginx": "active", "pc-buero-07:webseite_geht": True}}]}],
            },
            "srv-datei01": {"system": "windows_server", "zustand": {"frei": False},
                            "befehle": [{"muster": ["Clear-RecycleBin -Force"], "faelle": [{"setze": {"frei": True}}]}]},
        },
        ziel={"srv-web01:nginx": "active", "webseite_geht": True},
        loesung=["ssh admin@srv-web01", "sudo systemctl start nginx", "exit"],
        ticket={"nummer": "T-1", "von": "Vertrieb", "dringlichkeit": "hoch", "betreff": "Shop weg", "text": "Shop geht nicht."},
    )
    daten.update(extra)
    szenario, fehler = pruefe_daten(daten)
    assert not fehler, fehler
    return Sitzung(szenario, lade_allgemein("windows"))


def texte(antwort):
    return "\n".join(z.text for z in antwort.zeilen)


class MehrereRechnerTest(unittest.TestCase):
    def test_pruefung(self):
        _, fehler = pruefe_daten(mini(rechner={"srv": {"system": "macos"}}))
        self.assertTrue(any("system" in f for f in fehler))
        _, fehler = pruefe_daten(mini(ziel={"srv-x:nginx": "active"}))
        self.assertTrue(any("srv-x:nginx" in f for f in fehler))
        _, fehler = pruefe_daten(mini(rechner={"pc-buero-07": {"system": "linux"}}))
        self.assertTrue(any("schon der Rechner" in f for f in fehler))

    def test_ssh_wechsel_und_zurueck(self):
        s = zwei_rechner()
        self.assertEqual(s.eingabe("Test-NetConnection srv-web01 -Port 80").zeilen[0].text, "TcpTestSucceeded : False")
        a = s.eingabe("ssh admin@srv-web01")
        self.assertIn("Verbunden mit srv-web01", texte(a))
        self.assertEqual(s.prompt(), "admin@srv-web01:~$ ")
        self.assertIn("sudo!", texte(s.eingabe("systemctl start nginx")))
        a = s.eingabe("sudo systemctl start nginx")
        self.assertTrue(a.geloest_jetzt)
        self.assertIn("Ticket", texte(a))
        a = s.eingabe("exit")
        self.assertIn("Connection to srv-web01 closed.", texte(a))
        self.assertTrue(s.prompt().startswith("PS C:\\Windows\\system32>"))
        self.assertEqual(s.eingabe("Test-NetConnection srv-web01 -Port 80").zeilen[0].text, "TcpTestSucceeded : True")

    def test_linux_befehle_nur_auf_linux(self):
        s = zwei_rechner()
        self.assertEqual(s.eingabe("ls").art, "unbekannt")  # Windows-PowerShell kennt hier kein ls
        s.eingabe("ssh srv-web01")
        self.assertEqual(s.eingabe("cat /etc/nginx/nginx.conf").zeilen[0].text, "worker_processes auto;")

    def test_enter_pssession(self):
        s = zwei_rechner()
        s.eingabe("cmd")
        a = s.eingabe("Enter-PSSession -ComputerName srv-datei01")
        self.assertEqual(a.art, "falsch")
        s.eingabe("exit")
        s.eingabe("Enter-PSSession srv-datei01")
        self.assertEqual(s.prompt(), "[SRV-DATEI01]: PS C:\\Users\\Administrator\\Documents> ")
        s.eingabe("Clear-RecycleBin -Force")
        self.assertTrue(s.rechner["srv-datei01"].zustand.get("frei"))
        s.eingabe("Exit-PSSession")
        self.assertTrue(s.prompt().startswith("PS C:\\Windows\\system32>"))

    def test_ticket_schliessen(self):
        s = zwei_rechner()
        ok, meldung = s.ticket_schliessen("Nginx gestartet, war aus.")
        self.assertFalse(ok)
        self.assertIn("besteht noch", meldung)
        for schritt in s.szenario.loesung:
            s.loesungsschritt(schritt)
        self.assertTrue(s.geloest)
        self.assertFalse(s.ticket_schliessen("kurz")[0])
        ok, meldung = s.ticket_schliessen("nginx auf srv-web01 gestartet")
        self.assertTrue(ok)
        e = s.ergebnis()
        self.assertTrue(e["ticket_geschlossen"])
        self.assertEqual(e["ticket_notiz"], "nginx auf srv-web01 gestartet")


if __name__ == "__main__":
    unittest.main()
