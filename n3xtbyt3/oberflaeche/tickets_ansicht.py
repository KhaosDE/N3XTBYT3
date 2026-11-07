"""Ticket-Modus: Szenarien als Tickets mit Dringlichkeit, über alle Systeme gemischt."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

from ..kern import auswahl
from ..kern.systeme import REIHENFOLGE, SYSTEME
from .basis import Ansicht
from .menue import lade_alles
from .stil import FARBE, glow_text
from .text import kuerzen, zeichne_fuss

if TYPE_CHECKING:
    from .app import App

DRINGLICHKEIT_FARBE = {"kritisch": "fehler", "hoch": "warnung", "mittel": "erfolg", "niedrig": "text_schwach"}
DRINGLICHKEIT_RANG = {"kritisch": 0, "hoch": 1, "mittel": 2, "niedrig": 3}


@dataclass
class TicketEintrag:
    szenario: object
    system_id: str
    szenarien: list
    allgemein: object
    stand: object

    @property
    def geschlossen(self) -> bool:
        verlauf = self.stand.eintrag(self.szenario.id)["verlauf"]
        return any(v.get("ticket_geschlossen") for v in verlauf)


def lade_tickets() -> list[TicketEintrag]:
    eintraege: list[TicketEintrag] = []
    for sid in REIHENFOLGE:
        ergebnis, allgemein, stand = lade_alles(sid)
        if allgemein is None:
            continue
        for sz in ergebnis.szenarien:
            if sz.ticket:
                eintraege.append(TicketEintrag(sz, sid, ergebnis.szenarien, allgemein, stand))
    eintraege.sort(key=lambda e: (DRINGLICHKEIT_RANG.get(e.szenario.ticket.get("dringlichkeit"), 9),
                                  e.szenario.ticket.get("nummer", "")))
    return eintraege


def waehle_ticket(eintraege: list[TicketEintrag], zuletzt: str | None = None,
                  rng: random.Random | None = None) -> TicketEintrag | None:
    rng = rng or random.Random()
    kandidaten = [e for e in eintraege if e.szenario.id != zuletzt] or eintraege
    if not kandidaten:
        return None
    gewichte = []
    for e in kandidaten:
        if auswahl.faellig(e.stand, e.szenario.id):
            gewichte.append(auswahl.gewicht(e.stand, e.szenario.id))
        else:
            gewichte.append(1.0 / e.stand.kartei.szenario(e.szenario.id)["fach"])
    return rng.choices(kandidaten, weights=gewichte, k=1)[0]


def starte_ticket(app: "App", eintrag: TicketEintrag) -> None:
    from .spiel import Spielansicht
    app.wechsle(Spielansicht(app, eintrag.system_id, eintrag.szenario, eintrag.szenarien,
                             eintrag.allgemein, eintrag.stand, ticketmodus=True))


class Ticketliste(Ansicht):
    def __init__(self, app: "App"):
        super().__init__(app)
        self.eintraege = lade_tickets()
        self.auswahl = 0
        self.oben = 0
        self.rects: list[tuple[pygame.Rect, int]] = []

    def _anzahl(self) -> int:
        return len(self.eintraege) + 1

    def _starten(self, index: int) -> None:
        if not self.eintraege:
            return
        eintrag = waehle_ticket(self.eintraege) if index == 0 else self.eintraege[index - 1]
        if eintrag:
            starte_ticket(self.app, eintrag)

    def ereignis(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_UP:
                self.auswahl = (self.auswahl - 1) % self._anzahl()
            elif e.key == pygame.K_DOWN:
                self.auswahl = (self.auswahl + 1) % self._anzahl()
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._starten(self.auswahl)
            elif e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                from .menue import Hauptmenue
                self.app.wechsle(Hauptmenue(self.app))
        elif e.type == pygame.MOUSEMOTION:
            for r, i in self.rects:
                if r.collidepoint(e.pos):
                    self.auswahl = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for r, i in self.rects:
                if r.collidepoint(e.pos):
                    self._starten(i)
        elif e.type == pygame.MOUSEWHEEL:
            self.auswahl = max(0, min(self._anzahl() - 1, self.auswahl - e.y))

    def zeichnen(self, f):
        s = self.app.schriften
        w, h = f.get_size()
        f.fill(FARBE["hintergrund"])
        rand = s.zeichen_breite * 3
        y = s.zeilen_hoehe
        glow_text(f, s.zwischen, "N3XTBYT3 // Tickets", FARBE["gruen"], (rand, y))
        offen = sum(1 for e in self.eintraege if not e.geschlossen)
        info = s.text.render(f"{len(self.eintraege)} Tickets · {offen} offen", True, FARBE["text"])
        f.blit(info, (w - rand - info.get_width(), y + s.zeilen_hoehe // 4))
        y += s.zwischen.get_linesize() + s.zeilen_hoehe // 2
        pygame.draw.line(f, FARBE["linie"], (rand, y), (w - rand, y), 2)
        y += s.zeilen_hoehe // 2
        zeile_h = int(s.zeilen_hoehe * 1.5)
        sichtbar = max(3, (h - y - s.zeilen_hoehe * 3) // zeile_h)
        if self.auswahl < self.oben:
            self.oben = self.auswahl
        elif self.auswahl >= self.oben + sichtbar:
            self.oben = self.auswahl - sichtbar + 1
        self.rects = []
        for i in range(self.oben, min(self._anzahl(), self.oben + sichtbar)):
            rect = pygame.Rect(rand, y, w - 2 * rand, zeile_h - 4)
            self.rects.append((rect, i))
            if i == self.auswahl:
                pygame.draw.rect(f, FARBE["auswahl"], rect, border_radius=4)
                pygame.draw.rect(f, FARBE["linie"], rect, width=2, border_radius=4)
            ty = rect.top + (rect.height - s.text.get_linesize()) // 2
            x = rect.left + s.zeichen_breite
            if i == 0:
                f.blit(s.text_fett.render("»  Nächstes Ticket aus der Warteschlange (zufällig, Fälliges zuerst)", True,
                                          FARBE["gruen_hell"]), (x, ty))
            else:
                e = self.eintraege[i - 1]
                t = e.szenario.ticket
                stufe = t.get("dringlichkeit", "mittel")
                tag = s.klein.render(f" {stufe.upper()} ", True, FARBE["warnung_text"], FARBE[DRINGLICHKEIT_FARBE.get(stufe, "text")])
                f.blit(tag, (x, rect.centery - tag.get_height() // 2))
                x += s.zeichen_breite * 11
                f.blit(s.mono.render(t.get("nummer", ""), True, FARBE["text_schwach"]), (x, ty))
                x += s.zeichen_breite * 13
                rechts = s.klein.render(("geschlossen · " if e.geschlossen else "offen · ") + SYSTEME[e.system_id].name,
                                        True, FARBE["gruen"] if e.geschlossen else FARBE["text_schwach"])
                rx = rect.right - rechts.get_width() - s.zeichen_breite
                f.blit(rechts, (rx, rect.centery - rechts.get_height() // 2))
                betreff = kuerzen(t.get("betreff", e.szenario.titel), s.text, rx - x - s.zeichen_breite)
                f.blit(s.text.render(betreff, True, FARBE["text"]), (x, ty))
            y += zeile_h
        if not self.eintraege:
            f.blit(s.text.render("Noch keine Tickets vorhanden.", True, FARBE["text_schwach"]), (rand, y))
        fuss = "Pfeiltasten + Enter: Ticket öffnen  ·  Esc: zurück  ·  Im Ticket: F3 = Ticket schließen (wenn behoben)"
        zeichne_fuss(f, s.klein, fuss, FARBE["text_schwach"], h - s.zeilen_hoehe // 2, rand=s.zeichen_breite * 2)
