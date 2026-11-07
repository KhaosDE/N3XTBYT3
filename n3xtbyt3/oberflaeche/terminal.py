"""Das nachgebaute Terminal: Zeilenpuffer, Eingabezeile, Verlauf, Scrollen."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from .stil import FARBE, ZEILENART_FARBE, Schriften
from .text import umbrechen_fest, umbrechen_woerter_fest

MAX_ZEILEN = 5000


@dataclass
class TZeile:
    text: str
    art: str = "ausgabe"
    prompt_laenge: int = 0  # bei Eingabezeilen: so viele Zeichen sind Prompt


class Terminal:
    def __init__(self) -> None:
        self.zeilen: list[TZeile] = []
        self.eingabe = ""
        self.cursor = 0
        self.verlauf: list[str] = []
        self._verlauf_pos: int | None = None
        self._entwurf = ""
        self.scroll = 0  # Bildschirmzeilen nach oben geblättert
        self._anzeige: list[tuple[str, str, int]] = []  # (text, art, prompt-Zeichen in dieser Zeile)
        self._spalten = 0
        self._gezeichnet_zeilen = 0  # wie viele Puffer-Zeilen schon umgebrochen sind
        self.sichtbare_zeilen = 20

    # ------------------------------------------------------------------ Puffer

    def schreibe(self, text: str, art: str = "ausgabe", prompt_laenge: int = 0) -> None:
        if "\t" in text:
            text = text.expandtabs(8)
        self.zeilen.append(TZeile(text, art, prompt_laenge))
        if len(self.zeilen) > MAX_ZEILEN:
            self.zeilen = self.zeilen[-MAX_ZEILEN:]
            self._spalten = 0  # neu umbrechen
        self.scroll = 0

    def leeren(self) -> None:
        self.zeilen.clear()
        self._anzeige.clear()
        self._gezeichnet_zeilen = 0
        self.scroll = 0

    def _umbrechen(self, spalten: int) -> None:
        if spalten != self._spalten:
            self._spalten = spalten
            self._anzeige = []
            self._gezeichnet_zeilen = 0
        for z in self.zeilen[self._gezeichnet_zeilen:]:
            rest_prompt = z.prompt_laenge
            if z.art in ("sim", "erfolg"):
                einzug = len(z.text) - len(z.text.lstrip(" "))
                if z.text.startswith("[N3XTBYT3] "):
                    einzug = len("[N3XTBYT3] ")
                teile = umbrechen_woerter_fest(z.text, spalten, einzug)
            else:
                teile = umbrechen_fest(z.text, spalten)
            for teil in teile:
                p = min(rest_prompt, len(teil))
                self._anzeige.append((teil, z.art, p))
                rest_prompt -= p
        self._gezeichnet_zeilen = len(self.zeilen)

    # ------------------------------------------------------------------ Eingabe

    def text_eingabe(self, text: str) -> None:
        text = text.replace("\r", "").replace("\n", " ")
        self.eingabe = self.eingabe[: self.cursor] + text + self.eingabe[self.cursor:]
        self.cursor += len(text)
        self.scroll = 0

    def taste(self, e: pygame.event.Event, prompt: str, merken: bool = True) -> str | None:
        """Verarbeitet eine Taste. Gibt den abgeschickten Befehl zurück (oder None).

        merken=False: die Eingabe kommt nicht in den Verlauf (z. B. eine Lösungsnotiz).
        """
        strg = bool(e.mod & pygame.KMOD_CTRL)
        k = e.key
        if k in (pygame.K_RETURN, pygame.K_KP_ENTER):
            befehl = self.eingabe
            self.schreibe(prompt + befehl, "eingabe", len(prompt))
            if merken and befehl.strip() and (not self.verlauf or self.verlauf[-1] != befehl):
                self.verlauf.append(befehl)
            self.eingabe, self.cursor = "", 0
            self._verlauf_pos = None
            return befehl
        if k == pygame.K_BACKSPACE:
            if self.cursor > 0:
                self.eingabe = self.eingabe[: self.cursor - 1] + self.eingabe[self.cursor:]
                self.cursor -= 1
        elif k == pygame.K_DELETE:
            self.eingabe = self.eingabe[: self.cursor] + self.eingabe[self.cursor + 1:]
        elif k == pygame.K_LEFT:
            self.cursor = max(0, self.cursor - 1)
        elif k == pygame.K_RIGHT:
            self.cursor = min(len(self.eingabe), self.cursor + 1)
        elif k == pygame.K_HOME:
            self.cursor = 0
        elif k == pygame.K_END:
            self.cursor = len(self.eingabe)
        elif k == pygame.K_UP:
            self._verlauf_schritt(-1)
        elif k == pygame.K_DOWN:
            self._verlauf_schritt(1)
        elif k == pygame.K_PAGEUP:
            self.blaettern(max(1, self.sichtbare_zeilen - 2))
        elif k == pygame.K_PAGEDOWN:
            self.blaettern(-max(1, self.sichtbare_zeilen - 2))
        elif k == pygame.K_ESCAPE:
            pass
        elif strg and k == pygame.K_c:
            self.schreibe(prompt + self.eingabe + "^C", "eingabe", len(prompt))
            self.eingabe, self.cursor = "", 0
            self._verlauf_pos = None
            self._entwurf = ""
        elif strg and k == pygame.K_v:
            self.text_eingabe(_zwischenablage())
        return None

    def _verlauf_schritt(self, richtung: int) -> None:
        if not self.verlauf:
            return
        if self._verlauf_pos is None:
            if richtung > 0:
                return
            self._entwurf = self.eingabe
            self._verlauf_pos = len(self.verlauf) - 1
        else:
            self._verlauf_pos += richtung
        if self._verlauf_pos < 0:
            self._verlauf_pos = 0
        if self._verlauf_pos >= len(self.verlauf):
            self._verlauf_pos = None
            self.eingabe = self._entwurf
        else:
            self.eingabe = self.verlauf[self._verlauf_pos]
        self.cursor = len(self.eingabe)

    def blaettern(self, zeilen: int) -> None:
        self.scroll = max(0, self.scroll + zeilen)

    # ------------------------------------------------------------------ Zeichnen

    def zeichnen(self, flaeche: pygame.Surface, rect: pygame.Rect, schriften: Schriften,
                 prompt: str, cursor_an: bool, aktiv: bool = True) -> None:
        pygame.draw.rect(flaeche, FARBE["terminal"], rect)
        rand = schriften.zeichen_breite
        innen = rect.inflate(-2 * rand, -rand)
        zb, zh = schriften.zeichen_breite, schriften.zeilen_hoehe
        spalten = max(10, innen.width // zb)
        reihen = max(3, innen.height // zh)
        self.sichtbare_zeilen = reihen
        self._umbrechen(spalten)

        eingabe_voll = prompt + self.eingabe
        eingabe_zeilen = umbrechen_fest(eingabe_voll, spalten) if aktiv else []
        if aktiv and len(eingabe_voll) and len(eingabe_voll) % spalten == 0:
            eingabe_zeilen.append("")  # Cursor steht am Anfang der nächsten Zeile
        gesamt = len(self._anzeige) + len(eingabe_zeilen)
        self.scroll = min(self.scroll, max(0, gesamt - reihen))
        start = max(0, gesamt - reihen - self.scroll)

        y = innen.top
        for i in range(start, min(gesamt, start + reihen)):
            if i < len(self._anzeige):
                text, art, p = self._anzeige[i]
            else:
                j = i - len(self._anzeige)
                text = eingabe_zeilen[j]
                vorher = sum(len(t) for t in eingabe_zeilen[:j])
                p = max(0, min(len(prompt) - vorher, len(text)))
                art = "eingabe"
            self._zeile(flaeche, schriften, text, art, p, innen.left, y)
            y += zh

        if aktiv and cursor_an and self.scroll == 0:
            pos = len(prompt) + self.cursor
            reihe = len(self._anzeige) + pos // spalten - start
            spalte = pos % spalten
            if 0 <= reihe < reihen:
                cx, cy = innen.left + spalte * zb, innen.top + reihe * zh
                pygame.draw.rect(flaeche, FARBE["gruen"], (cx, cy + 2, zb, zh - 4))
                if self.cursor < len(self.eingabe):
                    zeichen = schriften.mono.render(self.eingabe[self.cursor], True, FARBE["terminal"])
                    flaeche.blit(zeichen, (cx, cy))

        if self.scroll:
            hinweis = schriften.klein.render(
                f"  ↑ {self.scroll} Zeilen zurückgeblättert – Bild runter zum Ende  ", True,
                FARBE["warnung_text"], FARBE["warnung"])
            flaeche.blit(hinweis, (rect.right - hinweis.get_width() - rand, rect.bottom - hinweis.get_height() - 4))

    @staticmethod
    def _zeile(flaeche, schriften, text, art, prompt_zeichen, x, y):
        if not text:
            return
        if prompt_zeichen:
            teil = schriften.mono.render(text[:prompt_zeichen], True, FARBE["prompt"])
            flaeche.blit(teil, (x, y))
            x += prompt_zeichen * schriften.zeichen_breite
            text = text[prompt_zeichen:]
            if not text:
                return
        farbe = FARBE[ZEILENART_FARBE.get(art, "ausgabe")]
        font = schriften.mono_fett if art == "erfolg" else schriften.mono
        flaeche.blit(font.render(text, True, farbe), (x, y))


def _zwischenablage() -> str:
    try:
        text = pygame.scrap.get_text()  # pygame-ce
    except (AttributeError, pygame.error):
        return ""
    if not text:
        return ""
    return text.splitlines()[0] if text.splitlines() else ""
