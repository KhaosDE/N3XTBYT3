import unittest

from n3xtbyt3.kern.dateisystem import menschlich, oktal_zu_rechte, rechte_zu_oktal
from n3xtbyt3.kern.editor import EditorPuffer
from n3xtbyt3.kern.sitzung import ERFOLG, FEHLER, SIM, Sitzung
from n3xtbyt3.kern.szenario import lade_allgemein, pruefe_daten

from .hilfen import mini


def linux_szenario(**extra):
    daten = mini(
        system="linux", id="test-linux",
        zustand={"dienst": "inactive"},
        dateien={
            "/etc/app.conf": {"inhalt": ["port=8080", "debug=true"], "rechte": "644", "besitzer": "root:root"},
            "/var/log/app.log": ["INFO start", "ERROR disk full", "INFO stop", "ERROR again"],
            "/home/anna/skript.sh": {"inhalt": "#!/bin/bash\necho hallo", "rechte": "rw-r--r--",
                                     "besitzer": "anna:anna"},
            "/home/anna/projekte/": {},
            "/root/geheim.txt": {"inhalt": "x", "rechte": "600"},
            "/etc/neu.conf": None,
        },
        befehle=[
            {"muster": ["systemctl start app"], "faelle": [
                {"wenn": {"root": False}, "sim": True, "ausgabe": "Nur mit sudo."},
                {"setze": {"dienst": "active"}}]},
            {"muster": ["journalctl -u app"], "faelle": [{"ausgabe": ["a ok", "b error", "c ok"]}]},
        ],
        ziel={"dienst": "active"},
        loesung=["sudo systemctl start app"],
    )
    daten.update(extra)
    szenario, fehler = pruefe_daten(daten)
    assert not fehler, fehler
    return szenario


def sitzung(**extra):
    sz = linux_szenario(**extra)
    return Sitzung(sz, lade_allgemein("linux"))


def text(antwort):
    return [z.text for z in antwort.zeilen]


class HilfsfunktionenTest(unittest.TestCase):
    def test_rechte(self):
        self.assertEqual(oktal_zu_rechte("755"), "rwxr-xr-x")
        self.assertEqual(oktal_zu_rechte("0640"), "rw-r-----")
        self.assertEqual(rechte_zu_oktal("rw-r--r--"), "644")

    def test_menschlich(self):
        self.assertEqual(menschlich(220), "220")
        self.assertEqual(menschlich(4096), "4.0K")
        self.assertEqual(menschlich(12345), "13K")
        self.assertEqual(menschlich(1572864), "1.5M")

    def test_dateien_pruefung(self):
        daten = mini(system="linux", dateien={"etc/x": "a"}, loesung=["Start-Service Testdienst"])
        _, fehler = pruefe_daten(daten)
        self.assertTrue(any("Pfade beginnen" in f for f in fehler))
        _, fehler = pruefe_daten(mini(dateien={"/x": "a"}))
        self.assertTrue(any("nur bei Linux" in f for f in fehler))


class DateisystemTest(unittest.TestCase):
    def test_prompt_und_cd(self):
        s = sitzung()
        self.assertEqual(s.prompt(), "anna@pc-lager02:~$ ")
        self.assertEqual(text(s.eingabe("pwd")), ["/home/anna"])
        s.eingabe("cd /var/log")
        self.assertEqual(s.prompt(), "anna@pc-lager02:/var/log$ ")
        s.eingabe("cd ..")
        self.assertEqual(text(s.eingabe("pwd")), ["/var"])
        a = s.eingabe("cd /gibtsnicht")
        self.assertEqual(text(a), ["bash: cd: /gibtsnicht: No such file or directory"])
        self.assertEqual(a.zeilen[0].art, FEHLER)
        s.eingabe("cd")
        self.assertEqual(s.prompt(), "anna@pc-lager02:~$ ")
        s.eingabe("cd projekte")
        self.assertEqual(s.prompt(), "anna@pc-lager02:~/projekte$ ")

    def test_ls(self):
        s = sitzung()
        self.assertEqual(text(s.eingabe("ls /etc")), ["app.conf  hostname  os-release  shadow"])
        self.assertIn(".bashrc", text(s.eingabe("ls -a"))[0])
        zeilen = text(s.eingabe("ls -l /etc"))
        self.assertTrue(zeilen[0].startswith("total "))
        self.assertTrue(any(z.startswith("-rw-r--r-- 1 root root") and z.endswith(" app.conf") for z in zeilen))
        self.assertTrue(any(z.startswith("-rw-r----- 1 root shadow") for z in zeilen))
        self.assertEqual(text(s.eingabe("ls /nix")), ["ls: cannot access '/nix': No such file or directory"])
        eine = text(s.eingabe("ls -l skript.sh"))
        self.assertEqual(len(eine), 1)
        self.assertIn("anna anna", eine[0])

    def test_cat_rechte(self):
        s = sitzung()
        self.assertEqual(text(s.eingabe("cat /etc/app.conf")), ["port=8080", "debug=true"])
        self.assertEqual(text(s.eingabe("cat /etc/shadow")), ["cat: /etc/shadow: Permission denied"])
        self.assertEqual(text(s.eingabe("cat /etc")), ["cat: /etc: Is a directory"])
        self.assertEqual(text(s.eingabe("cat /etc/neu.conf")), ["cat: /etc/neu.conf: No such file or directory"])
        self.assertEqual(text(s.eingabe("sudo cat /etc/shadow"))[0], "[sudo] password for anna: ")

    def test_grep_head_tail(self):
        s = sitzung()
        self.assertEqual(text(s.eingabe("grep ERROR /var/log/app.log")), ["ERROR disk full", "ERROR again"])
        self.assertEqual(text(s.eingabe("grep -n -i error /var/log/app.log")), ["2:ERROR disk full", "4:ERROR again"])
        self.assertEqual(text(s.eingabe("tail -n 1 /var/log/app.log")), ["ERROR again"])
        self.assertEqual(text(s.eingabe("head -2 /var/log/app.log")), ["INFO start", "ERROR disk full"])

    def test_pipes(self):
        s = sitzung()
        self.assertEqual(text(s.eingabe("journalctl -u app | grep error")), ["b error"])
        self.assertEqual(text(s.eingabe("cat /var/log/app.log | grep -c ERROR")), ["2"])
        self.assertEqual(text(s.eingabe("cat /var/log/app.log | wc -l")), ["4"])
        a = s.eingabe("cat /var/log/app.log | awk '{print $1}'")
        self.assertEqual(a.art, "nicht_erkannt")
        self.assertIn("hinter einer Pipe", a.zeilen[0].text)

    def test_chmod_chown(self):
        s = sitzung()
        s.eingabe("chmod u+x skript.sh")
        self.assertEqual(s.fs.rechte("/home/anna/skript.sh"), "rwxr--r--")
        s.eingabe("chmod 750 skript.sh")
        self.assertEqual(s.fs.rechte("/home/anna/skript.sh"), "rwxr-x---")
        a = s.eingabe("chmod 777 /etc/app.conf")
        self.assertIn("Operation not permitted", text(a)[0])
        a = s.eingabe("chown anna /etc/app.conf")
        self.assertIn("Operation not permitted", text(a)[0])
        s.eingabe("sudo chown anna:anna /etc/app.conf")
        self.assertEqual(s.fs.besitzer("/etc/app.conf"), ("anna", "anna"))

    def test_sudo_und_root_shell(self):
        s = sitzung()
        a = s.eingabe("systemctl start app")
        self.assertEqual(a.zeilen[0].art, SIM)
        a = s.eingabe("sudo systemctl start app")
        self.assertTrue(a.geloest_jetzt)
        self.assertFalse(s.zustand.get("root"))
        s2 = sitzung()
        s2.eingabe("sudo -i")
        self.assertEqual(s2.prompt(), "root@pc-lager02:~# ")
        self.assertEqual(text(s2.eingabe("pwd")), ["/root"])
        self.assertEqual(text(s2.eingabe("whoami")), ["root"])
        s2.eingabe("exit")
        self.assertEqual(s2.prompt(), "anna@pc-lager02:~$ ")

    def test_sudo_verboten(self):
        sz = linux_szenario(zustand={"dienst": "inactive", "sudo_erlaubt": False})
        s = Sitzung(sz, lade_allgemein("linux"))
        a = s.eingabe("sudo systemctl start app")
        self.assertIn("keine sudo-Rechte", a.zeilen[0].text)
        self.assertFalse(s.geloest)

    def test_editor_und_ziel_ueber_datei(self):
        daten = dict(ziel={"datei:/etc/app.conf": {"enthaelt": "debug=false"}}, loesung=["nano /etc/app.conf"])
        s = sitzung(**daten)
        a = s.eingabe("nano /etc/app.conf")
        self.assertEqual(a.aktion, "editor")
        self.assertTrue(a.editor["nur_lesen"])
        a = s.eingabe("sudo nano /etc/app.conf")
        self.assertFalse(a.editor["nur_lesen"])
        puffer = EditorPuffer(**{k: a.editor[k] for k in ("pfad", "inhalt", "nur_lesen", "neu")})
        puffer.runter()
        puffer.zeilenende()
        for _ in "true":
            puffer.rueckschritt()
        puffer.einfuegen("false")
        antwort = s.datei_speichern(puffer.pfad, puffer.text)
        self.assertEqual(antwort.zeilen[0].text, "[ Wrote 2 lines ]")
        self.assertTrue(antwort.geloest_jetzt)
        self.assertTrue(any(z.art == ERFOLG for z in antwort.zeilen))
        self.assertEqual(text(s.eingabe("cat /etc/app.conf")), ["port=8080", "debug=false"])

    def test_neue_datei_im_editor(self):
        s = sitzung()
        a = s.eingabe("sudo nano /etc/neu.conf")
        self.assertTrue(a.editor["neu"])
        s.datei_speichern("/etc/neu.conf", "a=1")
        self.assertIn("neu.conf", text(s.eingabe("ls /etc"))[0])

    def test_gross_klein(self):
        s = sitzung()
        a = s.eingabe("LS")
        self.assertIn("Meintest du „ls“", "\n".join(text(a)))


class EditorTest(unittest.TestCase):
    def test_bearbeiten(self):
        p = EditorPuffer("/x", "ab\ncd")
        p.zeilenende()
        p.neue_zeile()
        p.einfuegen("neu")
        self.assertEqual(p.text, "ab\nneu\ncd")
        p.zeilenanfang()
        p.rueckschritt()
        self.assertEqual(p.text, "abneu\ncd")
        p.entfernen()
        self.assertEqual(p.text, "abeu\ncd")
        p.zeile_ausschneiden()
        self.assertEqual(p.text, "cd")
        self.assertTrue(p.geaendert)

    def test_nur_lesen(self):
        p = EditorPuffer("/x", "ab", nur_lesen=True)
        p.einfuegen("x")
        p.rueckschritt()
        self.assertEqual(p.text, "ab")
        self.assertFalse(p.geaendert)


if __name__ == "__main__":
    unittest.main()
