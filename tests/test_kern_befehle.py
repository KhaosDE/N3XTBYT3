import unittest

from n3xtbyt3.kern.befehle import Vergleicher, befehlsname, ist_cmdlet_name, zerlege
from n3xtbyt3.kern.systeme import SYSTEME
from n3xtbyt3.kern.zustand import Zustand, bedingung_erfuellt, pruefe_aenderung, pruefe_bedingung


class ZerlegenTest(unittest.TestCase):
    def test_woerter_und_anfuehrungszeichen(self):
        self.assertEqual(zerlege('tasklist /FI "IMAGENAME eq EXCEL.EXE"'),
                         [["tasklist", "/FI", "IMAGENAME eq EXCEL.EXE"]])

    def test_backslash_bleibt(self):
        self.assertEqual(zerlege(r"dir C:\Windows\System32"), [["dir", r"C:\Windows\System32"]])

    def test_pipe(self):
        self.assertEqual(zerlege("Get-Service | Where-Object Status -eq Stopped"),
                         [["Get-Service"], ["Where-Object", "Status", "-eq", "Stopped"]])

    def test_pipe_in_anfuehrungszeichen(self):
        self.assertEqual(zerlege('echo "a|b"'), [["echo", "a|b"]])

    def test_leere_anfuehrungszeichen(self):
        self.assertEqual(zerlege('x ""'), [["x", ""]])

    def test_befehlsname(self):
        self.assertEqual(befehlsname("  ipconfig   /all "), "ipconfig")
        self.assertEqual(befehlsname(""), "")

    def test_cmdlet(self):
        self.assertTrue(ist_cmdlet_name("Get-Service"))
        self.assertFalse(ist_cmdlet_name("ipconfig"))


class VergleichTest(unittest.TestCase):
    def setUp(self):
        self.win = Vergleicher(SYSTEME["windows"])
        self.linux = Vergleicher(SYSTEME["linux"])

    def passt(self, v, muster, eingabe):
        return v.passt(v.vorbereiten(muster), v.vorbereiten(eingabe))

    def test_windows_gross_klein_egal(self):
        self.assertTrue(self.passt(self.win, "ipconfig /flushdns", "IPCONFIG /FlushDNS"))

    def test_linux_gross_klein_streng(self):
        self.assertTrue(self.passt(self.linux, "ls -la", "ls -la"))
        self.assertFalse(self.passt(self.linux, "ls -la", "LS -la"))

    def test_leerzeichen_egal(self):
        self.assertTrue(self.passt(self.win, "ipconfig /all", "  ipconfig    /all  "))

    def test_exe_endung(self):
        self.assertTrue(self.passt(self.win, "ipconfig /all", "ipconfig.exe /all"))

    def test_optionen_in_beliebiger_reihenfolge(self):
        self.assertTrue(self.passt(self.win, "taskkill /IM EXCEL.EXE /F", "taskkill /F /IM excel.exe"))
        self.assertTrue(self.passt(self.win, "Restart-Service -Name Spooler -Force",
                                   "Restart-Service -Force -Name Spooler"))

    def test_option_und_wert_gehoeren_zusammen(self):
        self.assertFalse(self.passt(self.win, "taskkill /IM EXCEL.EXE /F", "taskkill /IM /F EXCEL.EXE"))

    def test_positionen_in_fester_reihenfolge(self):
        self.assertFalse(self.passt(self.win, "net use Z: \\\\SRV\\Daten", "net Z: use \\\\SRV\\Daten"))

    def test_fehlender_parameter(self):
        self.assertFalse(self.passt(self.win, "taskkill /IM EXCEL.EXE /F", "taskkill /IM EXCEL.EXE"))

    def test_platzhalter(self):
        self.assertTrue(self.passt(self.win, "ping *", "ping 192.168.1.1"))
        self.assertFalse(self.passt(self.win, "ping *", "ping"))

    def test_pipe_abschnitte(self):
        muster = "Get-Process | Sort-Object CPU -Descending"
        self.assertTrue(self.passt(self.win, muster, "get-process | sort-object cpu -descending"))
        self.assertFalse(self.passt(self.win, muster, "Get-Process"))


class ZustandTest(unittest.TestCase):
    def test_gleich_und_vergleiche(self):
        werte = {"a": True, "n": 5, "s": "Running"}
        self.assertTrue(bedingung_erfuellt(werte, {"a": True, "s": "Running"}))
        self.assertFalse(bedingung_erfuellt(werte, {"a": 1}))  # true ist nicht 1
        self.assertTrue(bedingung_erfuellt(werte, {"n": {">=": 5}}))
        self.assertFalse(bedingung_erfuellt(werte, {"n": {"<": 5}}))
        self.assertTrue(bedingung_erfuellt(werte, {"s": {"in": ["Running", "Paused"]}}))
        self.assertTrue(bedingung_erfuellt(werte, {"s": {"nicht": "Stopped"}}))
        self.assertFalse(bedingung_erfuellt(werte, {"s": {">": 1}}))

    def test_setzen_und_rechnen(self):
        z = Zustand({"n": 1, "s": "a"})
        z.setze({"n": {"+": 2}, "s": "b"})
        self.assertEqual(z["n"], 3)
        self.assertEqual(z["s"], "b")

    def test_fuellen(self):
        z = Zustand({"hostname": "PC-01", "admin": True})
        self.assertEqual(z.fuelle("{hostname} {admin} {unbekannt}"), "PC-01 True {unbekannt}")

    def test_pruefen(self):
        self.assertEqual(pruefe_bedingung({"a": 1}, {"a"}, "x"), [])
        self.assertTrue(pruefe_bedingung({"b": 1}, {"a"}, "x"))
        self.assertTrue(pruefe_bedingung({"a": {"~": 1}}, {"a"}, "x"))
        self.assertTrue(pruefe_bedingung({"a": [1]}, {"a"}, "x"))
        self.assertTrue(pruefe_aenderung({"a": {"*": 2}}, {"a"}, "x"))
        self.assertEqual(pruefe_aenderung({"a": {"-": 2}}, {"a"}, "x"), [])


if __name__ == "__main__":
    unittest.main()
