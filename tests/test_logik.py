"""Abnahme „Logikprüfung“ (IDEEN.md, freigegeben 07.11.2026).

Jeder erzeugte Tippfehler bekommt eine Meldung, die das falsche Wort nennt („Meintest du“ / „Fast!“) –
außer er ergibt im echten System einen gültigen anderen Befehl (dann die echte Ausgabe).
Echte Aliase der Windows PowerShell 5.1 und die Schreibweise mit/ohne -Name lösen die Schritte.
"""

import importlib.util
import unittest
from pathlib import Path

from n3xtbyt3.kern import grundkurs as gk
from n3xtbyt3.kern.befehle import Vergleicher, abstand, vorschlag
from n3xtbyt3.kern.sitzung import FEHLER, SIM, Sitzung
from n3xtbyt3.kern.systeme import SYSTEME
from n3xtbyt3.kern.szenario import lade_allgemein, lade_system

from tests.hilfen import Datenordner


def _werkzeug():
    pfad = Path(__file__).resolve().parent.parent / "werkzeuge" / "logikpruefung.py"
    spec = importlib.util.spec_from_file_location("logikpruefung", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _texte(antwort):
    return " ".join(z.text for z in antwort.zeilen)


def _szenario(system_id, szenario_id):
    sz = next(s for s in lade_system(system_id).szenarien if s.id == szenario_id)
    return Sitzung(sz, lade_allgemein(system_id))


class LogikpruefungTest(unittest.TestCase):
    """Das Prüfwerkzeug spielt jede Aufgabe mit eingebauten Tippfehlern, Aliasen und -Name durch."""

    @classmethod
    def setUpClass(cls):
        with Datenordner():
            cls.zaehlung, cls.funde = _werkzeug().pruefen()

    def test_jeder_tippfehler_nennt_das_falsche_wort(self):
        for art in ("gk allgemein", "gk nicht erkannt", "gk akzeptiert", "sz allgemein", "sz nicht erkannt"):
            self.assertEqual(self.zaehlung[art], 0, f"{art}: {self.funde}")
        self.assertGreater(self.zaehlung["gk erkannt"], 400)
        self.assertGreater(self.zaehlung["sz erkannt"], 500)

    def test_aliase_name_kleinschreibung_und_hinweise(self):
        for kategorie in ("Windows: echter Alias wird nicht angenommen",
                          "Windows: gleichwertige Schreibweise (mit/ohne -Name) abgelehnt",
                          "Windows: Kleinschreibung abgelehnt",
                          "Hinweis nennt Befehl, der die Aufgabe nicht löst",
                          "Ladefehler"):
            self.assertEqual(self.funde.get(kategorie, []), [], kategorie)


class TobisFallTest(unittest.TestCase):
    """Grundkurs Windows, Lektion 3, Aufgabe 2: „get-command *-prcoess“."""

    def _lauf(self):
        lektion = next(l for l in gk.lade_kurs("windows").lektionen if l.id == "gk-win-hilfe")
        lauf = gk.Lektionslauf(lektion, lade_allgemein("windows"))
        for schritt in lektion.mitmachen:
            lauf.loesungsschritt(schritt.eingabe[0])
        self.assertTrue(lauf.eingabe("Get-Help Get-Process").geschafft)  # Aufgabe 1
        return lauf

    def test_tippfehler_wird_genannt(self):
        la = self._lauf().eingabe("get-command *-prcoess")
        self.assertFalse(la.geschafft)
        self.assertIn("„prcoess“", _texte(la.antwort))
        self.assertNotIn("nicht mit diesen Zusätzen", _texte(la.antwort) + (la.tipp or ""))

    def test_richtige_schreibweisen_loesen(self):
        for eingabe in ("Get-Command *-Process", "gcm *-Process", "get-command -name *-process",
                        "Get-Command *process*"):
            with self.subTest(eingabe=eingabe):
                self.assertTrue(self._lauf().eingabe(eingabe).geschafft)

    def test_platzhalter_vorn_und_hinten_erklaert(self):
        la = self._lauf().eingabe("Get-Command *process*")
        self.assertIn("Genauer sucht *-Process", _texte(la.antwort))


class TippfehlerTest(unittest.TestCase):
    def test_abstand_vertauscht_zaehlt_eins(self):
        self.assertEqual(abstand("pnig", "ping"), 1)
        self.assertEqual(abstand("prcoess", "process"), 1)
        self.assertEqual(abstand("Dokuente", "Dokumente"), 1)
        self.assertEqual(vorschlag("sduo", ["sudo", "su"]), "sudo")
        self.assertIsNone(vorschlag("xyz", ["ping"]))
        self.assertIsNone(vorschlag("ping", ["ping", "pong"]))  # gibt es genau so: kein Vorschlag

    def test_grenze_nach_laenge(self):
        self.assertIsNone(vorschlag("pnga", ["ping"]))       # 2 Fehler bei 4 Zeichen: zu viel
        self.assertEqual(vorschlag("Restrt-Servce", ["Restart-Service"]), "Restart-Service")

    def test_befehlsname(self):
        s = _szenario("windows", "win-dns-cache")
        self.assertIn("Meintest du „ping“", _texte(s.eingabe("pnig intranet.firma.internal")))
        s = _szenario("linux", "lin-paket-installieren")
        self.assertIn("Meintest du „sudo“", _texte(s.eingabe("sduo apt update")))
        self.assertIn("Meintest du „nano“", _texte(s.eingabe("sudo nnao /etc/hosts")))

    def test_argument_und_option(self):
        s = _szenario("windows", "tk-shop-502")
        self.assertIn("„Prot“", _texte(s.eingabe("Test-NetConnection shop.firma.internal -Prot 80")))
        self.assertIn("„niternal“", _texte(s.eingabe("Test-NetConnection shop.firma.niternal -Port 80")))
        self.assertIn("„rsv“", _texte(s.eingabe("ssh admin@rsv-web01")))

    def test_pfad_bleibt_echte_meldung_plus_vorschlag(self):
        s = _szenario("linux", "lin-skript-ausfuehrbar")
        a = s.eingabe("ls -l bacukp.sh")
        self.assertEqual(a.zeilen[0].art, FEHLER)
        self.assertIn("No such file or directory", a.zeilen[0].text)
        self.assertIn("Meintest du „backup.sh“", _texte(a))

    def test_filter_hinter_pipe(self):
        s = _szenario("linux", "lin-prozess-haengt")
        self.assertIn("Meintest du „head“", _texte(s.eingabe("ps aux | haed -5")))

    def test_chown_unbekannte_gruppe(self):
        s = _szenario("linux_server", "ls-worker-rechte")
        a = s.eingabe("sudo chown -R shop:hsop /var/lib/shop")
        self.assertIn("chown: invalid group: 'shop:hsop'", [z.text for z in a.zeilen])
        self.assertIn("Meintest du „shop“", _texte(a))
        self.assertNotEqual(s.fs.besitzer("/var/lib/shop")[1], "hsop")  # nichts geändert
        a = s.eingabe("sudo chown -R tobi:shop /var/lib/shop")
        self.assertIn("chown: invalid user: 'tobi:shop'", [z.text for z in a.zeilen])

    def test_keine_doppelte_meldung_im_grundkurs(self):
        lektion = next(l for l in gk.lade_kurs("windows").lektionen if l.id == "gk-win-konsole")
        lauf = gk.Lektionslauf(lektion, lade_allgemein("windows"))
        la = lauf.eingabe("hostnme")
        terminal = [z.text for z in la.antwort.zeilen if z.art == SIM] + ["[N3XTBYT3] " + la.tipp]
        self.assertEqual(sum("Meintest du" in z or "Fast!" in z for z in terminal), 1)


class AliasUndNameTest(unittest.TestCase):
    def setUp(self):
        self.v = Vergleicher(SYSTEME["windows"])

    def _passt(self, muster, eingabe, aliase=True):
        return self.v.passt(self.v.vorbereiten(muster), self.v.vorbereiten(eingabe), aliase)

    def test_aliase_der_powershell(self):
        for alias, voll in (("gsv Spooler", "Get-Service Spooler"), ("sasv Audiosrv", "Start-Service Audiosrv"),
                            ("spsv W32Time", "Stop-Service W32Time"), ("gps EXCEL", "Get-Process EXCEL"),
                            ("ps", "Get-Process"), ("kill 4711", "Stop-Process 4711"), ("gcm *-Service", "Get-Command *-Service"),
                            ("dir C:\\x", "Get-ChildItem C:\\x"), ("ls", "Get-ChildItem"), ("type a.txt", "Get-Content a.txt"),
                            ("del a.txt", "Remove-Item a.txt"), ("rd x", "Remove-Item x"), ("cls", "Clear-Host"),
                            ("help Get-Service", "Get-Help Get-Service")):
            with self.subTest(alias=alias):
                self.assertTrue(self._passt(voll, alias))
                self.assertTrue(self._passt(alias, voll))
                self.assertFalse(self._passt(voll, alias, aliase=False))

    def test_curl_ist_kein_alias_fuer_curl_exe(self):
        self.assertFalse(self._passt("curl.exe -I http://x", "Invoke-WebRequest -I http://x"))

    def test_mit_und_ohne_name(self):
        for kurz, lang in (("Get-Service Spooler", "Get-Service -Name Spooler"),
                           ("Restart-Service Spooler -Force", "Restart-Service -Force -Name Spooler"),
                           ("Get-Help Get-Service", "Get-Help -Name Get-Service"),
                           ("Get-Command *-Process", "Get-Command -Name *-Process")):
            with self.subTest(kurz=kurz):
                self.assertTrue(self._passt(kurz, lang, aliase=False))
        # Stop-Process: erster Positionsparameter ist -Id, nicht -Name
        self.assertFalse(self._passt("Stop-Process EXCEL", "Stop-Process -Name EXCEL", aliase=False))

    def test_aliase_nur_in_der_powershell(self):
        s = _szenario("windows", "win-druckwarteschlange")
        self.assertEqual(s.eingabe("gsv Spooler").art, "treffer")
        s.eingabe("cmd")
        self.assertNotEqual(s.eingabe("gsv Spooler").art, "treffer")

    def test_hilfe_der_simulation_bleibt(self):
        s = _szenario("windows", "win-dns-cache")
        self.assertIn("Hilfe der Simulation", _texte(s.eingabe("help")))
        self.assertNotIn("Hilfe der Simulation", _texte(s.eingabe("Get-Help")))


if __name__ == "__main__":
    unittest.main()
