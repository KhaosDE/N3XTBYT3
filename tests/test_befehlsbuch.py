"""Tests für Befehlsbuch und Lexikon."""

import unittest

from n3xtbyt3.kern import befehlsbuch as bb
from n3xtbyt3.kern import grundkurs as gk
from n3xtbyt3.kern.systeme import REIHENFOLGE
from n3xtbyt3.kern.szenario import lade_allgemein, lade_system


class BefehlsbuchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kurse = gk.alle_kurse()

    def _lauf(self, system_id, lektion_id):
        lektion = gk.finde_lektion(self.kurse, lektion_id)
        self.assertIsNotNone(lektion, f"Lektion „{lektion_id}“ gibt es nicht")
        return gk.Lektionslauf(lektion, lade_allgemein(lektion.system_id))

    def test_laedt_ohne_fehler(self):
        for sid in REIHENFOLGE:
            with self.subTest(system=sid):
                self.assertEqual(bb.lade(sid).fehler, [])

    def test_jedes_beispiel_funktioniert_in_der_simulation(self):
        """Nur Befehle, die in der Simulation wirklich gehen – geprüft in der genannten Lektion."""
        for sid in REIHENFOLGE:
            for e in bb.lade(sid).eintraege:
                for muster in e.muster:
                    with self.subTest(system=sid, befehl=muster):
                        lauf = self._lauf(sid, e.lektion)
                        for v in e.vorher:
                            self.assertEqual(lauf.eingabe(v).antwort.art, "treffer", f"vorher: {v}")
                        self.assertEqual(lauf.eingabe(muster).antwort.art, "treffer")

    def test_situationen(self):
        for sid in REIHENFOLGE:
            buch = bb.lade(sid)
            if not self.kurse[sid].lektionen:
                continue
            with self.subTest(system=sid):
                self.assertGreaterEqual(len(buch.situationen), 10, "mindestens 10 Situationen je System")
            for s in buch.situationen:
                with self.subTest(system=sid, wenn=s.wenn):
                    lauf = self._lauf(sid, s.lektion)
                    for befehl in [*s.vorher, *s.befehle]:
                        self.assertEqual(lauf.eingabe(befehl).antwort.art, "treffer", befehl)

    def test_suche(self):
        buch = bb.lade("windows")
        self.assertEqual([e.befehl for e in bb.suche_eintraege(buch, "dir")][:1], ["Get-ChildItem"])
        self.assertTrue(any("Programm" in s.wenn for s in bb.suche_situationen(buch, "reagiert")))
        self.assertEqual(len(bb.suche_eintraege(buch, "")), len(buch.eintraege))

    def test_pruefung_meldet_fehler(self):
        buch = bb.pruefe({"system": "windows", "befehle": [{"befehl": "x"}], "situationen": [{"wenn": "y"}]},
                         "windows")
        self.assertTrue(any("es fehlt" in f for f in buch.fehler))
        self.assertTrue(any("braucht" in f for f in buch.fehler))


class LexikonTest(unittest.TestCase):
    def test_sammeln_und_suchen(self):
        lektionen = gk.lade_kurs("windows").lektionen
        szenarien = lade_system("windows").szenarien
        begriffe = bb.lexikon(lektionen, szenarien)
        namen = [b.name for b in begriffe]
        self.assertEqual(namen, sorted(namen, key=str.casefold))
        self.assertEqual(len({n.casefold() for n in namen}), len(namen))
        prompt = next(b for b in begriffe if b.name == "Prompt")
        self.assertIn("Grundkurs, Lektion 1", prompt.vorkommen[0])
        dns = bb.suche_begriffe(begriffe, "dns")
        self.assertTrue(dns and "dns" in dns[0].name.casefold())


class GrundkursInTrainingUndAuswertungTest(unittest.TestCase):
    def test_karten_erst_nach_der_lektion(self):
        from n3xtbyt3.kern import auswertung, training
        from n3xtbyt3.kern.befehle import Vergleicher
        from n3xtbyt3.kern.spielstand import Spielstand
        from n3xtbyt3.kern.systeme import SYSTEME
        from tests.hilfen import Datenordner
        with Datenordner():
            buch = bb.lade("windows")
            lektionen = gk.lade_kurs("windows").lektionen
            stand = Spielstand.lade("windows")
            vorher = training.sammle_karten([], buch, stand, lektionen)
            self.assertEqual(vorher, [])
            stand.lektion_eintragen("gk-win-ordner", {"fertig": True, "befehle": 3})
            karten = training.sammle_karten([], buch, stand, lektionen)
            beispiele = {k.beispiel for k in karten}
            self.assertIn("Get-ChildItem", beispiele)
            karte = next(k for k in karten if k.beispiel == "Get-ChildItem")
            self.assertIn("Lektion 2", training.frage_text(karte))
            # Aliase gelten als richtig
            self.assertEqual(training.bewerte(karte, "dir", Vergleicher(SYSTEME["windows"])), "richtig")
            a = auswertung.erstelle("windows", [], stand, lektionen=lektionen, buch=buch)
            self.assertEqual(a["grundkurs"]["fertig"], 1)
            self.assertTrue(a["empfehlung"][0].startswith("Grundkurs weitermachen: Lektion 1"))
            self.assertIn("## Grundkurs", auswertung.als_markdown(a))
            self.assertIn("- [x] Lektion 2", auswertung.als_markdown(a))


if __name__ == "__main__":
    unittest.main()
