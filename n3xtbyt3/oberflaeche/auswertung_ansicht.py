"""Auswertung eines Systems ansehen (dieselbe Datei, die auch Claude lesen kann)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ..kern import auswertung, pfade
from ..kern.systeme import SYSTEME
from .basis import Ansicht
from .menue import Szenarioliste, lade_alles
from .stil import FARBE, glow_text
from .text import umbrechen

if TYPE_CHECKING:
    from .app import App


def _tabelle(zeilen: list[str]) -> list[str]:
    """Markdown-Tabelle → bündige Textzeilen."""
    reihen = []
    for z in zeilen:
        zellen = [c.strip().strip("`") for c in z.strip().strip("|").split("|")]
        if all(set(c) <= {"-", ":"} for c in zellen):
            continue
        reihen.append(zellen)
    breiten = [max(len(r[i]) for r in reihen if i < len(r)) for i in range(max(len(r) for r in reihen))]
    return ["  ".join(c.ljust(breiten[i]) for i, c in enumerate(r)).rstrip() for r in reihen]


class Auswertungsansicht(Ansicht):
    def __init__(self, app: "App", system_id: str, ergebnis, allgemein, stand):
        super().__init__(app)
        self.system_id = system_id
        self.scroll = 0
        try:
            daten = auswertung.schreibe(system_id, ergebnis.szenarien, stand)
            self.hinweis = f"Gespeichert als {pfade.datenordner() / f'auswertung_{system_id}.md'} (auch .json)"
        except OSError as e:
            daten = auswertung.erstelle(system_id, ergebnis.szenarien, stand)
            self.hinweis = f"Konnte nicht gespeichert werden: {e}"
        self.zeilen = self._aufbereiten(auswertung.als_markdown(daten))

    @staticmethod
    def _aufbereiten(md: str) -> list[tuple[str, str]]:
        """(Art, Text): titel, ueberschrift, tabelle, text."""
        ergebnis: list[tuple[str, str]] = []
        tabelle: list[str] = []
        for zeile in md.split("\n") + [""]:
            if zeile.startswith("|"):
                tabelle.append(zeile)
                continue
            if tabelle:
                ergebnis += [("tabelle", t) for t in _tabelle(tabelle)]
                tabelle = []
            if zeile.startswith("# "):
                ergebnis.append(("titel", zeile[2:]))
            elif zeile.startswith("## "):
                ergebnis.append(("ueberschrift", zeile[3:]))
            elif zeile.startswith("- "):
                ergebnis.append(("text", "• " + zeile[2:].replace("`", "")))
            else:
                ergebnis.append(("text", zeile.replace("`", "")))
        return ergebnis

    def ereignis(self, e):
        s = self.app.schriften
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                ergebnis, allgemein, stand = lade_alles(self.system_id)
                self.app.wechsle(Szenarioliste(self.app, self.system_id, ergebnis, allgemein, stand))
            elif e.key == pygame.K_DOWN:
                self.scroll += s.zeilen_hoehe * 2
            elif e.key == pygame.K_UP:
                self.scroll -= s.zeilen_hoehe * 2
            elif e.key == pygame.K_PAGEDOWN:
                self.scroll += self.app.fenster.get_height() // 2
            elif e.key == pygame.K_PAGEUP:
                self.scroll -= self.app.fenster.get_height() // 2
            elif e.key == pygame.K_HOME:
                self.scroll = 0
        elif e.type == pygame.MOUSEWHEEL:
            self.scroll -= e.y * s.zeilen_hoehe * 3
        self.scroll = max(0, self.scroll)

    def zeichnen(self, f):
        s = self.app.schriften
        w, h = f.get_size()
        f.fill(FARBE["hintergrund"])
        rand = s.zeichen_breite * 3
        breite = w - 2 * rand
        bloecke: list[tuple[pygame.font.Font, str, tuple, int]] = []
        for art, text in self.zeilen:
            if art == "titel":
                bloecke.append((s.zwischen, text, FARBE["gruen"], 0))
            elif art == "ueberschrift":
                bloecke.append((s.mono_fett, "", FARBE["text"], 0))
                bloecke.append((s.mono_fett, text.upper(), FARBE["magenta"], 0))
            elif art == "tabelle":
                bloecke.append((s.klein_mono, text, FARBE["gruen_hell"], 0))
            else:
                for teil in umbrechen(text, s.text, breite) or [""]:
                    bloecke.append((s.text, teil, FARBE["text"], 0))
        oben = s.zeilen_hoehe
        unten = h - s.zeilen_hoehe * 2
        gesamt = sum(b[0].get_linesize() for b in bloecke)
        self.scroll = min(self.scroll, max(0, gesamt - (unten - oben)))
        f.set_clip(pygame.Rect(0, oben, w, unten - oben))
        y = oben - self.scroll
        for font, text, farbe, _ in bloecke:
            hoehe = font.get_linesize()
            if text and y + hoehe > oben and y < unten:
                if font is s.zwischen:
                    glow_text(f, font, text, farbe, (rand, y), staerke=1)
                else:
                    f.blit(font.render(text, True, farbe), (rand, y))
            y += hoehe
        f.set_clip(None)
        fuss = f"↑↓ / Mausrad blättern · Esc zurück · {self.hinweis}"
        for i, zeile in enumerate(umbrechen(fuss, s.klein, breite)[:2]):
            f.blit(s.klein.render(zeile, True, FARBE["text_schwach"]), (rand, unten + 4 + i * s.klein.get_linesize()))
        titel = s.klein.render(SYSTEME[self.system_id].name, True, FARBE["text_schwach"])
        f.blit(titel, (w - rand - titel.get_width(), 4))
