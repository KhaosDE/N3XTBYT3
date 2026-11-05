"""Kleines Fenster mit Fortschrittsbalken, solange die neue Version geladen wird."""

from __future__ import annotations

import pygame

GROESSE = (640, 170)
HINTERGRUND = (4, 8, 7)
GRUEN = (61, 255, 122)
TEXT = (205, 230, 215)
DUNKEL = (0, 90, 52)


class Fortschrittsfenster:
    def __init__(self) -> None:
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption("N3XTBYT3 – Update")
        self.flaeche = pygame.display.set_mode(GROESSE)
        try:
            from n3xtbyt3.oberflaeche.stil import SCHRIFTORDNER
            self.font = pygame.font.Font(str(SCHRIFTORDNER / "DejaVuSans.ttf"), 18)
        except Exception:  # noqa: BLE001
            self.font = pygame.font.SysFont("segoeui,arial,sans", 18)

    def zeige(self, text: str, anteil: float | None) -> bool:
        """Zeichnet Text und Balken. False, wenn das Fenster geschlossen oder Esc gedrückt wurde."""
        weiter = True
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                weiter = False
        f = self.flaeche
        f.fill(HINTERGRUND)
        f.blit(self.font.render(text, True, TEXT), (24, 30))
        balken = pygame.Rect(24, 80, GROESSE[0] - 48, 26)
        pygame.draw.rect(f, DUNKEL, balken, width=2, border_radius=4)
        if anteil is not None:
            voll = balken.inflate(-6, -6)
            voll.width = int(voll.width * max(0.0, min(1.0, anteil)))
            pygame.draw.rect(f, GRUEN, voll, border_radius=3)
            prozent = self.font.render(f"{int(anteil * 100)} %", True, TEXT)
            f.blit(prozent, (balken.right - prozent.get_width(), balken.bottom + 10))
        hinweis = self.font.render("Esc: abbrechen und die alte Version starten", True, DUNKEL)
        f.blit(hinweis, (24, balken.bottom + 10))
        pygame.display.flip()
        return weiter

    def schliessen(self) -> None:
        pygame.display.quit()
