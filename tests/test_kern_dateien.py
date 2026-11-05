"""Tests für die Windows-Dateibefehle (PowerShell) und die Linux-Ergänzungen mkdir/touch/cp/mv/rm."""

import unittest

from n3xtbyt3.kern.sitzung import Sitzung
from n3xtbyt3.kern.szenario import lade_allgemein, pruefe_daten

from tests.hilfen import mini

HOME = "C:\\Users\\mberger"


def win_sitzung(**extra):
    daten = mini(
        zustand={"dienst": "Stopped", "pfad": HOME},
        dateien={
            HOME + "\\Documents\\": {"modus": "d-r---"},
            HOME + "\\Documents\\notiz.txt": ["Zeile 1", "Zeile 2", "Zeile 3"],
            HOME + "\\Desktop\\": None,
            HOME + "\\liste.txt": {"inhalt": "abc", "zeit": "11/3/2026 14:05"},
        },
        **extra,
    )
    sz, fehler = pruefe_daten(daten)
    assert not fehler, fehler
    return Sitzung(sz, lade_allgemein("windows"))


def texte(antwort):
    return [z.text for z in antwort.zeilen]


class WindowsDateienTest(unittest.TestCase):
    def test_get_location_und_prompt(self):
        s = win_sitzung()
        self.assertEqual(s.prompt(), f"PS {HOME}> ")
        self.assertEqual(texte(s.eingabe("Get-Location")), ["", "Path", "----", HOME, ""])
        self.assertEqual(texte(s.eingabe("pwd")), ["", "Path", "----", HOME, ""])

    def test_cd_relativ_absolut_und_hoch(self):
        s = win_sitzung()
        s.eingabe("cd documents")
        self.assertEqual(s.prompt(), f"PS {HOME}\\Documents> ")  # Schreibweise aus den Daten
        s.eingabe("cd ..")
        self.assertEqual(s.prompt(), f"PS {HOME}> ")
        s.eingabe("Set-Location C:\\Users")
        self.assertEqual(s.prompt(), "PS C:\\Users> ")
        s.eingabe("cd ~")
        self.assertEqual(s.prompt(), f"PS {HOME}> ")
        s.eingabe("cd..")
        self.assertEqual(s.prompt(), "PS C:\\Users> ")
        s.eingabe("cd \\")
        self.assertEqual(s.prompt(), "PS C:\\> ")

    def test_cd_gibt_es_nicht(self):
        s = win_sitzung()
        a = s.eingabe("cd Bilder")
        self.assertEqual(texte(a), [f"cd : Cannot find path '{HOME}\\Bilder' because it does not exist."])
        self.assertEqual(a.zeilen[0].art, "fehler")
        self.assertEqual(s.prompt(), f"PS {HOME}> ")

    def test_get_childitem_wie_in_der_doku(self):
        s = win_sitzung()
        zeilen = texte(s.eingabe("Get-ChildItem"))
        self.assertEqual(zeilen[:5], ["", f"    Directory: {HOME}", "",
                                      "Mode                LastWriteTime         Length Name",
                                      "----                -------------         ------ ----"])
        # Ordner zuerst, dann Dateien – Spalten wie im Beispiel auf learn.microsoft.com
        self.assertEqual(zeilen[5], "d-----        11/4/2026     09:12                Desktop")
        self.assertEqual(zeilen[6], "d-r---        11/4/2026     09:12                Documents")
        self.assertEqual(zeilen[7], "-a----        11/3/2026     14:05              3 liste.txt")
        self.assertEqual(zeilen[-1], "")
        self.assertEqual(texte(s.eingabe("dir")), zeilen)
        self.assertEqual(texte(s.eingabe("ls -Name")), ["Desktop", "Documents", "liste.txt"])
        self.assertEqual(texte(s.eingabe("gci *.txt -Name")), ["liste.txt"])

    def test_get_content(self):
        s = win_sitzung()
        self.assertEqual(texte(s.eingabe("Get-Content .\\Documents\\notiz.txt")), ["Zeile 1", "Zeile 2", "Zeile 3"])
        self.assertEqual(texte(s.eingabe("type Documents\\notiz.txt -Tail 1")), ["Zeile 3"])
        a = s.eingabe("cat fehlt.txt")
        self.assertIn("Cannot find path", a.zeilen[0].text)

    def test_neu_kopieren_verschieben_loeschen(self):
        s = win_sitzung()
        a = s.eingabe("New-Item -Name Projekt -ItemType Directory")
        self.assertIn("Projekt", texte(a)[-2])
        self.assertTrue(texte(a)[-2].startswith("d-----"))
        s.eingabe("New-Item -Path .\\Projekt -Name plan.txt -ItemType File -Value \"Montag\"")
        self.assertEqual(texte(s.eingabe("Get-Content Projekt\\plan.txt")), ["Montag"])
        self.assertIn("already exists", texte(s.eingabe("mkdir Projekt"))[0])
        s.eingabe("Copy-Item liste.txt Projekt")
        self.assertEqual(texte(s.eingabe("Get-Content Projekt\\liste.txt")), ["abc"])
        s.eingabe("Move-Item Projekt\\plan.txt Projekt\\wochenplan.txt")
        self.assertEqual(texte(s.eingabe("Get-ChildItem Projekt -Name")), ["liste.txt", "wochenplan.txt"])
        # Nicht leerer Ordner ohne -Recurse: die echte PowerShell fragt nach – hier wird nichts gelöscht
        a = s.eingabe("Remove-Item Projekt")
        self.assertEqual(a.zeilen[0].art, "sim")
        self.assertEqual(s.aktiv.wfs.art(HOME + "\\Projekt"), "ordner")
        s.eingabe("Remove-Item Projekt -Recurse")
        self.assertIsNone(s.aktiv.wfs.art(HOME + "\\Projekt"))
        s.eingabe("del liste.txt")
        self.assertEqual(texte(s.eingabe("ls -Name")), ["Desktop", "Documents"])

    def test_cmd_und_unbekannte_parameter(self):
        s = win_sitzung()
        a = s.eingabe("Get-ChildItem -Recurse")
        self.assertEqual(a.zeilen[0].art, "sim")  # nie eine erfundene Fehlermeldung
        s.eingabe("cmd")
        a = s.eingabe("dir")
        self.assertEqual(a.art, "nicht_erkannt")
        self.assertIn("powershell", a.zeilen[0].text)

    def test_ohne_dateien_keine_dateibefehle(self):
        sz, _ = pruefe_daten(mini())
        s = Sitzung(sz, lade_allgemein("windows"))
        self.assertIsNone(s.aktiv.wfs)
        self.assertEqual(s.eingabe("Get-ChildItem").art, "unbekannt")

    def test_dateien_pruefung(self):
        _, fehler = pruefe_daten(mini(dateien={"C:\\x\\": {"modus": "-a----"}}))
        self.assertTrue(any("modus" in f for f in fehler))
        _, fehler = pruefe_daten(mini(dateien={"C:\\x.txt": {"zeit": "gestern"}}))
        self.assertTrue(any("zeit" in f for f in fehler))


def linux_sitzung():
    daten = mini(system="linux", zustand={"x": 1}, befehle=[], ziel={"x": 2}, loesung=["pwd"],
                 dateien={"/home/anna/a.txt": "Hallo", "/home/anna/Ordner/b.txt": "B",
                          "/etc/geheim.conf": {"inhalt": "x", "rechte": "644"}})
    sz, fehler = pruefe_daten(daten)
    assert not fehler, fehler
    return Sitzung(sz, lade_allgemein("linux"))


class LinuxDateienTest(unittest.TestCase):
    def test_mkdir_touch(self):
        s = linux_sitzung()
        self.assertEqual(texte(s.eingabe("mkdir neu")), [])
        self.assertTrue(s.fs.ist_verzeichnis("/home/anna/neu"))
        self.assertEqual(s.fs.rechte("/home/anna/neu"), "rwxrwxr-x")
        self.assertEqual(texte(s.eingabe("mkdir neu")), ["mkdir: cannot create directory 'neu': File exists"])
        self.assertIn("No such file", texte(s.eingabe("mkdir x/y"))[0])
        s.eingabe("mkdir -p x/y")
        self.assertTrue(s.fs.ist_verzeichnis("/home/anna/x/y"))
        s.eingabe("touch neu/leer.txt")
        self.assertTrue(s.fs.ist_datei("/home/anna/neu/leer.txt"))
        self.assertEqual(s.fs.besitzer("/home/anna/neu/leer.txt"), ("anna", "anna"))
        self.assertIn("Permission denied", texte(s.eingabe("touch /etc/neu.conf"))[0])

    def test_cp_mv_rm(self):
        s = linux_sitzung()
        s.eingabe("cp a.txt kopie.txt")
        self.assertEqual(s.fs.inhalt("/home/anna/kopie.txt"), "Hallo")
        self.assertEqual(texte(s.eingabe("cp Ordner O2")), ["cp: -r not specified; omitting directory 'Ordner'"])
        s.eingabe("cp -r Ordner O2")
        self.assertEqual(s.fs.inhalt("/home/anna/O2/b.txt"), "B")
        s.eingabe("mv kopie.txt Ordner")
        self.assertTrue(s.fs.ist_datei("/home/anna/Ordner/kopie.txt"))
        self.assertFalse(s.fs.ist_datei("/home/anna/kopie.txt"))
        s.eingabe("mv Ordner Archiv")
        self.assertTrue(s.fs.ist_datei("/home/anna/Archiv/b.txt"))
        self.assertEqual(texte(s.eingabe("rm Archiv")), ["rm: cannot remove 'Archiv': Is a directory"])
        s.eingabe("rm -r Archiv")
        self.assertFalse(s.fs.existiert("/home/anna/Archiv"))
        self.assertIn("Permission denied", texte(s.eingabe("rm /etc/geheim.conf"))[0])
        s.eingabe("sudo rm /etc/geheim.conf")
        self.assertFalse(s.fs.ist_datei("/etc/geheim.conf"))
        self.assertEqual(texte(s.eingabe("rm fehlt")), ["rm: cannot remove 'fehlt': No such file or directory"])


if __name__ == "__main__":
    unittest.main()
