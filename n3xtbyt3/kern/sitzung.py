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
from . import dateisystem as ds
from . import dateisystem_win as dsw
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
    editor: dict | None = None  # Linux: Datei im Editor öffnen (pfad, inhalt, nur_lesen, neu)


def _sim(text: str) -> list[Zeile]:
    return [Zeile(SIM_PREFIX + z if i == 0 else " " * len(SIM_PREFIX) + z, SIM)
            for i, z in enumerate(text.split("\n"))]


class RechnerLauf:
    """Laufzeit-Zustand eines simulierten Rechners innerhalb einer Sitzung."""

    def __init__(self, name: str, system, allgemein: Allgemein, zustand: dict, befehle: list[Befehl],
                 shell: str, zugang: list[str] | None = None, haupt: bool = False):
        self.name = name
        self.system = system
        self.allgemein = allgemein
        self.befehle = befehle
        self.haupt = haupt
        self.vergleicher = Vergleicher(system)
        werte = {**allgemein.zustand, **zustand}
        if not haupt and "powershell" in system.shell_ids and "pfad" not in zustand:
            werte["pfad"] = f"C:\\Users\\{werte.get('benutzer', 'Administrator')}\\Documents"
        self.zustand = Zustand(werte)
        self.shell_stapel: list[str] = [shell]
        self.fs = ds.Dateisystem(self.zustand) if "bash" in system.shell_ids else None
        # Windows: Dateibefehle nur, wenn das Szenario (oder die Lektion) Dateien mitbringt
        self.wfs = dsw.WinDateisystem(self.zustand) if (
            self.fs is None and dsw.WinDateisystem.aktiv_fuer(werte)) else None
        self.root_stapel: list[str] = []
        self.zugang = [self.vergleicher.vorbereiten(z) for z in (zugang or [])]
        self.zugang_text = list(zugang or [])
        self.bekannte_namen: dict[str, list[Befehl]] = {}
        for b in [*befehle, *allgemein.befehle]:
            for n in b.namen:
                self.bekannte_namen.setdefault(n, []).append(b)


class Sitzung:
    def __init__(self, szenario: Szenario, allgemein: Allgemein,
                 uhr: Callable[[], float] = time.monotonic):
        self.szenario = szenario
        haupt = RechnerLauf(szenario.hauptrechner or "start", szenario.system, allgemein, szenario.zustand,
                            szenario.befehle, szenario.shell, haupt=True)
        self.rechner: dict[str, RechnerLauf] = {haupt.name: haupt}
        for name, r in szenario.rechner.items():
            self.rechner[name] = RechnerLauf(name, r.system, r.allgemein, r.zustand, r.befehle, r.shell, r.zugang)
        self.haupt = haupt
        self.rechner_stapel: list[RechnerLauf] = [haupt]
        self.ticket_geschlossen = False
        self.ticket_notiz = ""
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

    # ------------------------------------------------------------------ aktiver Rechner

    @property
    def aktiv(self) -> RechnerLauf:
        return self.rechner_stapel[-1]

    @property
    def system(self):
        return self.aktiv.system

    @property
    def allgemein(self) -> Allgemein:
        return self.aktiv.allgemein

    @property
    def vergleicher(self) -> Vergleicher:
        return self.aktiv.vergleicher

    @property
    def zustand(self) -> Zustand:
        return self.aktiv.zustand

    @property
    def shell_stapel(self) -> list[str]:
        return self.aktiv.shell_stapel

    @property
    def fs(self):
        return self.aktiv.fs

    @property
    def _root_stapel(self) -> list[str]:
        return self.aktiv.root_stapel

    @property
    def _bekannte_namen(self) -> dict[str, list[Befehl]]:
        return self.aktiv.bekannte_namen

    # ------------------------------------------------------------------ Zustand über Rechnergrenzen

    def _verteilen(self, werte: dict | None, standard: RechnerLauf) -> dict[str, tuple[RechnerLauf, dict]]:
        """Teilt Schlüssel mit „rechner:“-Vorsilbe dem richtigen Rechner zu."""
        teile: dict[str, tuple[RechnerLauf, dict]] = {}
        for schluessel, wert in (werte or {}).items():
            lauf, rest = standard, schluessel
            if ":" in schluessel:
                name, rest_kandidat = schluessel.split(":", 1)
                if name in self.rechner:
                    lauf, rest = self.rechner[name], rest_kandidat
            teile.setdefault(lauf.name, (lauf, {}))[1][rest] = wert
        return teile

    def _erfuellt(self, bedingung: dict | None, standard: RechnerLauf | None = None) -> bool:
        if not bedingung:
            return True
        return all(lauf.zustand.erfuellt(teil)
                   for lauf, teil in self._verteilen(bedingung, standard or self.aktiv).values())

    def _setze(self, aenderung: dict | None, standard: RechnerLauf | None = None) -> None:
        for lauf, teil in self._verteilen(aenderung, standard or self.aktiv).values():
            lauf.zustand.setze(teil)

    def ziel_erreicht(self) -> bool:
        return any(self._erfuellt(z, self.haupt) for z in self.szenario.ziel)

    # ------------------------------------------------------------------ Anzeige

    @property
    def shell(self) -> str:
        return self.shell_stapel[-1]

    def prompt(self) -> str:
        vorlage = self.allgemein.prompt.get(self.shell, "> ")
        if self.fs is None:
            if not self.aktiv.haupt and self.shell == "powershell":
                # PowerShell-Remoting zeigt den Rechnernamen vor dem Prompt
                return f"[{str(self.zustand.get('hostname', self.aktiv.name)).upper()}]: " + self.zustand.fuelle(vorlage)
            return self.zustand.fuelle(vorlage)
        werte = dict(self.zustand.werte)
        werte["benutzer_anzeige"] = self.fs.benutzer
        werte["pfad_anzeige"] = self.fs.pfad_anzeige()
        werte["prompt_zeichen"] = "#" if self.zustand.get("root") else "$"
        return Zustand(werte).fuelle(vorlage)

    def fenstertitel(self) -> str:
        shell = self.system.shell(self.shell)
        erhoeht = self.zustand.get("root") if self.fs is not None else self.zustand.get("admin")
        return shell.name_admin if erhoeht else shell.name

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

    def _finde(self, abschnitte) -> tuple[Befehl | None, Befehl | None]:
        """(Treffer in der aktuellen Shell, Treffer nur in einer anderen Shell)."""
        andere: Befehl | None = None
        for b in [*self.aktiv.befehle, *self.allgemein.befehle]:
            for i, v in enumerate(b.vorbereitet):
                if not self.vergleicher.passt(v, abschnitte):
                    continue
                if self.shell in b.shells_fuer(i):
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

        wechsel = self._rechnerwechsel(abschnitte, text)
        if wechsel is not None:
            return wechsel

        treffer, andere = self._finde(abschnitte)
        if treffer:
            return self._ausfuehren(treffer, text)
        if andere:
            return self._andere_shell(andere, text, roh_name)

        if self.fs is not None:
            linux = self._linux(text, abschnitte, roh_name)
            if linux is not None:
                return linux
        if self.aktiv.wfs is not None:
            windows = self._windows_datei(text, abschnitte, roh_name)
            if windows is not None:
                return windows

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
        kandidaten = list(self._bekannte_namen) + (list(ds.EINGEBAUT) if self.fs else []) \
            + (dsw.NAMEN if self.aktiv.wfs else [])
        if not self.system.gross_klein_egal:
            gleich = [n for n in kandidaten if n.casefold() == roh_name.casefold() and n != roh_name]
            if gleich:
                return (text + f"\nLinux unterscheidet Groß- und Kleinschreibung. "
                        f"Meintest du „{gleich[0]}“?")
        aehnlich = difflib.get_close_matches(self.vergleicher.norm_name(roh_name),
                                             kandidaten, n=1, cutoff=0.8)
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

    def _rechnerwechsel(self, abschnitte, text: str) -> Antwort | None:
        """ssh bzw. Enter-PSSession zu einem anderen Rechner des Szenarios."""
        for lauf in self.rechner.values():
            if not lauf.zugang_text:
                continue
            # Verglichen wird nach den Regeln der Shell, in der getippt wird (hier), nicht
            # nach denen des Zielrechners.
            treffer = None
            for z in lauf.zugang_text:
                vorbereitet = self.vergleicher.vorbereiten(z)
                if self.vergleicher.passt(vorbereitet, abschnitte):
                    treffer = vorbereitet
                    break
            if treffer is None:
                continue
            if lauf is self.aktiv:
                return Antwort(_sim(f"Du bist schon auf {lauf.name}."), "treffer")
            if lauf in self.rechner_stapel:
                return Antwort(_sim(f"Du bist schon über {lauf.name} verbunden. Zurück mit exit."), "treffer")
            ist_ps = bool(treffer) and treffer[0].name.casefold() == "enter-pssession"
            if ist_ps and self.shell != "powershell":
                self.falsche.append(text)
                meldung = "Enter-PSSession ist ein PowerShell-Befehl. Wechsle mit „powershell“."
                return Antwort(_sim(meldung), "falsch", warum=meldung)
            self.rechner_stapel.append(lauf)
            zeilen = _sim(f"Verbunden mit {lauf.name} ({lauf.system.name}). Zurück mit exit.")
            return self._ziel_pruefen(Antwort(zeilen, "treffer"))
        return None

    def _ausfuehren(self, befehl: Befehl, text: str) -> Antwort:
        fall = next((f for f in befehl.faelle if self._erfuellt(f.wenn)), None)
        if fall is None:
            return Antwort(_sim("Für diesen Befehl ist in diesem Zustand keine Ausgabe hinterlegt."),
                           "treffer")
        self._setze(fall.setze)
        antwort = Antwort(art="treffer", aktion=fall.aktion)
        if fall.ausgabe and fall.sim:
            antwort.zeilen = _sim(self.zustand.fuelle(fall.ausgabe))
        elif fall.ausgabe:
            art = FEHLER if fall.fehler else AUSGABE
            antwort.zeilen = [Zeile(z, art) for z in self.zustand.fuelle(fall.ausgabe).split("\n")]
        if fall.notiz:
            antwort.zeilen += _sim(self.zustand.fuelle(fall.notiz))

        if fall.aktion and fall.aktion.startswith("wechsel:"):
            self.shell_stapel.append(fall.aktion.split(":", 1)[1])
            antwort.zeilen += _sim(f"Jetzt in: {self.system.shell(self.shell).name}. "
                                   "Zurück mit: exit")
        elif fall.aktion == "exit":
            if self._root_stapel:
                self.zustand.werte["root"] = False
                self.zustand.werte["root_shell"] = False
                self.zustand.werte["pfad"] = self._root_stapel.pop()
                antwort.zeilen += [Zeile("logout", AUSGABE)]
            elif len(self.shell_stapel) > 1:
                self.shell_stapel.pop()
                antwort.zeilen += _sim(f"Zurück in: {self.system.shell(self.shell).name}.")
            elif len(self.rechner_stapel) > 1:
                verlassen = self.rechner_stapel.pop()
                if verlassen.fs is not None:
                    antwort.zeilen += [Zeile("logout", AUSGABE),
                                       Zeile(f"Connection to {verlassen.name} closed.", AUSGABE)]
                antwort.zeilen += _sim(f"Zurück auf {self.aktiv.name}.")
            else:
                antwort.zeilen += _sim("Hier gibt es kein Fenster zu schließen. "
                                       "Zurück zum Menü: Esc.")
        elif fall.aktion == "hilfe":
            antwort.zeilen += _sim(self.hilfetext())

        if befehl.falsch:
            self.falsche.append(text)
            antwort.art = "falsch"
            antwort.warum = befehl.warum

        return self._ziel_pruefen(antwort)

    def _ziel_pruefen(self, antwort: Antwort) -> Antwort:
        if not self.geloest and self.ziel_erreicht():
            self.geloest = True
            self._ende = self._uhr()
            antwort.geloest_jetzt = True
            meldung = ("Problem behoben! Schließe jetzt das Ticket mit F3 (kurze Lösungsnotiz)."
                       if self.szenario.ticket else "Gelöst! Die Erklärung steht rechts. Weiter mit F2.")
            antwort.zeilen += [Zeile("", AUSGABE)] + [Zeile(z.text, ERFOLG) for z in _sim(meldung)]
        return antwort

    def ticket_schliessen(self, notiz: str) -> tuple[bool, str]:
        """Schließt das Ticket. Geht erst, wenn das Problem behoben ist."""
        if not self.szenario.ticket:
            return False, "Dieses Szenario ist kein Ticket."
        if self.ticket_geschlossen:
            return True, "Das Ticket ist schon geschlossen."
        if not self.geloest:
            return False, "Das Problem besteht noch – prüfe nach, bevor du das Ticket schließt."
        if len(notiz.strip()) < 10:
            return False, "Schreib eine kurze Lösungsnotiz (mindestens ein halber Satz): Was war die Ursache, was hast du getan?"
        self.ticket_geschlossen = True
        self.ticket_notiz = notiz.strip()
        return True, f"Ticket {self.szenario.ticket.get('nummer', '')} geschlossen."

    # ------------------------------------------------------------------ Windows-Dateien

    def _windows_datei(self, text: str, abschnitte, roh_name: str) -> Antwort | None:
        name = roh_name.casefold()
        if name not in dsw.BEFEHLE and name not in ("cd..", "cd\\"):
            return None
        if self.shell != "powershell":
            self.nicht_erkannt.append(text)
            return Antwort(_sim("In der cmd sind die Dateibefehle in dieser Simulation nicht nachgebaut. "
                                "Nimm die PowerShell (wechseln mit: powershell)."), "nicht_erkannt")
        if len(abschnitte) >= 2:
            self.nicht_erkannt.append(text)
            return Antwort(_sim("Pipes hinter Dateibefehlen sind in dieser Simulation nicht nachgebaut."),
                           "nicht_erkannt")
        ergebnis = dsw.ausfuehren(self.aktiv.wfs, zerlege(text)[0])
        if ergebnis is None:
            return None
        antwort = Antwort(art="treffer")
        art = FEHLER if ergebnis.fehler else AUSGABE
        antwort.zeilen = [Zeile(z, art) for z in ergebnis.zeilen]
        if ergebnis.sim:
            antwort.zeilen += _sim(ergebnis.sim)
        return self._ziel_pruefen(antwort)

    # ------------------------------------------------------------------ Linux

    def _linux(self, text: str, abschnitte, roh_name: str) -> Antwort | None:
        """sudo, Filter hinter Pipes und eingebaute Dateibefehle. None = nicht zuständig."""
        woerter = zerlege(text)[0]
        if roh_name == "sudo":
            return self._sudo(text, woerter)
        if len(abschnitte) >= 2:
            links, rechts = _an_letzter_pipe(text)
            filter_woerter = zerlege(rechts)[0] if zerlege(rechts) and zerlege(rechts)[0] else []
            if filter_woerter and filter_woerter[0] in ds.FILTER:
                return self._pipe(links, filter_woerter, text)
            self.nicht_erkannt.append(text)
            return Antwort(_sim(f"„{rechts}“ hinter einer Pipe ist hier nicht nachgebaut. "
                                "Es gehen: grep, head, tail, sort, wc -l, less."), "nicht_erkannt")
        befehl = ds.EINGEBAUT.get(roh_name)
        if befehl is None:
            if roh_name in ("vi", "vim"):
                return Antwort(_sim(f"{roh_name} ist hier nicht nachgebaut – nimm nano (Strg+O speichern, Strg+X beenden)."),
                               "treffer")
            return None
        ergebnis = befehl(self.fs, woerter[1:])
        antwort = Antwort(art="treffer")
        art = FEHLER if ergebnis.fehler else AUSGABE
        antwort.zeilen = [Zeile(z, art) for z in ergebnis.zeilen]
        if ergebnis.sim:
            antwort.zeilen += _sim(ergebnis.sim)
        if ergebnis.editor:
            antwort.aktion = "editor"
            antwort.editor = ergebnis.editor
        return self._ziel_pruefen(antwort)

    def _sudo(self, text: str, woerter: list[str]) -> Antwort:
        rest = text.strip()[4:].strip()
        # „sudo sudo -i“ ist dasselbe wie „sudo -i“.
        while woerter[1:2] == ["sudo"]:
            woerter = woerter[1:]
            rest = rest[4:].strip()
        if not self.zustand.get("sudo_erlaubt"):
            return Antwort(_sim(f"{self.zustand.get('benutzer')} hat keine sudo-Rechte (nicht in der Gruppe sudo "
                                "bzw. nicht in der sudoers-Datei)."), "treffer")
        zeilen: list[Zeile] = []
        if not self.zustand.get("root") and not self.zustand.get("sudo_cache"):
            zeilen.append(Zeile(f"[sudo] password for {self.zustand.get('benutzer')}: ", AUSGABE))
            zeilen += _sim("Passwort gilt als eingegeben (sudo merkt es sich einige Minuten).")
            self.zustand.werte["sudo_cache"] = True
        if not rest:
            return Antwort(zeilen + _sim("sudo braucht einen Befehl, z. B. sudo systemctl restart nginx."), "treffer")
        if woerter[1:] in (["-i"], ["su"], ["su", "-"], ["-s"], ["su", "root"]):
            if self.zustand.get("root"):
                return Antwort(zeilen, "treffer")
            self._root_stapel.append(self.fs.cwd)
            self.zustand.werte["root"] = True
            self.zustand.werte["root_shell"] = True
            if woerter[1:] in (["-i"], ["su", "-"]):
                self.zustand.werte["pfad"] = "/root"
            return Antwort(zeilen + _sim("Du bist jetzt root (Prompt endet auf #). Zurück mit: exit"), "treffer")
        if woerter[1] in _SHELL_EINGEBAUT:
            # Eingebaute Befehle der Shell sind keine Programme – sudo findet sie nicht.
            return Antwort(zeilen + [Zeile(f"sudo: {woerter[1]}: command not found", FEHLER)], "treffer")
        # Merken, auf welchem Rechner root gesetzt wird: „sudo ssh …“ wechselt den Rechner.
        zustand = self.zustand
        war_root = bool(zustand.get("root"))
        zustand.werte["root"] = True
        try:
            antwort = self._auswerten(rest)
        finally:
            if not war_root:
                zustand.werte["root"] = False
        antwort.zeilen = zeilen + antwort.zeilen
        return antwort

    def _pipe(self, links: str, filter_woerter: list[str], text: str) -> Antwort:
        # Erst prüfen, ob der Filter in dieser Form nachgebaut ist – sonst gar nichts ausführen.
        _, probe = ds.filter_anwenden(filter_woerter[0], filter_woerter[1:], [])
        if probe == "nicht":
            self.nicht_erkannt.append(text)
            return Antwort(_sim(f"„{' '.join(filter_woerter)}“ hinter einer Pipe ist hier nicht nachgebaut. "
                                "Es gehen: grep, head, tail, sort, wc -l, less."), "nicht_erkannt")
        antwort = self._auswerten(links)
        if antwort.art not in ("treffer",) or antwort.aktion:
            return antwort
        # Nur die normale Ausgabe (stdout) geht durch die Pipe. Fehlermeldungen (stderr)
        # erscheinen trotzdem im Terminal.
        ausgabe = [z.text for z in antwort.zeilen if z.art == AUSGABE]
        fehlerzeilen = [z for z in antwort.zeilen if z.art == FEHLER]
        rest = [z for z in antwort.zeilen if z.art not in (AUSGABE, FEHLER)]
        gefiltert, fehler = ds.filter_anwenden(filter_woerter[0], filter_woerter[1:], ausgabe)
        if fehler:
            neu = fehlerzeilen + [Zeile(fehler, FEHLER)]
        else:
            neu = fehlerzeilen + [Zeile(t, AUSGABE) for t in gefiltert]
        antwort.zeilen = neu + [z for z in rest if z.art != ERFOLG]
        if any(z.art == ERFOLG for z in rest):
            antwort.zeilen += [Zeile("", AUSGABE)] + [z for z in rest if z.art == ERFOLG]
        return antwort

    def loesungsschritt(self, schritt) -> Antwort:
        """Ein Schritt aus „loesung“: Befehl (Text) oder Speichern im Editor ({speichern, inhalt})."""
        if isinstance(schritt, dict):
            return self.datei_speichern(self.fs.absolut(schritt["speichern"]), schritt["inhalt"])
        return self.eingabe(schritt)

    def datei_speichern(self, pfad: str, inhalt: str) -> Antwort:
        """Speichert eine Datei aus dem Editor in den simulierten Zustand."""
        self.fs.schreibe(pfad, inhalt)
        anzahl = len(inhalt.split("\n")) if inhalt else 0
        antwort = Antwort([Zeile(f"[ Wrote {anzahl} line{'s' if anzahl != 1 else ''} ]", AUSGABE)], "treffer")
        return self._ziel_pruefen(antwort)

    def hilfetext(self) -> str:
        zeilen = [
            "Hilfe der Simulation (im echten System zeigt „help“ etwas anderes).",
            "Tasten: F1 Hinweis · F2 weiter · F4 Befehlsbuch · F5 Lexikon · Esc zurück · Pfeil hoch/runter Verlauf",
            "        Bild hoch/runter blättern · Strg+Plus/Minus Schriftgröße · F11 Vollbild",
            "Grundbefehle, die überall gehen:",
        ]
        for b in self.allgemein.befehle:
            if b.bedeutung and self.shell in b.shells:
                zeilen.append(f"  {b.muster[0]:<20} {b.bedeutung}")
        if self.aktiv.wfs is not None and self.shell == "powershell":
            for name, bedeutung in dsw.BEDEUTUNG.items():
                zeilen.append(f"  {name:<20} {bedeutung}")
        if self.fs is not None:
            for name, bedeutung in ds.BEDEUTUNG.items():
                zeilen.append(f"  {name:<20} {bedeutung}")
            zeilen.append("  sudo <befehl>        Befehl als root ausführen · Pipes: … | grep, head, tail, sort, wc -l")
        if self.szenario.kategorie == "Grundkurs":
            zeilen.append("Was als Nächstes dran ist, steht rechts in der Lektion.")
        else:
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
            **({"ticket_geschlossen": self.ticket_geschlossen, "ticket_notiz": self.ticket_notiz}
               if self.szenario.ticket else {}),
        }


# In die Bash eingebaute Befehle: kein eigenes Programm, darum geht „sudo cd …“ nicht.
_SHELL_EINGEBAUT = frozenset({"cd", "exit", "logout", "export", "source", "alias", "history", "umask"})


def _an_letzter_pipe(text: str) -> tuple[str, str]:
    """Teilt die Eingabe an der letzten Pipe außerhalb von Anführungszeichen."""
    quote: str | None = None
    letzte = -1
    for i, zeichen in enumerate(text):
        if quote:
            if zeichen == quote:
                quote = None
        elif zeichen in ("\"", "'"):
            quote = zeichen
        elif zeichen == "|":
            letzte = i
    if letzte < 0:
        return text, ""
    return text[:letzte].strip(), text[letzte + 1:].strip()
