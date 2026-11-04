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
        self.app = App(groesse=(1280, 720))

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
        app.schritt([taste(pygame.K_RETURN)], dt=0.05)  # Zufällig
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
        app.schritt([taste(pygame.K_RETURN)], dt=0.05)
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
        app.schritt([taste(pygame.K_RETURN)], dt=0.05)
        app.schritt([taste(pygame.K_ESCAPE)], dt=0.05)
        self.assertEqual(Spielstand.lade("windows").daten["szenarien"], {})


if __name__ == "__main__":
    unittest.main()
