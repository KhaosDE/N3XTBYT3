"""Eine laufende Sitzung: ein Szenario wird gespielt.

Die Sitzung nimmt Eingaben entgegen, sucht den passenden Befehl, ändert den
simulierten Zustand und meldet, wann das Ziel erreicht ist. Sie führt nie einen
echten Befehl aus – jede Ausgabe stammt aus den Szenario-Daten.
"""

from __future__ import annotations

import datetime as _dt
import difflib
import time
from dataclasses import dataclass, field
from typing import Callable

from .befehle import Vergleicher, ist_cmdlet_name, zerlege
from .szenario import Allgemein, Befehl, Szenario
from .zustand import Zustand

# Arten von Zeilen im Terminal
EINGABE = "eingabe"   # Prompt und getippter Befehl
AUSGABE = "ausgabe"   # normale Ausgabe des simulierten Systems
FEHLER = "fehler"     # Fehlerausgabe des simulierten Systems
SIM = "sim"           # Meldung der Simulation (kein echter Systemtext)
ERFOLG = "erfolg"     # Meldung der Simulation: gelöst

SIM_PREFIX = "[N3XTBYT3] "


@dataclass
class Zeile:
    text: str
    art: str = AUSGABE


@dataclass
class Antwort:
    zeilen: list[Zeile] = field(default_factory=list)
    # leer | treffer | falsch | nicht_erkannt | unbekannt
    art: str = "leer"
    geloest_jetzt: bool = False
    aktion: str | None = None
    warum: str | None = None


def _sim(text: str) -> list[Zeile]:
    return [Zeile(SIM_PREFIX + z if i == 0 else " " * len(SIM_PREFIX) + z, SIM)
            for i, z in enumerate(text.split("\n"))]


class Sitzung:
    def __init__(self, szenario: Szenario, allgemein: Allgemein,
                 uhr: Callable[[], float] = time.monotonic):
        self.szenario = szenario
        self.allgemein = allgemein
        self.system = szenario.system
        self.vergleicher = Vergleicher(self.system)
        self.zustand = Zustand({**allgemein.zustand, **szenario.zustand})
        self.shell_stapel: list[str] = [szenario.shell]
        self.hinweis_stufe = 0
        self.geloest = False
        self.falsche: list[str] = []
        self.nicht_erkannt: list[str] = []
        self.unbekannte: list[str] = []
        self.anzahl_befehle = 0
        self.begonnen = _dt.datetime.now().replace(microsecond=0)
        self._uhr = uhr
        self._start = uhr()
        self._ende: float | None = None
        self._bekannte_namen = self._sammle_namen()

    # ------------------------------------------------------------------ Anzeige

    @property
    def shell(self) -> str:
        return self.shell_stapel[-1]

    def prompt(self) -> str:
        vorlage = self.allgemein.prompt.get(self.shell, "> ")
        return self.zustand.fuelle(vorlage)

    def fenstertitel(self) -> str:
        shell = self.system.shell(self.shell)
        return shell.name_admin if self.zustand.get("admin") else shell.name

    def startzeilen(self) -> list[Zeile]:
        return _sim(f"Szenario: {self.szenario.titel}\n"
                    f"Du bist in: {self.fenstertitel()}. Hilfe: help · Hinweis: F1")

    # ------------------------------------------------------------------ Hinweise

    def naechster_hinweis(self) -> str | None:
        if self.hinweis_stufe >= len(self.szenario.hinweise):
            return None
        self.hinweis_stufe += 1
        return self.szenario.hinweise[self.hinweis_stufe - 1]

    @property
    def gezeigte_hinweise(self) -> list[str]:
        return self.szenario.hinweise[: self.hinweis_stufe]

    # ------------------------------------------------------------------ Zeit

    def sekunden(self) -> int:
        ende = self._ende if self._ende is not None else self._uhr()
        return int(round(ende - self._start))

    # ------------------------------------------------------------------ Eingabe

    def _sammle_namen(self) -> dict[str, list[Befehl]]:
        namen: dict[str, list[Befehl]] = {}
        for b in [*self.szenario.befehle, *self.allgemein.befehle]:
            for n in b.namen:
                namen.setdefault(n, []).append(b)
        return namen

    def _finde(self, abschnitte) -> tuple[Befehl | None, Befehl | None]:
        """(Treffer in der aktuellen Shell, Treffer nur in einer anderen Shell)."""
        andere: Befehl | None = None
        for b in [*self.szenario.befehle, *self.allgemein.befehle]:
            if any(self.vergleicher.passt(v, abschnitte) for v in b.vorbereitet):
                if self.shell in b.shells:
                    return b, None
                andere = andere or b
        return None, andere

    def eingabe(self, text: str) -> Antwort:
        text = text.strip()
        if not text:
            return Antwort()
        self.anzahl_befehle += 1
        shell_vorher = self.shell
        antwort = self._auswerten(text)
        # Die echte cmd setzt nach jedem Befehl eine Leerzeile vor den nächsten Prompt.
        if shell_vorher == "cmd" and self.shell == "cmd" and antwort.aktion != "leeren":
            antwort.zeilen.append(Zeile("", AUSGABE))
        return antwort

    def _auswerten(self, text: str) -> Antwort:
        roh_name = zerlege(text)[0][0] if zerlege(text)[0] else ""

        for falle in self.allgemein.shell_fallen:
            if falle.shell == self.shell and roh_name.casefold() == falle.name.casefold():
                self.falsche.append(text)
                return Antwort(_sim(falle.meldung), "falsch", warum=falle.meldung)

        abschnitte = self.vergleicher.vorbereiten(text)
        if not abschnitte or not abschnitte[0].woerter:
            # z. B. nur "|"
            self.unbekannte.append(text)
            return Antwort(_sim("Diese Eingabe ist unvollständig."), "unbekannt")

        treffer, andere = self._finde(abschnitte)
        if treffer:
            return self._ausfuehren(treffer, text)
        if andere:
            return self._andere_shell(andere, text, roh_name)

        name = abschnitte[0].name
        if name in self._bekannte_namen:
            self.nicht_erkannt.append(text)
            return Antwort(_sim(
                f"„{roh_name}“ kennt diese Simulation, aber nicht in dieser Form.\n"
                "Prüfe Parameter und Schreibweise. Weiter kommst du auch mit einem Hinweis (F1)."
            ), "nicht_erkannt")

        self.unbekannte.append(text)
        return Antwort(_sim(self._unbekannt_text(roh_name)), "unbekannt")

    def _unbekannt_text(self, roh_name: str) -> str:
        text = f"In dieser Simulation nicht vorhanden: „{roh_name}“."
        if not self.system.gross_klein_egal:
            gleich = [n for n in self._bekannte_namen if n.casefold() == roh_name.casefold()]
            if gleich:
                return (text + f"\nLinux unterscheidet Groß- und Kleinschreibung. "
                        f"Meintest du „{gleich[0]}“?")
        if self.shell == "cmd" and ist_cmdlet_name(roh_name):
            text += ("\nDer Name sieht aus wie ein PowerShell-Befehl (Verb-Nomen). "
                     "In der cmd gibt es solche Befehle nicht – wechseln mit: powershell")
        aehnlich = difflib.get_close_matches(self.vergleicher.norm_name(roh_name),
                                             list(self._bekannte_namen), n=1, cutoff=0.8)
        if aehnlich:
            return text + f"\nTippfehler? Meintest du „{aehnlich[0]}“?"
        return text + ("\nDas Szenario braucht andere Befehle. Überleg, was zum Problem passt, "
                       "oder hol dir einen Hinweis (F1). Liste der Grundbefehle: help")

    def _andere_shell(self, befehl: Befehl, text: str, roh_name: str) -> Antwort:
        self.falsche.append(text)
        namen = {"powershell": "PowerShell", "cmd": "Eingabeaufforderung (cmd)", "bash": "Bash"}
        ziel = befehl.shells[0]
        hier = namen.get(self.shell, self.shell)
        dort = namen.get(ziel, ziel)
        meldung = f"„{roh_name}“ geht hier in der {dort}, du bist aber in der {hier}."
        if self.shell == "cmd" and ist_cmdlet_name(roh_name):
            meldung += ("\nDie echte cmd meldet dazu: '" + roh_name + "' is not recognized as an "
                        "internal or external command, operable program or batch file.")
        wechsel = "powershell" if ziel == "powershell" else ("cmd" if ziel == "cmd" else ziel)
        meldung += f"\nWechseln mit: {wechsel}"
        return Antwort(_sim(meldung), "falsch", warum=meldung)

    def _ausfuehren(self, befehl: Befehl, text: str) -> Antwort:
        fall = next((f for f in befehl.faelle if self.zustand.erfuellt(f.wenn)), None)
        if fall is None:
            return Antwort(_sim("Für diesen Befehl ist in diesem Zustand keine Ausgabe hinterlegt."),
                           "treffer")
        self.zustand.setze(fall.setze)
        antwort = Antwort(art="treffer", aktion=fall.aktion)
        if fall.ausgabe and fall.sim:
            antwort.zeilen = _sim(self.zustand.fuelle(fall.ausgabe))
        elif fall.ausgabe:
            art = FEHLER if fall.fehler else AUSGABE
            antwort.zeilen = [Zeile(z, art) for z in self.zustand.fuelle(fall.ausgabe).split("\n")]

        if fall.aktion and fall.aktion.startswith("wechsel:"):
            self.shell_stapel.append(fall.aktion.split(":", 1)[1])
            antwort.zeilen += _sim(f"Jetzt in: {self.system.shell(self.shell).name}. "
                                   "Zurück mit: exit")
        elif fall.aktion == "exit":
            if len(self.shell_stapel) > 1:
                self.shell_stapel.pop()
                antwort.zeilen += _sim(f"Zurück in: {self.system.shell(self.shell).name}.")
            else:
                antwort.zeilen += _sim("Hier gibt es kein Fenster zu schließen. "
                                       "Zurück zum Menü: Esc.")
        elif fall.aktion == "hilfe":
            antwort.zeilen += _sim(self.hilfetext())

        if befehl.falsch:
            self.falsche.append(text)
            antwort.art = "falsch"
            antwort.warum = befehl.warum

        if not self.geloest and any(self.zustand.erfuellt(z) for z in self.szenario.ziel):
            self.geloest = True
            self._ende = self._uhr()
            antwort.geloest_jetzt = True
            antwort.zeilen += [Zeile("", AUSGABE)] + [
                Zeile(z.text, ERFOLG) for z in _sim(
                    "Gelöst! Die Erklärung steht rechts. Weiter mit F2.")
            ]
        return antwort

    def hilfetext(self) -> str:
        zeilen = [
            "Hilfe der Simulation (im echten System zeigt „help“ etwas anderes).",
            "Tasten: F1 Hinweis · F2 nächstes Szenario · Esc Menü · Pfeil hoch/runter Verlauf",
            "        Bild hoch/runter blättern · Strg+Plus/Minus Schriftgröße · F11 Vollbild",
            "Grundbefehle, die überall gehen:",
        ]
        for b in self.allgemein.befehle:
            if b.bedeutung and self.shell in b.shells:
                zeilen.append(f"  {b.muster[0]:<20} {b.bedeutung}")
        zeilen.append("Welche Befehle das Problem lösen, findest du selbst heraus – dafür ist das Szenario da.")
        return "\n".join(zeilen)

    # ------------------------------------------------------------------ Ergebnis

    def ergebnis(self) -> dict:
        """Der Versuch als Eintrag für den Spielstand."""
        return {
            "datum": self.begonnen.isoformat(),
            "geloest": self.geloest,
            "hinweise": self.hinweis_stufe,
            "falsche_befehle": len(self.falsche) + len(self.nicht_erkannt),
            "unbekannte_befehle": len(self.unbekannte),
            "befehle": self.anzahl_befehle,
            "sekunden": self.sekunden(),
            "falsch": (self.falsche + self.nicht_erkannt)[:20],
            "unbekannt": self.unbekannte[:20],
        }
