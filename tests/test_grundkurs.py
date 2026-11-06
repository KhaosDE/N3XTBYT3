"""Tests für den Grundkurs: Laden, Ablauf einer Lektion, Tippfehler-Hinweise, Fortschritt."""

import copy
import unittest

from n3xtbyt3.kern import grundkurs as gk
from n3xtbyt3.kern.befehle import Vergleicher
from n3xtbyt3.kern.spielstand import Spielstand, erster_start
from n3xtbyt3.kern.systeme import REIHENFOLGE, SYSTEME
from n3xtbyt3.kern.szenario import lade_allgemein

from tests.hilfen import Datenordner

MINI = {
    "id": "gk-test",
    "system": "windows",
    "titel": "Testlektion",
    "pruefstatus": "ungeprueft",
    "quelle": "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/hostname",
    "datum": "2026-11-05",
    "zustand": {"pfad": "C:\\Users\\mberger", "x": 0},
    "dateien": {"C:\\Users\\mberger\\Documents\\": {}},
    "erklaeren": "Ein Absatz.",
    "begriffe": {"Prompt": "Text vor dem Cursor."},
    "befehle": [{"muster": ["Set-Zahl"], "faelle": [{"setze": {"x": 1}}]}],
    "mitmachen": [
        {"text": "Tippe hostname", "eingabe": "hostname", "danach": "Das ist der Name."},
        {"text": "Geh in Documents", "eingabe": ["cd Documents"], "ziel": {"pfad": "C:\\Users\\mberger\\Documents"},
         "danach": "Gewechselt."},
    ],
    "aufgaben": [
        {"aufgabe": "Setz die Zahl.", "ziel": {"x": 1}, "hinweise": ["a", "b", "c"], "loesung": ["Set-Zahl"],
         "danach": "Gut."},
        {"aufgabe": "Zeig den Ordner an, aber in Documents.", "eingabe": ["Get-Location", "pwd"],
         "wenn": {"pfad": "C:\\Users\\mberger\\Documents"}, "hinweise": ["a", "b", "c"], "danach": "Prima."},
    ],
    "fertig": ["Du kannst es."],
}


def lektion(**aenderung):
    roh = copy.deepcopy(MINI)
    roh.update(aenderung)
    l, fehler = gk.pruefe_lektion(roh, 1)
    return l, fehler


class LadenTest(unittest.TestCase):
    def test_mini_laedt(self):
        l, fehler = lektion()
        self.assertEqual(fehler, [])
        self.assertEqual(l.befehle_gelernt, ["hostname", "cd Documents", "Get-Location"])

    def test_fehler_werden_gesammelt(self):
        _, fehler = lektion(mitmachen=[{"text": "x", "danach": "y"}], aufgaben=[{"aufgabe": "z", "eingabe": "a"}])
        text = " ".join(fehler)
        self.assertIn("Beim Mitmachen muss feststehen", text)
        self.assertIn("hinweise", text)
        self.assertIn("danach", text)
        _, fehler = lektion(aufgaben=[{"aufgabe": "z", "ziel": {"gibtsnicht": 1}, "hinweise": ["a", "b", "c"],
                                       "danach": "d"}])
        self.assertTrue(any("gibtsnicht" in f for f in fehler))
        _, fehler = lektion(szenario="gibt-es-nicht")
        self.assertTrue(any("kein Szenario" in f for f in fehler))

    def test_alle_kurse_laden(self):
        for sid in REIHENFOLGE:
            kurs = gk.lade_kurs(sid)
            with self.subTest(system=sid):
                self.assertEqual([str(f) for f in kurs.fehler], [])
                nummern = [l.nr for l in kurs.lektionen]
                self.assertEqual(nummern, list(range(1, len(nummern) + 1)), "Lektionen lückenlos nummeriert")

    def test_ids_eindeutig_und_voraussetzungen(self):
        kurse = gk.alle_kurse()
        ids = [l.id for k in kurse.values() for l in k.lektionen]
        self.assertEqual(len(ids), len(set(ids)))
        for k in kurse.values():
            for l in k.lektionen:
                if l.voraussetzung:
                    self.assertIsNotNone(gk.finde_lektion(kurse, l.voraussetzung), l.id)


class AblaufTest(unittest.TestCase):
    def setUp(self):
        l, _ = lektion()
        self.lauf = gk.Lektionslauf(l, lade_allgemein("windows"))

    def test_mitmachen_mit_tippfehler(self):
        a = self.lauf.eingabe("hostnme")
        self.assertFalse(a.geschafft)
        self.assertIn("Fast!", a.tipp)
        self.assertIn("hostname", a.tipp)
        a = self.lauf.eingabe("HOSTNAME")
        self.assertTrue(a.geschafft)
        self.assertEqual(a.erklaerung, "Das ist der Name.")
        self.assertEqual(self.lauf.index, 1)

    def test_ziel_reicht_auch_anders_geschrieben(self):
        self.lauf.eingabe("hostname")
        a = self.lauf.eingabe("Set-Location .\\documents")
        self.assertTrue(a.geschafft)
        self.assertEqual(a.teil_neu, "aufgaben")

    def test_aufgaben_hinweise_und_wenn(self):
        self.lauf.eingabe("hostname")
        self.lauf.eingabe("cd Documents")
        self.assertEqual(self.lauf.naechster_hinweis(), "a")
        self.assertEqual(self.lauf.naechster_hinweis(), "b")
        tipp = self.lauf.eingabe("hostname").tipp  # bei Aufgaben: Rückmeldung, aber kein Vorsagen
        self.assertIn("noch nicht", tipp)
        self.assertNotIn("Set-Zahl", tipp)
        self.assertTrue(self.lauf.eingabe("Set-Zahl").geschafft)
        self.assertEqual(self.lauf.hinweis_stufe, 0)
        self.lauf.eingabe("cd ..")
        a = self.lauf.eingabe("pwd")  # falscher Ordner
        self.assertFalse(a.geschafft)
        self.assertIn("richtigen Ort", a.tipp)
        self.lauf.eingabe("cd Documents")
        a = self.lauf.eingabe("pwd")
        self.assertTrue(a.geschafft)
        self.assertEqual(a.teil_neu, "fertig")
        self.assertTrue(self.lauf.fertig)
        self.assertEqual(self.lauf.ergebnis()["hinweise"], 2)

    def test_kein_geloest_aus_der_sitzung(self):
        a = self.lauf.eingabe("hostname")
        self.assertFalse(a.antwort.geloest_jetzt)


class TippTest(unittest.TestCase):
    def test_tipps(self):
        w = Vergleicher(SYSTEME["windows"])
        lx = Vergleicher(SYSTEME["linux"])
        self.assertIn("Leerzeichen", gk.tipp("cd..", "cd ..", lx))
        self.assertIn("Groß- und Kleinschreibung", gk.tipp("LS -L", "ls -l", lx))
        self.assertIn("Fast!", gk.tipp("Get-Locaton", "Get-Location", w))
        self.assertIn("anderer Befehl", gk.tipp("whoami", "Get-Location", w))


class FortschrittTest(unittest.TestCase):
    def test_spielstand(self):
        with Datenordner():
            self.assertTrue(erster_start())
            stand = Spielstand.lade("windows")
            self.assertFalse(stand.lektion("gk-win-konsole")["fertig"])
            self.assertFalse(stand.lektion_eintragen("gk-win-konsole", {"fertig": False, "befehle": 0}))
            self.assertTrue(stand.lektion_eintragen("gk-win-konsole", {"fertig": True, "befehle": 5, "hinweise": 1}))
            stand.speichere()
            self.assertFalse(erster_start())
            stand = Spielstand.lade("windows")
            self.assertTrue(stand.lektion("gk-win-konsole")["fertig"])
            # einmal fertig bleibt fertig
            stand.lektion_eintragen("gk-win-konsole", {"fertig": False, "befehle": 3})
            self.assertTrue(stand.lektion("gk-win-konsole")["fertig"])
            kurs = gk.lade_kurs("windows")
            fertig, offen = gk.fortschritt(stand, kurs.lektionen)
            self.assertEqual(fertig, 1)
            self.assertEqual(offen.nr, 2)


class AlleLektionenSpielbarTest(unittest.TestCase):
    """Jede Lektion lässt sich mit den Vorgaben und Lösungen von Anfang bis Ende durchspielen."""

    def test_durchspielen(self):
        for sid in REIHENFOLGE:
            allgemein = lade_allgemein(sid)
            for l in gk.lade_kurs(sid).lektionen:
                with self.subTest(lektion=l.id):
                    lauf = gk.Lektionslauf(l, allgemein)
                    for nr, schritt in enumerate(l.mitmachen, start=1):
                        a = lauf.eingabe(schritt.eingabe[0])
                        self.assertEqual(a.antwort.art, "treffer",
                                         f"Mitmachen {nr}: „{schritt.eingabe[0]}“ läuft so nicht")
                        self.assertTrue(a.geschafft, f"Mitmachen {nr}: „{schritt.eingabe[0]}“ erfüllt den Schritt nicht")
                    for nr, aufgabe in enumerate(l.aufgaben, start=1):
                        ergebnisse = [lauf.loesungsschritt(s) for s in aufgabe.loesung]
                        for s, a in zip(aufgabe.loesung, ergebnisse):
                            self.assertEqual(a.antwort.art, "treffer", f"Aufgabe {nr}: „{s}“ läuft so nicht")
                        self.assertTrue(ergebnisse[-1].geschafft, f"Aufgabe {nr} wird mit der Lösung nicht geschafft")
                    self.assertTrue(lauf.fertig)


class RueckmeldungTest(unittest.TestCase):
    """Fehler von Tobi (06.11.2026): Nach whoami ging es nicht weiter – und es kam keine Erklärung."""

    def _lauf(self, lektion_id):
        l = next(x for x in gk.lade_kurs("windows").lektionen if x.id == lektion_id)
        return l, gk.Lektionslauf(l, lade_allgemein("windows"))

    def test_wiederholungsschritt_erklaert_den_pfeil(self):
        l, lauf = self._lauf("gk-win-konsole")
        lauf.eingabe("hostname")
        lauf.eingabe("whoami")
        a = lauf.eingabe("whoami")  # nur einmal ↑ gedrückt
        self.assertFalse(a.geschafft)
        self.assertIn("„whoami“", a.tipp)
        self.assertIn("↑ noch einmal", a.tipp)
        self.assertTrue(lauf.eingabe("hostname").geschafft)

    def test_selbst_probieren_gibt_immer_rueckmeldung(self):
        l, lauf = self._lauf("gk-win-konsole")
        for s in l.mitmachen:
            lauf.eingabe(s.eingabe[0])
        a = lauf.eingabe("whoami")  # Aufgabe 1 fragt nach dem Computernamen
        self.assertFalse(a.geschafft)
        self.assertIn("Das löst Aufgabe 1 noch nicht", a.tipp)
        self.assertIsNone(lauf.eingabe("Get-Kaffeee").tipp)  # unbekannt: die blaue Meldung erklärt es schon
        self.assertTrue(lauf.eingabe("hostname").geschafft)
        self.assertIsNone(lauf.letzter_tipp)

    def test_erster_teilschritt_wird_gelobt(self):
        l, lauf = self._lauf("gk-win-ordner")
        for s in l.mitmachen:
            lauf.eingabe(s.eingabe[0])
        a = lauf.eingabe("cd Downloads")  # Aufgabe 1: wechseln und anzeigen
        self.assertIn("Guter erster Schritt", a.tipp)
        self.assertTrue(lauf.eingabe("dir").geschafft)


if __name__ == "__main__":
    unittest.main()
