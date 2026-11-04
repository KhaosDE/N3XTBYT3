"""Befehls-Training: Fragen „Welcher Befehl …?“ im Terminal beantworten."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

import pygame

from ..kern import auswertung, training
from ..kern.befehle import Vergleicher
from ..kern.systeme import SYSTEME
from .basis import Ansicht, Knopf, knopf_klick, zeichne_knopf
from .menue import Szenarioliste, lade_alles
from .stil import FARBE, glow_text
from .terminal import Terminal
from .text import umbrechen

if TYPE_CHECKING:
    from .app import App

PROMPT = "Befehl> "
P = "[N3XTBYT3] "


class Trainingsansicht(Ansicht):
    def __init__(self, app: "App", system_id: str, ergebnis, allgemein, stand):
        super().__init__(app)
        self.system_id = system_id
        self.ergebnis = ergebnis
        self.stand = stand
        self.kartei = stand.kartei
        self.karten = training.sammle_karten(ergebnis.szenarien)
        self.vergleicher = Vergleicher(SYSTEME[system_id])
        self.terminal = Terminal()
        self.karte: training.Karte | None = None
        self.zaehler: Counter[str] = Counter()
        self.geaendert = False
        self.blink = 0.0
        self.knoepfe: list[Knopf] = []
        self.terminal.schreibe(P + "Befehls-Training: Tippe den Befehl, der zur Beschreibung passt – mit Parametern",
                               "sim")
        self.terminal.schreibe(" " * len(P) + "wie im Szenario. F1 zeigt die Lösung (zählt als falsch). Esc beendet.", "sim")
        self.terminal.schreibe("")
        self._naechste()

    def _naechste(self) -> None:
        zuletzt = self.karte.schluessel if self.karte else None
        self.karte = training.waehle_karte(self.karten, self.kartei, zuletzt=zuletzt)
        if self.karte is None:
            self.terminal.schreibe(P + "Für dieses System gibt es noch keine Befehle zum Trainieren.", "sim")
            return
        fach = self.kartei.befehl(self.karte.schluessel)["fach"]
        zeilen = training.frage_text(self.karte).split("\n")
        self.terminal.schreibe(f"Frage (Fach {fach}): {zeilen[0]}", "erfolg")
        for z in zeilen[1:]:
            self.terminal.schreibe("   " + z, "sim")

    def _bewerten(self, bewertung: str) -> None:
        karte = self.karte
        if karte is None:
            return
        self.kartei.befehl_ergebnis(karte.schluessel, bewertung)
        self.zaehler[bewertung] += 1
        self.geaendert = True
        if bewertung == "richtig":
            self.terminal.schreibe(P + "Richtig!", "erfolg")
        elif bewertung == "halb":
            self.terminal.schreibe(P + f"Fast: Der Befehl stimmt, die Parameter weichen ab. Im Szenario: {karte.beispiel}",
                                   "sim")
        else:
            self.terminal.schreibe(P + f"Nicht richtig. Gesucht war: {karte.beispiel}", "fehler")
        self.terminal.schreibe("")
        self._naechste()

    def _loesung(self) -> None:
        if self.karte is None:
            return
        self.terminal.schreibe(PROMPT + "(Lösung gezeigt)", "eingabe", len(PROMPT))
        self._bewerten("falsch")

    def _speichern(self) -> None:
        if not self.geaendert:
            return
        self.geaendert = False
        try:
            self.stand.speichere()
            auswertung.schreibe(self.system_id, self.ergebnis.szenarien, self.stand)
        except OSError as e:
            print(f"Spielstand konnte nicht gespeichert werden: {e}")

    def zurueck(self) -> None:
        self._speichern()
        ergebnis, allgemein, stand = lade_alles(self.system_id)
        self.app.wechsle(Szenarioliste(self.app, self.system_id, ergebnis, allgemein, stand))

    def verlassen(self) -> None:
        self._speichern()

    def ereignis(self, e):
        if knopf_klick(self.knoepfe, e):
            return
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.zurueck()
                return
            if e.key == pygame.K_F1:
                self._loesung()
                return
            antwort = self.terminal.taste(e, PROMPT)
            if antwort is not None and self.karte is not None:
                if antwort.strip():
                    self._bewerten(training.bewerte(self.karte, antwort, self.vergleicher))
            self.blink = 0.0
        elif e.type == pygame.TEXTINPUT:
            self.terminal.text_eingabe(e.text)
            self.blink = 0.0
        elif e.type == pygame.MOUSEWHEEL:
            self.terminal.blaettern(e.y * 3)

    def update(self, dt):
        self.blink += dt

    def zeichnen(self, f):
        s = self.app.schriften
        w, h = f.get_size()
        f.fill(FARBE["hintergrund"])
        kopf_h = int(s.zeilen_hoehe * 2)
        panel_b = max(int(w * 0.30), 28 * s.zeichen_breite)
        kopf = pygame.Rect(0, 0, w, kopf_h)
        pygame.draw.rect(f, FARBE["kopf"], kopf)
        pygame.draw.line(f, FARBE["linie"], kopf.bottomleft, kopf.bottomright, 2)
        y = kopf.centery - s.mono_fett.get_linesize() // 2
        r = glow_text(f, s.mono_fett, "N3XTBYT3", FARBE["gruen"], (s.zeichen_breite, y), staerke=1)
        f.blit(s.mono.render(f" // {SYSTEME[self.system_id].name} // Befehls-Training", True, FARBE["gruen_hell"]),
               (r.right + s.zeichen_breite, y))
        term = pygame.Rect(0, kopf_h, w - panel_b, h - kopf_h)
        self.terminal.zeichnen(f, term, s, PROMPT, (self.blink % 1.0) < 0.6, aktiv=self.karte is not None)

        panel = pygame.Rect(w - panel_b, kopf_h, panel_b, h - kopf_h)
        pygame.draw.rect(f, FARBE["panel"], panel)
        pygame.draw.line(f, FARBE["linie"], panel.topleft, panel.bottomleft, 2)
        rand = s.zeichen_breite * 2
        x, y = panel.left + rand, panel.top + rand
        breite = panel.width - 2 * rand
        f.blit(s.mono_fett.render("DIESE RUNDE", True, FARBE["magenta"]), (x, y))
        y += s.mono_fett.get_linesize() + 4
        for name, farbe in (("richtig", "erfolg"), ("halb", "sim"), ("falsch", "fehler")):
            f.blit(s.text.render(f"{name}: {self.zaehler[name]}", True, FARBE[farbe]), (x, y))
            y += s.text.get_linesize()
        y += s.zeilen_hoehe // 2
        f.blit(s.mono_fett.render("LERNKARTEI", True, FARBE["magenta"]), (x, y))
        y += s.mono_fett.get_linesize() + 4
        faecher = Counter(self.kartei.befehl(k.schluessel)["fach"] for k in self.karten)
        for fach in range(1, 6):
            f.blit(s.text.render(f"Fach {fach}: {faecher[fach]} Befehle", True, FARBE["text"]), (x, y))
            y += s.text.get_linesize()
        y += s.zeilen_hoehe // 2
        f.blit(s.mono_fett.render("SO WIRD BEWERTET", True, FARBE["magenta"]), (x, y))
        y += s.mono_fett.get_linesize() + 4
        erklaerung = ("Richtig: Befehl und Parameter wie im Szenario → ein Fach weiter. "
                      "Halb: richtiger Befehl, andere Parameter → Fach bleibt. "
                      "Falsch → zurück in Fach 1, die Frage kommt bald wieder.")
        for zeile in umbrechen(erklaerung, s.klein, breite):
            f.blit(s.klein.render(zeile, True, FARBE["text"]), (x, y))
            y += s.klein.get_linesize()

        knopf_h = int(s.zeilen_hoehe * 1.7)
        ky = panel.bottom - 2 * knopf_h - rand
        self.knoepfe = [
            Knopf(pygame.Rect(x, ky, breite, knopf_h), "Lösung zeigen (F1)", self._loesung, self.karte is not None),
            Knopf(pygame.Rect(x, ky + knopf_h + rand // 2, breite, knopf_h), "Beenden (Esc)", self.zurueck),
        ]
        maus = pygame.mouse.get_pos()
        for k in self.knoepfe:
            zeichne_knopf(f, k, s.text_fett, maus)
