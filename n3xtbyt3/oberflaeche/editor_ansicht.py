"""Editor (nano-Ersatz) im Terminalbereich: Text bearbeiten, Strg+O speichern, Strg+X beenden."""

from __future__ import annotations

from typing import Callable

import pygame

from ..kern.editor import EditorPuffer
from .stil import FARBE, Schriften

HILFE = "^O Speichern   ^X Beenden   ^K Zeile ausschneiden   Pfeile/Pos1/Ende/Bild bewegen"


class EditorFeld:
    """Zeichnet und bedient einen EditorPuffer.

    ``speichern(pfad, text)`` gibt die Statusmeldung zurück.
    ``beendet()`` wird nach dem Schließen aufgerufen.
    """

    def __init__(self, puffer: EditorPuffer, speichern: Callable[[str, str], str], beendet: Callable[[], None]):
        self.puffer = puffer
        self._speichern = speichern
        self._beendet = beendet
        self.meldung = "[ Schreibgeschützt – zum Ändern mit sudo öffnen ]" if puffer.nur_lesen else (
            "[ Neue Datei ]" if puffer.neu else f"[ {len(puffer.zeilen)} Zeilen gelesen ]")
        self.frage_beenden = False
        self.oben = 0
        self.sichtbar = 20

    def speichern(self) -> None:
        if self.puffer.nur_lesen:
            self.meldung = "[ Keine Schreibrechte – Datei mit sudo nano öffnen ]"
            return
        self.meldung = self._speichern(self.puffer.pfad, self.puffer.text)
        self.puffer.geaendert = False
        self.puffer.neu = False

    def beenden(self) -> None:
        if self.puffer.geaendert and not self.puffer.nur_lesen:
            self.frage_beenden = True
            self.meldung = "Änderungen speichern? J = ja · N = nein, verwerfen · Esc = zurück zum Text"
            return
        self._beendet()

    def text_eingabe(self, text: str) -> None:
        if self.frage_beenden:
            return
        self.puffer.einfuegen(text)

    def taste(self, e: pygame.event.Event) -> None:
        strg = bool(e.mod & pygame.KMOD_CTRL)
        k = e.key
        if self.frage_beenden:
            if k in (pygame.K_j, pygame.K_y):
                self.speichern()
                self._beendet()
            elif k == pygame.K_n:
                self._beendet()
            elif k in (pygame.K_ESCAPE, pygame.K_c):
                self.frage_beenden = False
                self.meldung = "[ Abgebrochen ]"
            return
        if strg and k == pygame.K_o:
            self.speichern()
        elif strg and k == pygame.K_x:
            self.beenden()
        elif strg and k == pygame.K_k:
            self.puffer.zeile_ausschneiden()
        elif k == pygame.K_ESCAPE:
            self.beenden()
        elif k in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.puffer.neue_zeile()
        elif k == pygame.K_BACKSPACE:
            self.puffer.rueckschritt()
        elif k == pygame.K_DELETE:
            self.puffer.entfernen()
        elif k == pygame.K_LEFT:
            self.puffer.links()
        elif k == pygame.K_RIGHT:
            self.puffer.rechts()
        elif k == pygame.K_UP:
            self.puffer.hoch()
        elif k == pygame.K_DOWN:
            self.puffer.runter()
        elif k == pygame.K_HOME:
            self.puffer.zeilenanfang()
        elif k == pygame.K_END:
            self.puffer.zeilenende()
        elif k == pygame.K_PAGEUP:
            self.puffer.hoch(max(1, self.sichtbar - 2))
        elif k == pygame.K_PAGEDOWN:
            self.puffer.runter(max(1, self.sichtbar - 2))
        elif k == pygame.K_TAB:
            self.puffer.einfuegen("    ")

    def zeichnen(self, f: pygame.Surface, rect: pygame.Rect, s: Schriften, cursor_an: bool) -> None:
        pygame.draw.rect(f, FARBE["terminal"], rect)
        zb, zh = s.zeichen_breite, s.zeilen_hoehe
        rand = zb
        # Kopfzeile (invers)
        kopf = pygame.Rect(rect.left, rect.top, rect.width, zh + 4)
        pygame.draw.rect(f, FARBE["gruen"], kopf)
        zustand = " [schreibgeschützt]" if self.puffer.nur_lesen else (" [geändert]" if self.puffer.geaendert else "")
        f.blit(s.mono_fett.render(f" Editor (nano-Ersatz)   {self.puffer.pfad}{zustand}", True, FARBE["terminal"]),
               (rect.left + rand, rect.top + 2))
        # Fußzeilen: Meldung und Tastenhilfe
        fuss_h = 2 * zh + 8
        text_rect = pygame.Rect(rect.left + rand, kopf.bottom + 4, rect.width - 2 * rand,
                                rect.height - kopf.height - fuss_h - 8)
        self.sichtbar = max(3, text_rect.height // zh)
        p = self.puffer
        if p.zeile < self.oben:
            self.oben = p.zeile
        elif p.zeile >= self.oben + self.sichtbar:
            self.oben = p.zeile - self.sichtbar + 1
        spalten = max(10, text_rect.width // zb)
        versatz = max(0, p.spalte - spalten + 1)
        for i in range(self.oben, min(len(p.zeilen), self.oben + self.sichtbar)):
            zeile = p.zeilen[i]
            if i == p.zeile:
                zeile = zeile[versatz:versatz + spalten]
            else:
                zeile = zeile[:spalten]
            y = text_rect.top + (i - self.oben) * zh
            if zeile:
                f.blit(s.mono.render(zeile, True, FARBE["eingabe"]), (text_rect.left, y))
        if cursor_an and not self.frage_beenden:
            cx = text_rect.left + (p.spalte - versatz) * zb
            cy = text_rect.top + (p.zeile - self.oben) * zh
            pygame.draw.rect(f, FARBE["gruen"], (cx, cy + 2, zb, zh - 4))
            zeichen = p.zeilen[p.zeile][p.spalte:p.spalte + 1]
            if zeichen:
                f.blit(s.mono.render(zeichen, True, FARBE["terminal"]), (cx, cy))
        y = rect.bottom - fuss_h
        farbe = FARBE["warnung"] if self.frage_beenden else FARBE["sim"]
        f.blit(s.mono.render(self.meldung, True, farbe), (rect.left + rand, y))
        hilfe = pygame.Rect(rect.left, rect.bottom - zh - 4, rect.width, zh + 4)
        pygame.draw.rect(f, FARBE["kopf"], hilfe)
        f.blit(s.klein_mono.render(HILFE, True, FARBE["gruen_hell"]), (rect.left + rand, hilfe.top + 3))
