"""Hauptprogramm der Oberfläche: Fenster, Hauptschleife, globale Tasten."""

from __future__ import annotations

import os

# Scharfe Darstellung bei Windows-Skalierung (125 %, 150 % …). SDL liest das beim Start.
os.environ.setdefault("SDL_WINDOWS_DPI_AWARENESS", "permonitorv2")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

from ..kern import einstellungen  # noqa: E402
from .basis import Ansicht  # noqa: E402
from .stil import Schriften  # noqa: E402

FENSTER_STANDARD = (1600, 900)


class App:
    def __init__(self, groesse: tuple[int, int] | None = None):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption("N3XTBYT3 – Lern-Simulator für Systemwartung")
        self.einstellungen = einstellungen.lade()
        self._fenstergroesse = groesse or self._standardgroesse()
        self.fenster = self._fenster_oeffnen()
        pygame.key.set_repeat(400, 35)
        pygame.key.start_text_input()
        self.schriften = Schriften(self.einstellungen["schriftgroesse"])
        self.uhr = pygame.time.Clock()
        self.laufend = True
        from ..kern.spielstand import erster_start
        if erster_start():
            from .grundkurs_ansicht import Willkommen
            self.ansicht: Ansicht = Willkommen(self)
        else:
            from .menue import Hauptmenue
            self.ansicht = Hauptmenue(self)

    # ------------------------------------------------------------------ Fenster

    @staticmethod
    def _standardgroesse() -> tuple[int, int]:
        try:
            breite, hoehe = pygame.display.get_desktop_sizes()[0]
        except (AttributeError, IndexError, pygame.error):
            return FENSTER_STANDARD
        return (min(FENSTER_STANDARD[0], int(breite * 0.92)), min(FENSTER_STANDARD[1], int(hoehe * 0.88)))

    def _fenster_oeffnen(self) -> pygame.Surface:
        if self.einstellungen.get("vollbild"):
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        return pygame.display.set_mode(self._fenstergroesse, pygame.RESIZABLE)

    def vollbild_umschalten(self) -> None:
        self.einstellungen["vollbild"] = not self.einstellungen.get("vollbild")
        self.fenster = self._fenster_oeffnen()
        self._einstellungen_speichern()

    def schriftgroesse_aendern(self, schritt: int) -> None:
        neu = max(einstellungen.SCHRIFT_MIN,
                  min(einstellungen.SCHRIFT_MAX, self.einstellungen["schriftgroesse"] + schritt))
        if neu != self.einstellungen["schriftgroesse"]:
            self.einstellungen["schriftgroesse"] = neu
            self.schriften = Schriften(neu)
            self.ansicht.schrift_geaendert()
            self._einstellungen_speichern()

    def _einstellungen_speichern(self) -> None:
        try:
            einstellungen.speichere(self.einstellungen)
        except OSError as e:
            print(f"Einstellungen konnten nicht gespeichert werden: {e}")

    # ------------------------------------------------------------------ Ablauf

    def wechsle(self, ansicht: Ansicht) -> None:
        if ansicht is not self.ansicht:
            self.ansicht.verlassen()
        self.ansicht = ansicht

    def beenden(self) -> None:
        self.laufend = False

    def _globale_taste(self, e: pygame.event.Event) -> bool:
        if e.type != pygame.KEYDOWN:
            return False
        strg = bool(e.mod & pygame.KMOD_CTRL)
        if e.key == pygame.K_F11:
            self.vollbild_umschalten()
            return True
        if strg and e.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
            self.schriftgroesse_aendern(+2)
            return True
        if strg and e.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.schriftgroesse_aendern(-2)
            return True
        if strg and e.key == pygame.K_0:
            self.schriftgroesse_aendern(einstellungen.STANDARD["schriftgroesse"] - self.einstellungen["schriftgroesse"])
            return True
        return False

    def schritt(self, ereignisse: list[pygame.event.Event] | None = None, dt: float | None = None) -> None:
        """Ein Durchlauf der Hauptschleife (auch für Tests nutzbar)."""
        if dt is None:
            dt = self.uhr.tick(60) / 1000.0
        for e in (ereignisse if ereignisse is not None else pygame.event.get()):
            if e.type == pygame.QUIT:
                self.beenden()
                continue
            if self._globale_taste(e):
                continue
            # Strg+Plus erzeugt auf manchen Tastaturen zusätzlich ein Textzeichen
            if e.type == pygame.TEXTINPUT and pygame.key.get_mods() & pygame.KMOD_CTRL \
                    and not pygame.key.get_mods() & pygame.KMOD_ALT:
                continue
            self.ansicht.ereignis(e)
        self.ansicht.update(dt)
        self.ansicht.zeichnen(self.fenster)
        pygame.display.flip()

    def lauf(self) -> None:
        try:
            while self.laufend:
                self.schritt()
        finally:
            self.ansicht.verlassen()
            pygame.quit()


def main() -> None:
    import sys
    if "--selbsttest" in sys.argv[1:]:
        from ..kern import selbsttest
        raise SystemExit(selbsttest.main())
    App().lauf()


if __name__ == "__main__":
    main()
