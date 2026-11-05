"""Rauchtest der Oberfläche ohne Bildschirm (SDL-Dummy-Treiber).

Wird übersprungen, wenn pygame-ce nicht installiert ist.
"""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

try:
    import pygame
except ImportError:  # pragma: no cover
    pygame = None

from .hilfen import Datenordner


def taste(k, mod=0):
    return pygame.event.Event(pygame.KEYDOWN, key=k, mod=mod, unicode="", scancode=0)


def tippe(text):
    return [pygame.event.Event(pygame.TEXTINPUT, text=c) for c in text] + [taste(pygame.K_RETURN)]


@unittest.skipIf(pygame is None, "pygame-ce nicht installiert")
class OberflaecheTest(unittest.TestCase):
    def setUp(self):
        self._daten = Datenordner()
        self.ordner = self._daten.__enter__()
        from n3xtbyt3.oberflaeche.app import App
        from n3xtbyt3.oberflaeche.grundkurs_ansicht import Willkommen
        self.app = App(groesse=(1280, 720))
        self.assertIsInstance(self.app.ansicht, Willkommen)  # erster Start: noch kein Spielstand
        self.app.schritt([taste(pygame.K_ESCAPE)], dt=0.05)  # → Hauptmenü

    def tearDown(self):
        self.app.ansicht.verlassen()
        pygame.quit()
        self._daten.__exit__(None, None, None)

    def test_durchlauf_menue_spiel_spielstand(self):
        from n3xtbyt3.kern.spielstand import Spielstand
        from n3xtbyt3.oberflaeche.menue import Hauptmenue, Szenarioliste
        from n3xtbyt3.oberflaeche.spiel import Spielansicht

        app = self.app
        app.schritt([], dt=0.05)
        self.assertIsInstance(app.ansicht, Hauptmenue)
        app.schritt([taste(pygame.K_RETURN)], dt=0.05)
        self.assertIsInstance(app.ansicht, Szenarioliste)
        self.assertEqual(app.ansicht.sonder[0][0], "grundkurs")  # Grundkurs zuerst, vorgewählt
        self.assertEqual(app.ansicht.auswahl, 0)
        app.schritt([taste(pygame.K_DOWN), taste(pygame.K_RETURN)], dt=0.05)  # Zufällig
        self.assertIsInstance(app.ansicht, Spielansicht)
        spiel = app.ansicht
        app.schritt([taste(pygame.K_F1)], dt=0.05)
        self.assertEqual(spiel.sitzung.hinweis_stufe, 1)
        for schritt in spiel.szenario.loesung:
            app.schritt(tippe(schritt), dt=0.05)
        self.assertTrue(spiel.sitzung.geloest)
        app.schritt([taste(pygame.K_ESCAPE)], dt=0.05)
        self.assertIsInstance(app.ansicht, Szenarioliste)
        stand = Spielstand.lade("windows")
        eintrag = stand.eintrag(spiel.szenario.id)
        self.assertTrue(eintrag["geloest"])
        self.assertEqual(eintrag["hinweise_max"], 1)

    def test_verlauf_und_schriftgroesse(self):
        app = self.app
        app.schritt([taste(pygame.K_RETURN)], dt=0.05)
        app.schritt([taste(pygame.K_DOWN), taste(pygame.K_RETURN)], dt=0.05)
        spiel = app.ansicht
        app.schritt(tippe("hostname"), dt=0.05)
        app.schritt([taste(pygame.K_UP)], dt=0.05)
        self.assertEqual(spiel.terminal.eingabe, "hostname")
        alt = app.schriften.groesse
        app.schritt([taste(pygame.K_PLUS, pygame.KMOD_CTRL)], dt=0.05)
        self.assertEqual(app.schriften.groesse, alt + 2)
        self.assertTrue(os.path.exists(os.path.join(self.ordner, "einstellungen.json")))

    def test_versuch_ohne_eingabe_zaehlt_nicht(self):
        from n3xtbyt3.kern.spielstand import Spielstand
        app = self.app
        app.schritt([taste(pygame.K_RETURN)], dt=0.05)
        app.schritt([taste(pygame.K_DOWN), taste(pygame.K_RETURN)], dt=0.05)
        app.schritt([taste(pygame.K_ESCAPE)], dt=0.05)
        self.assertEqual(Spielstand.lade("windows").daten["szenarien"], {})

    def test_training_und_auswertung(self):
        from n3xtbyt3.kern.spielstand import Spielstand
        from n3xtbyt3.oberflaeche.auswertung_ansicht import Auswertungsansicht
        from n3xtbyt3.oberflaeche.menue import Szenarioliste
        from n3xtbyt3.oberflaeche.training_ansicht import Trainingsansicht

        app = self.app
        app.schritt([taste(pygame.K_RETURN)], dt=0.05)
        app.schritt([taste(pygame.K_DOWN), taste(pygame.K_DOWN), taste(pygame.K_RETURN)], dt=0.05)
        self.assertIsInstance(app.ansicht, Trainingsansicht)
        training = app.ansicht
        karte = training.karte
        app.schritt(tippe(karte.beispiel), dt=0.05)
        self.assertEqual(training.zaehler["richtig"], 1)
        app.schritt([taste(pygame.K_F1)], dt=0.05)
        self.assertEqual(training.zaehler["falsch"], 1)
        app.schritt([taste(pygame.K_ESCAPE)], dt=0.05)
        self.assertIsInstance(app.ansicht, Szenarioliste)
        self.assertTrue(Spielstand.lade("windows").kartei.befehle)
        app.schritt([taste(pygame.K_DOWN)] * 3 + [taste(pygame.K_RETURN)], dt=0.05)
        self.assertIsInstance(app.ansicht, Auswertungsansicht)
        app.schritt([taste(pygame.K_PAGEDOWN)], dt=0.05)
        self.assertTrue(os.path.exists(os.path.join(self.ordner, "auswertung_windows.md")))
        app.schritt([taste(pygame.K_ESCAPE)], dt=0.05)
        self.assertIsInstance(app.ansicht, Szenarioliste)


@unittest.skipIf(pygame is None, "pygame-ce nicht installiert")
class TicketOberflaecheTest(unittest.TestCase):
    def setUp(self):
        self._daten = Datenordner()
        self.ordner = self._daten.__enter__()
        from n3xtbyt3.oberflaeche.app import App
        self.app = App(groesse=(1280, 720))
        self.app.schritt([taste(pygame.K_ESCAPE)], dt=0.05)  # Willkommensbild → Hauptmenü

    def tearDown(self):
        self.app.ansicht.verlassen()
        pygame.quit()
        self._daten.__exit__(None, None, None)

    def test_ticket_ueber_zwei_rechner(self):
        """Abnahme M4: Ein Ticket-Einsatz über zwei Rechner ist spielbar."""
        from n3xtbyt3.kern.spielstand import Spielstand
        from n3xtbyt3.oberflaeche.spiel import Spielansicht
        from n3xtbyt3.oberflaeche.tickets_ansicht import Ticketliste

        app = self.app
        app.schritt([taste(pygame.K_5)], dt=0.05)  # Kachel „Tickets“
        self.assertIsInstance(app.ansicht, Ticketliste)
        liste = app.ansicht
        index = 1 + next(i for i, e in enumerate(liste.eintraege) if e.szenario.id == "tk-shop-502")
        liste.auswahl = index
        app.schritt([taste(pygame.K_RETURN)], dt=0.05)
        spiel = app.ansicht
        self.assertIsInstance(spiel, Spielansicht)
        self.assertTrue(spiel.ticketmodus)
        app.schritt([taste(pygame.K_F3)], dt=0.05)
        self.assertFalse(spiel.notiz_modus)  # noch nicht behoben
        for schritt in spiel.szenario.loesung:
            app.schritt(tippe(schritt), dt=0.05)
        self.assertTrue(spiel.sitzung.geloest)
        self.assertEqual(spiel.sitzung.aktiv.name, spiel.sitzung.haupt.name)  # wieder am PC
        app.schritt([taste(pygame.K_F3)], dt=0.05)
        self.assertTrue(spiel.notiz_modus)
        app.schritt(tippe("php8.3-fpm auf srv-web01 gestartet"), dt=0.05)
        self.assertTrue(spiel.sitzung.ticket_geschlossen)
        app.schritt([taste(pygame.K_ESCAPE)], dt=0.05)
        self.assertIsInstance(app.ansicht, Ticketliste)
        verlauf = Spielstand.lade("windows").eintrag("tk-shop-502")["verlauf"]
        self.assertTrue(verlauf[-1]["ticket_geschlossen"])


@unittest.skipIf(pygame is None, "pygame-ce nicht installiert")
class GrundkursOberflaecheTest(unittest.TestCase):
    def setUp(self):
        self._daten = Datenordner()
        self.ordner = self._daten.__enter__()
        from n3xtbyt3.oberflaeche.app import App
        self.app = App(groesse=(1280, 720))

    def tearDown(self):
        self.app.ansicht.verlassen()
        pygame.quit()
        self._daten.__exit__(None, None, None)

    def test_erster_start_bis_lektion_2(self):
        """Abnahme G: Erster Start zeigt das Willkommensbild, „Grundkurs starten“ führt in Windows-Lektion 1."""
        from n3xtbyt3.kern.spielstand import Spielstand
        from n3xtbyt3.oberflaeche.grundkurs_ansicht import Grundkursliste, Lektionsansicht, Willkommen
        from n3xtbyt3.oberflaeche.menue import Szenarioliste

        app = self.app
        self.assertIsInstance(app.ansicht, Willkommen)
        self.assertEqual(app.ansicht.auswahl, 0)  # „Grundkurs starten“ vorgewählt
        app.schritt([], dt=0.05)
        app.schritt([taste(pygame.K_RETURN)], dt=0.05)
        lektion = app.ansicht
        self.assertIsInstance(lektion, Lektionsansicht)
        self.assertEqual(lektion.lektion.id, "gk-win-konsole")
        app.schritt(tippe("hostnme"), dt=0.05)  # Tippfehler: freundlicher Hinweis, Schritt bleibt
        self.assertEqual(lektion.lauf.index, 0)
        self.assertIn("Fast!", lektion.lauf.letzter_tipp)
        for schritt in lektion.lektion.mitmachen:
            app.schritt(tippe(schritt.eingabe[0]), dt=0.05)
        self.assertEqual(lektion.lauf.teil, "aufgaben")
        app.schritt([taste(pygame.K_F1)], dt=0.05)
        self.assertEqual(lektion.lauf.hinweis_stufe, 1)
        for aufgabe in lektion.lektion.aufgaben:
            for befehl in aufgabe.loesung:
                app.schritt(tippe(befehl), dt=0.05)
        self.assertTrue(lektion.lauf.fertig)
        self.assertTrue(Spielstand.lade("windows").lektion("gk-win-konsole")["fertig"])
        app.schritt([taste(pygame.K_F2)], dt=0.05)
        self.assertEqual(app.ansicht.lektion.id, "gk-win-ordner")
        app.schritt([taste(pygame.K_ESCAPE)], dt=0.05)
        self.assertIsInstance(app.ansicht, Grundkursliste)
        self.assertEqual(app.ansicht.auswahl, 1)  # Lektion 2 ist dran
        app.schritt([taste(pygame.K_ESCAPE)], dt=0.05)
        self.assertIsInstance(app.ansicht, Szenarioliste)
        self.assertIn("Lektion 2 von 10", app.ansicht.sonder[0][1])
        app.schritt([taste(pygame.K_RETURN)], dt=0.05)
        self.assertIsInstance(app.ansicht, Grundkursliste)


if __name__ == "__main__":
    unittest.main()
