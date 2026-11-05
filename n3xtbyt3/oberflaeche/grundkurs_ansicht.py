"""Grundkurs in der Oberfläche: Willkommensbild, Lektionsliste und Lektionsansicht."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ..kern import grundkurs as gk
from ..kern.editor import EditorPuffer
from ..kern.spielstand import Spielstand
from ..kern.systeme import SYSTEME
from ..kern.szenario import SzenarioFehler, lade_allgemein
from .basis import Ansicht, Knopf, MatrixRegen, knopf_klick, zeichne_knopf
from .editor_ansicht import EditorFeld
from .panel import Bloecke
from .stil import FARBE, glow_text
from .terminal import Terminal
from .text import umbrechen

if TYPE_CHECKING:
    from .app import App


def oeffne_kurs(app: "App", system_id: str) -> None:
    """Zur Lektionsliste eines Systems."""
    kurs = gk.lade_kurs(system_id)
    app.wechsle(Grundkursliste(app, system_id, kurs, Spielstand.lade(system_id)))


def starte_lektion(app: "App", lektion: gk.Lektion, kurs: gk.Kursergebnis, stand: Spielstand) -> None:
    try:
        allgemein = lade_allgemein(lektion.system_id)
    except SzenarioFehler:
        return
    app.wechsle(Lektionsansicht(app, lektion, kurs, allgemein, stand))


def _status(stand: Spielstand, lektion: gk.Lektion) -> str:
    return "fertig" if stand.lektion(lektion.id)["fertig"] else "offen"


# --------------------------------------------------------------------------- Willkommen

class Willkommen(Ansicht):
    """Erster Start ohne Spielstand: kurze Begrüßung, „Grundkurs starten“ ist vorgewählt."""

    def __init__(self, app: "App"):
        super().__init__(app)
        self.auswahl = 0
        self.wahl = [("grundkurs", "Grundkurs starten (empfohlen) – Windows, Lektion 1: die Konsole"),
                     ("menue", "Zum Hauptmenü – ich kenne mich schon aus")]
        self.rects: list[pygame.Rect] = []
        self.regen: MatrixRegen | None = None

    def schrift_geaendert(self) -> None:
        self.regen = None

    def _oeffnen(self, art: str) -> None:
        from .menue import Hauptmenue
        if art == "grundkurs":
            kurs = gk.lade_kurs("windows")
            if kurs.lektionen:
                starte_lektion(self.app, kurs.lektionen[0], kurs, Spielstand.lade("windows"))
                return
        self.app.wechsle(Hauptmenue(self.app))

    def ereignis(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_TAB):
                self.auswahl = (self.auswahl + 1) % len(self.wahl)
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._oeffnen(self.wahl[self.auswahl][0])
            elif e.key == pygame.K_ESCAPE:
                self._oeffnen("menue")
        elif e.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.rects):
                if r.collidepoint(e.pos):
                    self.auswahl = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(e.pos):
                    self._oeffnen(self.wahl[i][0])

    def update(self, dt):
        if self.regen:
            self.regen.update(dt)

    def zeichnen(self, f):
        s = self.app.schriften
        w, h = f.get_size()
        if self.regen is None or (self.regen.breite, self.regen.hoehe) != (w, h):
            self.regen = MatrixRegen(s.klein_mono, (w, h))
        f.fill(FARBE["hintergrund"])
        self.regen.zeichnen(f)
        schleier = pygame.Surface((w, h), pygame.SRCALPHA)
        schleier.fill((0, 0, 0, 170))
        f.blit(schleier, (0, 0))
        y = int(h * 0.09)
        glow_text(f, s.titel, "N3XTBYT3", FARBE["gruen"], (w // 2, y), staerke=3, mitte=True)
        y += s.titel.get_linesize() + s.zeilen_hoehe
        breite = min(int(w * 0.7), 70 * s.zeichen_breite)
        x = (w - breite) // 2
        text = ("Willkommen! Hier lernst du, Fehler an Computern zu finden und zu beheben – mit Befehlen in einem "
                "nachgebauten Terminal. Alles ist Simulation: Dein echter PC bleibt unberührt, du kannst nichts "
                "kaputt machen.\n\nNeu an der Konsole? Dann fang mit dem Grundkurs an. Er beginnt ganz vorn: Was ist "
                "ein Prompt, wie tippe ich einen Befehl? Schritt für Schritt, mit Erklärung nach jedem Befehl.")
        for zeile in umbrechen(text, s.text, breite):
            if zeile:
                f.blit(s.text.render(zeile, True, FARBE["text"]), (x, y))
            y += s.text.get_linesize()
        y += s.zeilen_hoehe * 2
        self.rects = []
        kh = int(s.zeilen_hoehe * 2.2)
        for i, (_, label) in enumerate(self.wahl):
            rect = pygame.Rect(x, y, breite, kh)
            self.rects.append(rect)
            gewaehlt = i == self.auswahl
            pygame.draw.rect(f, FARBE["auswahl"] if gewaehlt else FARBE["panel"], rect, border_radius=6)
            pygame.draw.rect(f, FARBE["linie"] if gewaehlt else FARBE["linie_dunkel"], rect,
                             width=3 if gewaehlt else 2, border_radius=6)
            font = s.text_fett if gewaehlt else s.text
            bild = font.render(label, True, FARBE["gruen_hell"] if gewaehlt else FARBE["text"])
            f.blit(bild, (rect.left + s.zeichen_breite * 2, rect.centery - bild.get_height() // 2))
            y += kh + s.zeilen_hoehe // 2
        fuss = "Pfeiltasten + Enter: wählen  ·  Esc: Hauptmenü  ·  Strg +/−: Schriftgröße  ·  F11: Vollbild"
        bild = s.klein.render(fuss, True, FARBE["text_schwach"])
        f.blit(bild, bild.get_rect(midbottom=(w // 2, h - s.zeilen_hoehe)))


# --------------------------------------------------------------------------- Lektionsliste

class Grundkursliste(Ansicht):
    def __init__(self, app: "App", system_id: str, kurs: gk.Kursergebnis, stand: Spielstand):
        super().__init__(app)
        self.system_id = system_id
        self.kurs = kurs
        self.stand = stand
        _, offen = gk.fortschritt(stand, kurs.lektionen)
        self.auswahl = kurs.lektionen.index(offen) if offen else 0
        self.rects: list[tuple[pygame.Rect, int]] = []
        self._kurse: dict | None = None
        self._staende: dict[str, Spielstand] = {system_id: stand}

    def _voraussetzung(self, lektion: gk.Lektion) -> str | None:
        """„braucht: Windows-Lektion 10“, solange die vorausgesetzte Lektion nicht fertig ist."""
        if not lektion.voraussetzung:
            return None
        if self._kurse is None:
            self._kurse = gk.alle_kurse()
        vor = gk.finde_lektion(self._kurse, lektion.voraussetzung)
        if vor is None:
            return None
        stand = self._staende.setdefault(vor.system_id, Spielstand.lade(vor.system_id))
        if stand.lektion(vor.id)["fertig"]:
            return None
        return "braucht: " + gk.lektion_name(vor, self.system_id)

    def ereignis(self, e):
        n = len(self.kurs.lektionen)
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_UP and n:
                self.auswahl = (self.auswahl - 1) % n
            elif e.key == pygame.K_DOWN and n:
                self.auswahl = (self.auswahl + 1) % n
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE) and n:
                starte_lektion(self.app, self.kurs.lektionen[self.auswahl], self.kurs, self.stand)
            elif e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.zurueck()
        elif e.type == pygame.MOUSEMOTION:
            for r, i in self.rects:
                if r.collidepoint(e.pos):
                    self.auswahl = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for r, i in self.rects:
                if r.collidepoint(e.pos):
                    starte_lektion(self.app, self.kurs.lektionen[i], self.kurs, self.stand)
        elif e.type == pygame.MOUSEWHEEL and n:
            self.auswahl = max(0, min(n - 1, self.auswahl - e.y))

    def zurueck(self) -> None:
        from .menue import Szenarioliste, lade_alles
        ergebnis, allgemein, stand = lade_alles(self.system_id)
        self.app.wechsle(Szenarioliste(self.app, self.system_id, ergebnis, allgemein, stand))

    def zeichnen(self, f):
        s = self.app.schriften
        w, h = f.get_size()
        f.fill(FARBE["hintergrund"])
        rand = s.zeichen_breite * 3
        y = s.zeilen_hoehe
        lektionen = self.kurs.lektionen
        fertig, offen = gk.fortschritt(self.stand, lektionen)
        glow_text(f, s.zwischen, f"GRUNDKURS // {SYSTEME[self.system_id].name}", FARBE["gruen"], (rand, y))
        info = s.text.render(f"{fertig} von {len(lektionen)} Lektionen geschafft", True, FARBE["text"])
        f.blit(info, (w - rand - info.get_width(), y + s.zeilen_hoehe // 4))
        y += s.zwischen.get_linesize() + s.zeilen_hoehe // 2
        pygame.draw.line(f, FARBE["linie"], (rand, y), (w - rand, y), 2)
        y += s.zeilen_hoehe // 2
        unter = ("Von vorn nach hinten: Jede Lektion erklärt kurz, dann tippst du mit, dann probierst du selbst. "
                 + (f"Als Nächstes: Lektion {offen.nr}." if offen else "Alles geschafft – du kannst jede Lektion wiederholen."))
        for zeile in umbrechen(unter, s.text, w - 2 * rand):
            f.blit(s.text.render(zeile, True, FARBE["text_schwach"]), (rand, y))
            y += s.text.get_linesize()
        y += s.zeilen_hoehe // 2

        fehlerzeilen = [f"Fehlerhafte Lektion: {fe.datei.name} – {fe.meldungen[0]}" for fe in self.kurs.fehler]
        if fehlerzeilen:
            fy = h - s.zeilen_hoehe * 2 - len(fehlerzeilen[:6]) * s.klein.get_linesize()
            for zeile in fehlerzeilen[:6]:
                f.blit(s.klein.render(zeile, True, FARBE["fehler"]), (rand, fy))
                fy += s.klein.get_linesize()

        zeile_h = int(s.zeilen_hoehe * 1.6)
        self.rects = []
        if not lektionen:
            f.blit(s.text.render("Für dieses System gibt es noch keine Lektionen.", True, FARBE["aus"]), (rand, y))
        for i, l in enumerate(lektionen):
            rect = pygame.Rect(rand, y, w - 2 * rand, zeile_h - 4)
            if rect.bottom > h - s.zeilen_hoehe * 2 - len(fehlerzeilen[:6]) * s.klein.get_linesize():
                break
            self.rects.append((rect, i))
            gewaehlt = i == self.auswahl
            if gewaehlt:
                pygame.draw.rect(f, FARBE["auswahl"], rect, border_radius=4)
                pygame.draw.rect(f, FARBE["linie"], rect, width=2, border_radius=4)
            ty = rect.top + (rect.height - s.text.get_linesize()) // 2
            x = rect.left + s.zeichen_breite
            status = _status(self.stand, l)
            zeichen = "✓" if status == "fertig" else ("»" if l is offen else "·")
            farbe = FARBE["gruen"] if status == "fertig" else (FARBE["erfolg"] if l is offen else FARBE["aus"])
            f.blit(s.text_fett.render(zeichen, True, farbe), (x, ty))
            x += s.zeichen_breite * 3
            f.blit(s.text.render(f"Lektion {l.nr}", True, FARBE["text_schwach"]), (x, ty))
            x += s.zeichen_breite * 11
            f.blit(s.text.render(l.titel, True, FARBE["gruen_hell"] if gewaehlt else FARBE["text"]), (x, ty))
            rx = rect.right - s.zeichen_breite
            tags = []
            if not l.bestaetigt:
                tags.append((" ungeprüft ", FARBE["warnung"]))
            if status == "fertig":
                tags.append((" fertig ", FARBE["bestaetigt"]))
            elif l is offen:
                tags.append((" als Nächstes ", FARBE["erfolg"]))
            vor = self._voraussetzung(l)
            if vor:
                tags.append((f" {vor} ", FARBE["sim"]))
            for text, hinter in tags:
                tag = s.klein.render(text, True, FARBE["warnung_text"], hinter)
                rx -= tag.get_width()
                f.blit(tag, (rx, rect.centery - tag.get_height() // 2))
                rx -= s.zeichen_breite
            y += zeile_h

        fuss = "Pfeiltasten + Enter: Lektion starten  ·  F4 Befehlsbuch  ·  F5 Lexikon  ·  Esc: zurück zur Szenarioliste"
        bild = s.klein.render(fuss, True, FARBE["text_schwach"])
        f.blit(bild, bild.get_rect(midbottom=(w // 2, h - s.zeilen_hoehe // 2)))


# --------------------------------------------------------------------------- Lektion

class Lektionsansicht(Ansicht):
    """Links das Terminal, rechts: worum es geht, was zu tippen ist, Erklärung, Hinweise."""

    def __init__(self, app: "App", lektion: gk.Lektion, kurs: gk.Kursergebnis, allgemein, stand: Spielstand):
        super().__init__(app)
        self.lektion = lektion
        self.kurs = kurs
        self.allgemein = allgemein
        self.stand = stand
        self.system_id = lektion.system_id
        self.lauf = gk.Lektionslauf(lektion, allgemein)
        self.terminal = Terminal()
        self.terminal.schreibe(f"[N3XTBYT3] Grundkurs {SYSTEME[self.system_id].name} · Lektion {lektion.nr}: "
                               f"{lektion.titel}", "sim")
        self.terminal.schreibe("[N3XTBYT3] Rechts steht, was du tippen sollst. Hinweis: F1 · Befehlsbuch: F4 · "
                               "Lexikon: F5 · zurück: Esc", "sim")
        self.terminal.schreibe("")
        self.panel_scroll = 0
        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.knoepfe: list[Knopf] = []
        self.blink = 0.0
        self.editor: EditorFeld | None = None
        self.letzte_erklaerung: str | None = None
        self.hinweis_mitmachen: str | None = None
        self._gespeichert = False

    # ------------------------------------------------------------------ Aktionen

    def _speichern(self) -> None:
        # Einmal pro Durchgang: beim Schaffen der Lektion sofort, sonst beim Verlassen.
        if self._gespeichert:
            return
        self._gespeichert = True
        if self.stand.lektion_eintragen(self.lektion.id, self.lauf.ergebnis()):
            try:
                self.stand.speichere()
                from ..kern import auswertung
                from ..kern.szenario import lade_system
                auswertung.schreibe(self.system_id, lade_system(self.system_id, allgemein=self.allgemein).szenarien,
                                    self.stand)
            except OSError as e:
                print(f"Spielstand konnte nicht gespeichert werden: {e}")

    def verlassen(self) -> None:
        self._speichern()

    def hinweis(self) -> None:
        text = self.lauf.naechster_hinweis()
        if text is None:
            meldung = ("Die Lektion ist geschafft – weiter mit F2." if self.lauf.fertig
                       else "Alle drei Hinweise sind schon offen (rechts).")
            self.terminal.schreibe("[N3XTBYT3] " + meldung, "sim")
            return
        if self.lauf.teil == "mitmachen":
            self.hinweis_mitmachen = text
            self.terminal.schreibe("[N3XTBYT3] " + text, "sim")
        else:
            self.terminal.schreibe(f"[N3XTBYT3] Hinweis {self.lauf.hinweis_stufe} steht rechts.", "sim")
        self.panel_scroll = 0

    def naechste(self) -> None:
        self._speichern()
        lektionen = self.kurs.lektionen
        i = lektionen.index(self.lektion) if self.lektion in lektionen else -1
        if 0 <= i < len(lektionen) - 1:
            starte_lektion(self.app, lektionen[i + 1], self.kurs, self.stand)
        else:
            self.zur_liste()

    def zur_liste(self) -> None:
        self._speichern()
        self.app.wechsle(Grundkursliste(self.app, self.system_id, self.kurs, self.stand))

    def _antwort_zeigen(self, la: gk.LektionsAntwort) -> None:
        if la.antwort.aktion == "leeren":
            self.terminal.leeren()
        for z in la.antwort.zeilen:
            self.terminal.schreibe(z.text, z.art)
        if la.geschafft:
            self.letzte_erklaerung = la.erklaerung
            self.hinweis_mitmachen = None
            self.panel_scroll = 0
            if la.teil_neu == "aufgaben":
                self.terminal.schreibe("[N3XTBYT3] ✓ Geschafft! Mitmachen ist durch – jetzt probierst du selbst "
                                       "(rechts). Hinweise mit F1.", "erfolg")
            elif la.teil_neu == "fertig":
                self.terminal.schreibe("[N3XTBYT3] ✓ Lektion geschafft! Rechts steht, was du jetzt kannst. "
                                       "Weiter mit F2.", "erfolg")
                self._speichern()
            else:
                self.terminal.schreibe("[N3XTBYT3] ✓ Geschafft! Die Erklärung steht rechts.", "erfolg")
        elif la.tipp:
            self.terminal.schreibe("[N3XTBYT3] " + la.tipp, "sim")

    def ausfuehren(self, befehl: str) -> None:
        la = self.lauf.eingabe(befehl)
        self._antwort_zeigen(la)
        antwort = la.antwort
        if antwort.aktion == "editor" and antwort.editor:
            puffer = EditorPuffer(antwort.editor["pfad"], antwort.editor["inhalt"],
                                  antwort.editor["nur_lesen"], antwort.editor["neu"])
            self.editor = EditorFeld(puffer, self._datei_speichern, self._editor_zu)

    def _datei_speichern(self, pfad: str, text: str) -> str:
        la = self.lauf.datei_speichern(pfad, text)
        zeilen = la.antwort.zeilen
        la.antwort.zeilen = zeilen[1:]
        self._antwort_zeigen(la)
        return zeilen[0].text if zeilen else ""

    def _editor_zu(self) -> None:
        self.editor = None

    # ------------------------------------------------------------------ Ereignisse

    def ereignis(self, e):
        if knopf_klick(self.knoepfe, e):
            return
        if self.editor is not None:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_F1:
                self.hinweis()
            elif e.type == pygame.KEYDOWN:
                self.editor.taste(e)
            elif e.type == pygame.TEXTINPUT:
                self.editor.text_eingabe(e.text)
            self.blink = 0.0
            return
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_F1:
                self.hinweis()
                return
            if e.key == pygame.K_F2:
                self.naechste()
                return
            if e.key == pygame.K_ESCAPE:
                self.zur_liste()
                return
            befehl = self.terminal.taste(e, self.lauf.sitzung.prompt())
            if befehl is not None:
                self.ausfuehren(befehl)
            self.blink = 0.0
        elif e.type == pygame.TEXTINPUT:
            self.terminal.text_eingabe(e.text)
            self.blink = 0.0
        elif e.type == pygame.MOUSEWHEEL:
            maus = pygame.mouse.get_pos()
            if self.panel_rect.collidepoint(maus):
                self.panel_scroll = max(0, self.panel_scroll - e.y * self.app.schriften.zeilen_hoehe * 2)
            else:
                self.terminal.blaettern(e.y * 3)

    def update(self, dt):
        self.blink += dt

    # ------------------------------------------------------------------ Zeichnen

    def zeichnen(self, f):
        s = self.app.schriften
        w, h = f.get_size()
        f.fill(FARBE["hintergrund"])
        kopf_h = int(s.zeilen_hoehe * 2)
        fuss_h = int(s.zeilen_hoehe * 1.4)
        panel_b = max(int(w * 0.38), 32 * s.zeichen_breite)
        panel_b = min(panel_b, w - 40 * s.zeichen_breite) if w > 72 * s.zeichen_breite else int(w * 0.42)
        self._kopf(f, pygame.Rect(0, 0, w, kopf_h))
        terminal_rect = pygame.Rect(0, kopf_h, w - panel_b, h - kopf_h - fuss_h)
        self.panel_rect = pygame.Rect(w - panel_b, kopf_h, panel_b, h - kopf_h - fuss_h)
        cursor_an = (self.blink % 1.0) < 0.6
        if self.editor is not None:
            self.editor.zeichnen(f, terminal_rect, s, cursor_an)
        else:
            self.terminal.zeichnen(f, terminal_rect, s, self.lauf.sitzung.prompt(), cursor_an)
        pygame.draw.line(f, FARBE["linie"], self.panel_rect.topleft, self.panel_rect.bottomleft, 2)
        self._panel(f, self.panel_rect)
        self._fuss(f, pygame.Rect(0, h - fuss_h, w, fuss_h))

    def _kopf(self, f, rect):
        s = self.app.schriften
        pygame.draw.rect(f, FARBE["kopf"], rect)
        pygame.draw.line(f, FARBE["linie"], rect.bottomleft, rect.bottomright, 2)
        x = s.zeichen_breite
        y = rect.centery - s.mono_fett.get_linesize() // 2
        r = glow_text(f, s.mono_fett, "N3XTBYT3", FARBE["gruen"], (x, y), staerke=1)
        rest = (f" // Grundkurs {SYSTEME[self.system_id].name} // Lektion {self.lektion.nr} von "
                f"{len(self.kurs.lektionen)} // {self.lauf.sitzung.fenstertitel()}")
        f.blit(s.mono.render(rest, True, FARBE["gruen_hell"]), (r.right + s.zeichen_breite, y))

    def _fuss(self, f, rect):
        s = self.app.schriften
        pygame.draw.rect(f, FARBE["kopf"], rect)
        pygame.draw.line(f, FARBE["linie_dunkel"], rect.topleft, rect.topright, 1)
        text = ("F1 Hinweis  ·  F2 Nächste Lektion  ·  F4 Befehlsbuch  ·  F5 Lexikon  ·  Esc Übersicht  ·  "
                "↑↓ frühere Befehle  ·  Strg +/− Schrift")
        bild = s.klein.render(text, True, FARBE["text_schwach"])
        f.blit(bild, (s.zeichen_breite, rect.centery - bild.get_height() // 2))

    def _bloecke(self, breite: int) -> Bloecke:
        s = self.app.schriften
        l = self.lektion
        lauf = self.lauf
        b = Bloecke(s, breite)
        b.absatz(l.titel, s.zwischen, FARBE["gruen_hell"])
        tags = [(f"Lektion {l.nr} von {len(self.kurs.lektionen)}", FARBE["linie_dunkel"], FARBE["gruen_hell"])]
        tags.append(("bestätigt", FARBE["bestaetigt"], FARBE["warnung_text"]) if l.bestaetigt
                    else ("UNGEPRÜFT", FARBE["warnung"], FARBE["warnung_text"]))
        b.etiketten(tags)

        if lauf.fertig:
            b.ueberschrift("GESCHAFFT – DAS KANNST DU JETZT", FARBE["erfolg"])
            for punkt in l.fertig:
                b.absatz("✓ " + punkt, einzug=0)
            b.abstand(s.zeilen_hoehe // 3)
            b.absatz("Die Befehle dieser Lektion stehen im Befehlsbuch (F4). Weiter mit F2 (nächste Lektion) "
                     "oder Esc (Übersicht).", s.klein, FARBE["erfolg"])

        if self.letzte_erklaerung:
            b.ueberschrift("✓ GERADE GESCHAFFT", FARBE["erfolg"])
            b.absatz(self.letzte_erklaerung)

        schritt = lauf.schritt
        if schritt is not None and lauf.teil == "mitmachen":
            b.ueberschrift(f"MITMACHEN · SCHRITT {lauf.index + 1} VON {len(l.mitmachen)}")
            b.absatz(schritt.text)
            b.kasten([("Tippe:", s.klein, FARBE["text_schwach"]), (schritt.eingabe[0], s.mono_fett, FARBE["gruen"])])
            b.absatz("… und drück Enter.", s.klein, FARBE["text_schwach"])
        elif schritt is not None:
            b.ueberschrift(f"SELBST PROBIEREN · AUFGABE {lauf.index + 1} VON {len(l.aufgaben)}")
            b.kasten([(schritt.text, s.text_fett, FARBE["gruen_hell"])], FARBE["magenta"])
            stufen = ("Richtung", "Werkzeug", "Fast die Lösung")
            if not lauf.gezeigte_hinweise:
                b.absatz("Nicht weiter? F1 zeigt einen Hinweis – Stufe für Stufe.", s.klein, FARBE["text_schwach"])
            for i, hinweis in enumerate(lauf.gezeigte_hinweise):
                b.absatz(f"{i + 1}. {stufen[i]}", s.text_fett, FARBE["sim"])
                b.absatz(hinweis, einzug=s.zeichen_breite)
        if lauf.letzter_tipp and not lauf.fertig:
            b.abstand(s.zeilen_hoehe // 3)
            b.absatz(lauf.letzter_tipp, s.text, FARBE["warnung"])

        b.ueberschrift("WORUM ES GEHT")
        b.absatz(l.erklaeren)
        if l.begriffe:
            b.ueberschrift("BEGRIFFE")
            for begriff, erklaerung in l.begriffe.items():
                b.absatz(begriff, s.text_fett, FARBE["gruen"])
                b.absatz(erklaerung, einzug=s.zeichen_breite)
        if lauf.erledigt:
            b.ueberschrift("BISHER")
            for erledigt, _ in lauf.erledigt:
                b.absatz("✓ " + (erledigt.eingabe[0] if erledigt.eingabe else erledigt.text),
                         s.klein_mono, FARBE["text_schwach"])
        b.ueberschrift("QUELLE")
        for q in l.quelle:
            b.absatz(q, s.klein, FARBE["text_schwach"])
        if not l.bestaetigt:
            b.absatz("Ungeprüft: von Claude geschrieben, von dir noch nicht mit dem echten System verglichen.",
                     s.klein, FARBE["warnung"])
        return b

    def _panel(self, f, rect):
        s = self.app.schriften
        pygame.draw.rect(f, FARBE["panel"], rect.inflate(-2, 0).move(1, 0))
        rand = s.zeichen_breite * 2
        knopf_h = int(s.zeilen_hoehe * 1.7)
        knopf_bereich = knopf_h + rand * 2
        inhalt = pygame.Rect(rect.left + rand, rect.top + rand // 2, rect.width - 2 * rand - 8,
                             rect.height - knopf_bereich - rand // 2)
        self.panel_scroll = self._bloecke(inhalt.width).zeichnen(f, inhalt, self.panel_scroll)
        kb = (inhalt.width - rand) // 2
        ky = rect.bottom - knopf_bereich + rand // 2
        weiter = "Nächste Lektion (F2)" if self.lauf.fertig else "Überspringen (F2)"
        self.knoepfe = [
            Knopf(pygame.Rect(inhalt.left, ky, kb, knopf_h), "Hinweis (F1)", self.hinweis, not self.lauf.fertig),
            Knopf(pygame.Rect(inhalt.left + kb + rand, ky, kb, knopf_h), weiter, self.naechste),
        ]
        maus = pygame.mouse.get_pos()
        for k in self.knoepfe:
            zeichne_knopf(f, k, s.text_fett, maus)
