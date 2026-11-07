"""Tests für Fehler aus der Bugsuche vom 07.11.2026 (jeder Test stellt einen gefundenen Fehler nach)."""

import unittest
from pathlib import Path
from unittest import mock

from n3xtbyt3.kern import auswertung, einstellungen, training
from n3xtbyt3.kern.spielstand import Spielstand
from n3xtbyt3.kern.szenario import lade_system, pruefe_daten

from tests.hilfen import Datenordner, mini


class SpielstandSchutzTest(unittest.TestCase):
    def test_gesperrte_datei_wird_nicht_ueberschrieben(self):
        with Datenordner() as ordner:
            stand = Spielstand("windows")
            stand.versuch_eintragen("win-dns-cache", {"geloest": True, "befehle": 3, "hinweise": 0})
            stand.speichere()
            datei = Path(ordner, "spielstand_windows.json")
            vorher = datei.read_text(encoding="utf-8")
            with mock.patch.object(Path, "read_text", side_effect=PermissionError("gesperrt")):
                gesperrt = Spielstand.lade("windows")
            self.assertTrue(gesperrt.nicht_speichern)
            self.assertIn("nicht lesen", gesperrt.warnung)
            gesperrt.versuch_eintragen("win-apipa", {"geloest": True, "befehle": 2, "hinweise": 0})
            with self.assertRaises(OSError):
                gesperrt.speichere()
            self.assertEqual(datei.read_text(encoding="utf-8"), vorher)  # nichts verloren
            self.assertEqual([p.name for p in Path(ordner).glob("*.defekt-*")], [])

    def test_falsche_zeichenkodierung_wird_gesichert(self):
        with Datenordner() as ordner:
            Path(ordner, "einstellungen.json").write_bytes(b'{"schriftgroesse": 24, "x": "\xe4"}')  # ANSI statt UTF-8
            werte = einstellungen.lade()  # stürzte vorher mit UnicodeDecodeError ab
            self.assertEqual(werte["schriftgroesse"], einstellungen.STANDARD["schriftgroesse"])
            self.assertEqual(len(list(Path(ordner).glob("einstellungen.defekt-*.json"))), 1)


class AuswertungTest(unittest.TestCase):
    def test_pipe_im_befehl_verschiebt_keine_spalten(self):
        with Datenordner():
            szenarien = lade_system("windows").szenarien
            stand = Spielstand("windows")
            karten = [k for k in training.sammle_karten(szenarien) if "|" in k.beispiel]
            self.assertTrue(karten)
            stand.kartei.befehl_ergebnis(karten[0].schluessel, "falsch")
            md = auswertung.als_markdown(auswertung.erstelle("windows", szenarien, stand))
            zeile = next(z for z in md.split("\n") if karten[0].beispiel.split("|")[0].strip() in z and z.startswith("|"))
            self.assertEqual(zeile.replace("\\|", "").count("|"), 6)

    def test_beispiele_fuer_falsch_und_unbekannt_getrennt(self):
        with Datenordner():
            szenarien = lade_system("windows").szenarien
            stand = Spielstand("windows")
            stand.versuch_eintragen(szenarien[0].id, {"befehle": 1, "falsch": ["shutdown /r /t 0"], "unbekannt": []})
            stand.versuch_eintragen(szenarien[1].id, {"befehle": 1, "falsch": [], "unbekannt": ["shutdown /a"]})
            a = auswertung.erstelle("windows", szenarien, stand)
            self.assertEqual(a["haeufige_fehler"]["falsch"][0]["beispiel"], "shutdown /r /t 0")
            self.assertEqual(a["haeufige_fehler"]["unbekannt"][0]["beispiel"], "shutdown /a")


class IdTest(unittest.TestCase):
    def test_zeilenumbruch_in_der_id(self):
        _, fehler = pruefe_daten(mini(id="test-mini\n"))
        self.assertTrue(any("„id“" in f for f in fehler))
        _, fehler = pruefe_daten(mini(voraussetzung="gk-win-konsole\n"))
        self.assertTrue(any("voraussetzung" in f for f in fehler))


class McpTest(unittest.TestCase):
    def test_szenario_lesen_nur_mit_id(self):
        from n3xtbyt3_mcp import server
        with Datenordner() as ordner:
            geheim = Path(ordner, "geheim.json")
            geheim.write_text('{"geheim": 1}', encoding="utf-8")
            for sid in (str(geheim)[:-5], "../../../../../../" + str(geheim)[1:-5]):
                antwort = server.bearbeite({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                            "params": {"name": "szenario_lesen", "arguments": {"id": sid}}})
                self.assertTrue(antwort["result"]["isError"], sid)
                self.assertNotIn("geheim", antwort["result"]["content"][0]["text"].split("„")[0])

    def test_params_kein_objekt(self):
        from n3xtbyt3_mcp import server
        for params in ([1], "x", 5):
            antwort = server.bearbeite({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": params})
            self.assertEqual(antwort["error"]["code"], -32602)
        antwort = server.bearbeite({"jsonrpc": "2.0", "id": 8, "method": "tools/call",
                                    "params": {"name": "systeme_uebersicht", "arguments": [1]}})
        self.assertEqual(antwort["error"]["code"], -32602)


if __name__ == "__main__":
    unittest.main()


class BefehlsauswertungTest(unittest.TestCase):
    """Funde aus der Durchsicht von sitzung.py, befehle.py und szenario.py."""

    def test_klassische_programme_gehen_auch_in_der_cmd(self):
        from n3xtbyt3.kern.sitzung import Sitzung
        from n3xtbyt3.kern.szenario import lade_allgemein
        sz, fehler = pruefe_daten(mini(befehle=[
            {"muster": ["Stop-Process -Name EXCEL", "taskkill /IM EXCEL.EXE /F", "tnc srv01"],
             "faelle": [{"ausgabe": "ok"}]}]))
        self.assertEqual(fehler, [])
        s = Sitzung(sz, lade_allgemein("windows"))
        s.eingabe("cmd")
        self.assertEqual(s.eingabe("taskkill /IM EXCEL.EXE /F").art, "treffer")
        self.assertEqual(s.eingabe("Stop-Process -Name EXCEL").art, "falsch")  # Cmdlet: nur PowerShell
        self.assertEqual(s.eingabe("tnc srv01").art, "falsch")  # Kurzname der PowerShell

    def test_cmdlet_mit_ziffern(self):
        from n3xtbyt3.kern.befehle import ist_cmdlet_name
        self.assertTrue(ist_cmdlet_name("Get-DhcpServerv4Scope"))
        self.assertFalse(ist_cmdlet_name("ipconfig"))
        sz, _ = pruefe_daten(mini(system="windows_server", befehle=[
            {"muster": ["Get-DhcpServerv4Scope"], "faelle": [{"ausgabe": "x"}]}]))
        self.assertEqual(sz.befehle[0].shells, ("powershell",))

    def test_datum_und_rechnername_streng(self):
        for falsch in ("20261104", "2026-W45-3"):
            _, fehler = pruefe_daten(mini(datum=falsch))
            self.assertTrue(any("datum" in f for f in fehler), falsch)
        _, fehler = pruefe_daten(mini(rechner={"srv\n": {"system": "linux"}}))
        self.assertTrue(fehler)


class SudoUndPipeTest(unittest.TestCase):
    def _linux(self):
        from tests.test_kern_linux import sitzung
        return sitzung()

    def test_sudo_eingebaute_befehle(self):
        s = self._linux()
        a = s.eingabe("sudo cd /root")
        self.assertIn("sudo: cd: command not found", [z.text for z in a.zeilen])
        self.assertNotEqual(s.fs.cwd, "/root")
        self.assertFalse(s.zustand.get("root"))

    def test_sudo_sudo_i(self):
        s = self._linux()
        s.eingabe("sudo sudo -i")
        self.assertTrue(s.zustand.get("root_shell"))

    def test_sudo_ssh_laesst_kein_root_zurueck(self):
        from tests.test_kern_mehrere_rechner import zwei_rechner
        s = zwei_rechner()
        s.eingabe("ssh admin@srv-web01")
        s.eingabe("sudo ssh admin@srv-web01")  # schon dort
        self.assertFalse(s.zustand.get("root"))
        self.assertIn("schon auf srv-web01", "\n".join(z.text for z in s.eingabe("ssh admin@srv-web01").zeilen))

    def test_enter_pssession_in_cmd_zaehlt_als_falsch(self):
        from tests.test_kern_mehrere_rechner import zwei_rechner
        s = zwei_rechner()
        s.eingabe("cmd")
        a = s.eingabe("Enter-PSSession srv-datei01")
        self.assertEqual(a.art, "falsch")
        self.assertEqual(len(s.falsche), 1)

    def test_fehlerzeilen_gehen_nicht_durch_die_pipe(self):
        from n3xtbyt3.kern.sitzung import FEHLER
        s = self._linux()
        a = s.eingabe("cat /root/geheim.txt | grep x")
        self.assertEqual([(z.text, z.art) for z in a.zeilen],
                         [("cat: /root/geheim.txt: Permission denied", FEHLER)])
        a = s.eingabe("cat gibtsnicht | wc -l")
        self.assertEqual([z.text for z in a.zeilen], ["cat: gibtsnicht: No such file or directory", "0"])

    def test_unbekannter_filter_wird_gezaehlt_und_nichts_ausgefuehrt(self):
        s = self._linux()
        a = s.eingabe("sudo systemctl start app | wc -m")
        self.assertEqual(a.art, "nicht_erkannt")
        self.assertEqual(len(s.nicht_erkannt), 1)
        self.assertFalse(s.geloest)

    def test_loesung_mit_pipe_bleibt_geloest(self):
        s = self._linux()
        a = s.eingabe("sudo systemctl start app | grep -x")  # grep-Fehler hinter erfolgreichem Befehl
        self.assertTrue(a.geloest_jetzt)
