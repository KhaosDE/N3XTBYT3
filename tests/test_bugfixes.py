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


def _lx(**dateien):
    from n3xtbyt3.kern.sitzung import Sitzung
    from n3xtbyt3.kern.szenario import lade_allgemein
    from tests.test_kern_linux import linux_szenario
    basis = {
        "/etc/app.conf": {"inhalt": ["port=8080", "debug=true"], "rechte": "644", "besitzer": "root:root"},
        "/home/anna/d/": {}, "/home/anna/d/a.txt": "A", "/home/anna/d/sub/b.txt": "B",
        "/home/anna/f.txt": "F", "/home/anna/z.txt": [f"Z{i}" for i in range(1, 13)],
        "/home/anna/skript.sh": {"inhalt": "#!/bin/bash", "rechte": "755", "besitzer": "anna:anna"},
        "/tmp/fremd.txt": {"inhalt": "x", "besitzer": "root:root"},
        "/root/offen.txt": {"inhalt": "x", "rechte": "644"},
    }
    basis.update(dateien)
    return Sitzung(linux_szenario(dateien=basis), lade_allgemein("linux"))


def _t(s, befehl):
    return [z.text for z in s.eingabe(befehl).zeilen]


class LinuxDateisystemTest(unittest.TestCase):
    """Funde aus der Durchsicht von dateisystem.py (jeweils mit echtem GNU-Verhalten verglichen)."""

    def test_cp_ohne_schreibrecht(self):
        s = _lx()
        self.assertEqual(_t(s, "cp f.txt /etc/app.conf"),
                         ["cp: cannot create regular file '/etc/app.conf': Permission denied"])
        self.assertEqual(s.fs.besitzer("/etc/app.conf"), ("root", "root"))

    def test_cp_rechte_und_selbstkopie(self):
        s = _lx()
        _t(s, "cp skript.sh neu.sh")
        self.assertEqual(s.fs.rechte("/home/anna/neu.sh"), "rwxr-xr-x")  # 755 ohne umask 002
        self.assertEqual(_t(s, "cp f.txt f.txt"), ["cp: 'f.txt' and 'f.txt' are the same file"])
        self.assertEqual(_t(s, "cp -r d d"), ["cp: cannot copy a directory, 'd', into itself, 'd/d'"])

    def test_mv_in_sich_selbst_und_ueberschreiben(self):
        s = _lx(**{"/home/anna/ziel.txt": {"inhalt": "Z", "rechte": "600", "zeit": "Jan  1 00:00"}})
        self.assertEqual(_t(s, "mv d d/sub"), ["mv: cannot move 'd' to a subdirectory of itself, 'd/sub/d'"])
        self.assertTrue(s.fs.ist_datei("/home/anna/d/a.txt"))
        _t(s, "mv f.txt ziel.txt")
        self.assertEqual(s.fs.rechte("/home/anna/ziel.txt"), "rw-r--r--")
        self.assertEqual(s.fs.inhalt("/home/anna/ziel.txt"), "F")
        self.assertEqual(_t(s, "mv d ziel.txt"), ["mv: cannot overwrite non-directory 'ziel.txt' with directory 'd'"])

    def test_ls_d_und_mehrere(self):
        s = _lx()
        self.assertEqual(_t(s, "ls -ld /tmp"), ["drwxrwxrwt 2 root root 4096 Nov  4 09:12 /tmp"])
        self.assertEqual(_t(s, "ls d | wc -l"), ["2"])
        self.assertEqual(_t(s, "ls -1 d"), ["a.txt", "sub"])

    def test_chmod_chown_rekursiv_und_sonderbits(self):
        s = _lx()
        _t(s, "chmod -R 700 d")
        self.assertEqual(s.fs.rechte("/home/anna/d/sub/b.txt"), "rwx------")
        _t(s, "chmod 1777 d")
        self.assertEqual(s.fs.rechte("/home/anna/d"), "rwxrwxrwt")
        _t(s, "chmod u=rw,go= f.txt")
        self.assertEqual(s.fs.rechte("/home/anna/f.txt"), "rw-------")
        self.assertEqual(_t(s, "chmod u5x f.txt")[0], "chmod: invalid mode: 'u5x'")
        _t(s, "sudo chown -R root:root d")
        self.assertEqual(s.fs.besitzer("/home/anna/d/sub/b.txt"), ("root", "root"))

    def test_head_tail_vorzeichen(self):
        s = _lx()
        self.assertEqual(_t(s, "tail -n +11 z.txt"), ["Z11", "Z12"])
        self.assertEqual(_t(s, "head -n -10 z.txt"), ["Z1", "Z2"])
        self.assertEqual(_t(s, "cat z.txt | tail -n +12"), ["Z12"])
        self.assertEqual(_t(s, "head -n 1 f.txt z.txt"), ["==> f.txt <==", "F", "", "==> z.txt <==", "Z1"])

    def test_rechte_auf_dem_weg_und_sticky_bit(self):
        s = _lx()
        self.assertEqual(_t(s, "cat /root/offen.txt"), ["cat: /root/offen.txt: Permission denied"])
        self.assertEqual(_t(s, "rm /tmp/fremd.txt"), ["rm: cannot remove '/tmp/fremd.txt': Operation not permitted"])
        self.assertEqual(_t(s, "sudo cat /root/offen.txt")[-1], "x")

    def test_mkdir_durch_datei_und_ordner_bleiben(self):
        s = _lx()
        self.assertEqual(_t(s, "mkdir -p f.txt/sub"), ["mkdir: cannot create directory 'f.txt/sub': Not a directory"])
        self.assertTrue(s.fs.ist_datei("/home/anna/f.txt"))
        _t(s, "rm d/sub/b.txt")
        self.assertTrue(s.fs.ist_verzeichnis("/home/anna/d/sub"))

    def test_grep_optionen(self):
        s = _lx(**{"/home/anna/p.txt": ["a.b", "axb", "port 80", "Port=1"]})
        self.assertEqual(_t(s, "grep -E 'port|Port' p.txt"), ["port 80", "Port=1"])
        self.assertEqual(_t(s, "grep 'a\\|port' p.txt"), ["a.b", "axb", "port 80"])
        self.assertEqual(_t(s, "grep -A 1 axb p.txt"), ["axb", "port 80"])
        self.assertEqual(_t(s, "grep -c a f.txt p.txt"), ["f.txt:0", "p.txt:2"])
        # /etc/shadow ist 640 root:shadow – wie im echten System meldet grep -r das
        self.assertEqual(_t(s, "grep -r port /etc"),
                         ["/etc/app.conf:port=8080", "grep: /etc/shadow: Permission denied"])

    def test_sort_und_wc(self):
        s = _lx(**{"/home/anna/n.txt": ["10", "9", "100", "9", "2"]})
        self.assertEqual(_t(s, "cat n.txt | sort -n"), ["2", "9", "9", "10", "100"])
        self.assertEqual(_t(s, "cat n.txt | sort -rnu"), ["100", "10", "9", "2"])
        self.assertEqual(_t(s, "cat n.txt | wc"), ["      5       5      13"])

    def test_platzhalter_und_tilde(self):
        s = _lx()
        self.assertEqual(_t(s, "ls d/*.txt"), ["d/a.txt"])
        self.assertEqual(_t(s, "cat ~/nix"), ["cat: /home/anna/nix: No such file or directory"])
        self.assertEqual(_t(s, "rm *.log"), ["rm: cannot remove '*.log': No such file or directory"])
        self.assertEqual(_t(s, "cat 'd/*.txt'"), ["cat: d/*.txt: No such file or directory"])

    def test_wurzel_rekursiv_haengt_nicht(self):
        s = _lx()
        s.eingabe("sudo -i")
        self.assertEqual(_t(s, "chmod -R 755 /"), [])  # lief vorher endlos

    def test_nano_speichern(self):
        s = _lx()
        a = s.eingabe("nano /tmp/notiz.txt")
        antwort = s.datei_speichern(a.editor["pfad"], "zeile1\n")
        self.assertEqual([z.text for z in antwort.zeilen], ["[ Wrote 1 line ]"])
        self.assertEqual(_t(s, "cat /tmp/notiz.txt | wc -l"), ["1"])
        self.assertEqual(s.fs.besitzer("/tmp/notiz.txt"), ("anna", "anna"))
        a = s.eingabe("sudo nano /etc/neu.conf")
        s.datei_speichern(a.editor["pfad"], "x")
        self.assertEqual(s.fs.besitzer("/etc/neu.conf"), ("root", "root"))

    def test_menschlich_grenzen(self):
        from n3xtbyt3.kern.dateisystem import menschlich
        self.assertEqual(menschlich(10239), "10K")
        self.assertEqual(menschlich(1048575), "1.0M")


class WindowsDateisystemTest(unittest.TestCase):
    def _s(self):
        from tests.test_kern_dateien import HOME
        sz, fehler = pruefe_daten(mini(zustand={"dienst": "Stopped", "pfad": HOME}, dateien={
            HOME + "\\Doc\\": None, HOME + "\\Documents\\": {"modus": "d-r---"},
            HOME + "\\Documents\\Sub\\tief.txt": "tief",
            HOME + "\\AppData\\": {"modus": "d--h--"},
            HOME + "\\liste.txt": {"inhalt": "abc", "zeit": "11/3/2026 14:05"},
            HOME + "\\Desktop\\": None}))
        self.assertEqual(fehler, [])
        from n3xtbyt3.kern.sitzung import Sitzung
        from n3xtbyt3.kern.szenario import lade_allgemein
        return Sitzung(sz, lade_allgemein("windows")), HOME

    def test_ordner_bleibt_und_move_behaelt_zeit(self):
        s, home = self._s()
        s.eingabe("rm Documents\\Sub\\tief.txt")
        self.assertEqual(s.eingabe("cd Documents\\Sub").zeilen, [])
        s.eingabe("cd " + home)
        s.eingabe("Move-Item liste.txt Desktop")
        self.assertEqual(s.aktiv.wfs.zeit(home + "\\Desktop\\liste.txt"), "11/3/2026 14:05")

    def test_move_item_aktueller_ordner(self):
        s, home = self._s()
        s.eingabe("cd Documents")
        s.eingabe("Move-Item ..\\Doc ..\\Archiv")
        self.assertEqual(s.prompt(), f"PS {home}\\Documents> ")

    def test_versteckt_nur_mit_force(self):
        s, _ = self._s()
        self.assertNotIn("AppData", "\n".join(_t(s, "Get-ChildItem")))
        self.assertIn("AppData", "\n".join(_t(s, "Get-ChildItem -Force")))

    def test_mkdir_mit_elternordnern_und_datei_vorhanden(self):
        s, home = self._s()
        s.eingabe("mkdir x\\y\\z")
        self.assertEqual(s.aktiv.wfs.art(home + "\\x\\y\\z"), "ordner")
        self.assertIn("already exists", _t(s, "mkdir liste.txt -Force")[0])
        self.assertEqual(s.aktiv.wfs.art(home + "\\liste.txt"), "datei")

    def test_copy_in_sich_selbst_und_get_content(self):
        s, _ = self._s()
        self.assertIn("in sich selbst", _t(s, "Copy-Item Documents Documents\\Sub -Recurse")[0])
        self.assertEqual(_t(s, "Get-Content liste.txt -TotalCount -1"), ["abc"])
        self.assertEqual(_t(s, "Get-Content *.txt"), ["abc"])


class EditorTest(unittest.TestCase):
    def test_spalte_bleibt_beim_hoch_runter(self):
        from n3xtbyt3.kern.editor import EditorPuffer
        p = EditorPuffer("/x", "lange zeile hier\nkurz\nnoch eine lange zeile")
        p.zeilenende()
        p.runter()
        p.runter()
        self.assertEqual((p.zeile, p.spalte), (2, 16))

    def test_leeren_puffer_ausschneiden_aendert_nichts(self):
        from n3xtbyt3.kern.editor import EditorPuffer
        p = EditorPuffer("/y", "")
        p.zeile_ausschneiden()
        self.assertFalse(p.geaendert)


class MusterZuordnungTest(unittest.TestCase):
    def test_platzhalter_nimmt_keine_option_weg(self):
        from n3xtbyt3.kern.befehle import Vergleicher
        from n3xtbyt3.kern.systeme import SYSTEME
        v = Vergleicher(SYSTEME["windows"])
        self.assertTrue(v.passt(v.vorbereiten("cmd -a * -a x"), v.vorbereiten("cmd -a x -a y")))
        self.assertTrue(v.passt(v.vorbereiten("cmd -a x -a *"), v.vorbereiten("cmd -a y -a x")))
        self.assertFalse(v.passt(v.vorbereiten("cmd -a x -a x"), v.vorbereiten("cmd -a x -a y")))
