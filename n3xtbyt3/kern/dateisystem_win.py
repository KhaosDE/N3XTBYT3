"""Simuliertes Dateisystem für Windows (nur PowerShell, nur was der Grundkurs braucht).

Dateien stehen im Szenario oder in der Lektion unter ``dateien`` mit Windows-Pfaden
(``C:\\Users\\mberger\\notiz.txt``) und landen – wie unter Linux – als flache Schlüssel im
Zustand: ``datei:<pfad>`` (Inhalt), ``verzeichnis:<pfad>`` (true), ``zeit:<pfad>``
(z. B. ``11/4/2026 09:12``) und ``modus:<pfad>`` (z. B. ``d-r---``).

Windows unterscheidet bei Pfaden nicht zwischen Groß- und Kleinschreibung. Angezeigt wird
immer die Schreibweise aus den Daten.

Eingebaut sind (mit ihren Aliasen aus der Microsoft-Doku, Windows PowerShell 5.1):
Get-Location, Set-Location, Get-ChildItem, Get-Content, New-Item (auch mkdir/md),
Copy-Item, Move-Item, Remove-Item. Das Ausgabeformat von Get-ChildItem folgt den Beispielen
auf learn.microsoft.com. Fehlermeldungen werden auf die erste Zeile gekürzt.
Alles entsteht nur aus den Daten; es wird nie auf echte Dateien zugegriffen.
"""

from __future__ import annotations

import datetime as _dt
import fnmatch
import ntpath
import re
from typing import Any, Callable

from .zustand import Zustand

STANDARD_ZEIT = "11/4/2026 09:12"
_LAUFWERK = re.compile(r"^[A-Za-z]:\\")
_MODUS = re.compile(r"^[d-][a-][r-][h-][s-][l-]$")

QUELLEN = [
    "https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem?view=powershell-5.1",
    "https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-location?view=powershell-5.1",
    "https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-item?view=powershell-5.1",
]


def ist_windows_pfad(pfad: Any) -> bool:
    return isinstance(pfad, str) and bool(_LAUFWERK.match(pfad))


def win_dateien_zu_zustand(roh: Any, ort: str, fehler: list[str]) -> dict[str, Any]:
    """Wandelt das Feld ``dateien`` (Windows-Pfade) in Zustandsschlüssel um."""
    werte: dict[str, Any] = {}
    if roh is None:
        return werte
    if not isinstance(roh, dict):
        fehler.append(f"{ort}: muss ein Objekt sein: „C:\\\\pfad“: Inhalt.")
        return werte
    for pfad, eintrag in roh.items():
        stelle = f"{ort}[{pfad}]"
        if not ist_windows_pfad(pfad):
            fehler.append(f"{stelle}: Windows-Pfade beginnen mit Laufwerk, z. B. „C:\\\\Users\\\\mberger\\\\“.")
            continue
        ist_ordner = pfad.endswith("\\") and len(pfad) > 3
        pfad = ntpath.normpath(pfad)
        if eintrag is None and not ist_ordner:
            werte[f"datei:{pfad}"] = None
            continue
        if isinstance(eintrag, (str, list)) or (eintrag is None and ist_ordner):
            eintrag = {"inhalt": eintrag or ""}
        if not isinstance(eintrag, dict):
            fehler.append(f"{stelle}: Text, Liste von Zeilen oder Objekt mit „inhalt“.")
            continue
        for k in eintrag:
            if k not in ("inhalt", "zeit", "modus") and not k.startswith("_"):
                fehler.append(f"{stelle}: unbekanntes Feld „{k}“ (erlaubt: inhalt, zeit, modus).")
        if ist_ordner:
            werte[f"verzeichnis:{pfad}"] = True
        else:
            inhalt = eintrag.get("inhalt", "")
            if isinstance(inhalt, list) and all(isinstance(z, str) for z in inhalt):
                inhalt = "\n".join(inhalt)
            if not isinstance(inhalt, str):
                fehler.append(f"{stelle}.inhalt: Text oder Liste von Zeilen.")
                inhalt = ""
            werte[f"datei:{pfad}"] = inhalt
        zeit = eintrag.get("zeit")
        if zeit is not None:
            if not isinstance(zeit, str) or not re.match(r"^\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}$", zeit):
                fehler.append(f"{stelle}.zeit: Format M/T/JJJJ HH:MM, z. B. „11/4/2026 09:12“.")
            else:
                werte[f"zeit:{pfad}"] = zeit
        modus = eintrag.get("modus")
        if modus is not None:
            if not isinstance(modus, str) or not _MODUS.match(modus) or (modus[0] == "d") != ist_ordner:
                fehler.append(f"{stelle}.modus: sechs Zeichen wie bei Get-ChildItem, z. B. „-a----“ "
                              "oder „d-r---“ (d nur bei Ordnern).")
            else:
                werte[f"modus:{pfad}"] = modus
    return werte


def _jetzt() -> str:
    j = _dt.datetime.now()
    return f"{j.month}/{j.day}/{j.year} {j.hour:02d}:{j.minute:02d}"


class WinDateisystem:
    """Sicht auf die Windows-Datei-Schlüssel im Zustand einer Sitzung."""

    def __init__(self, zustand: Zustand):
        self.z = zustand

    @staticmethod
    def aktiv_fuer(werte: dict[str, Any]) -> bool:
        return any(k.startswith(("datei:", "verzeichnis:")) and ist_windows_pfad(k.split(":", 1)[1])
                   for k in werte)

    # ------------------------------------------------------------------ Pfade

    @property
    def home(self) -> str:
        return str(self.z.get("home") or f"C:\\Users\\{self.z.get('benutzer', 'Administrator')}")

    @property
    def cwd(self) -> str:
        return str(self.z.get("pfad") or self.home)

    def _index(self) -> dict[str, tuple[str, str]]:
        """casefold(pfad) → (pfad wie in den Daten, "datei" | "ordner"). Elternordner zählen mit."""
        index: dict[str, tuple[str, str]] = {}
        for k, v in self.z.werte.items():
            if k.startswith("datei:") and v is not None:
                pfad, art = k[6:], "datei"
            elif k.startswith("verzeichnis:") and v:
                pfad, art = k[12:], "ordner"
            else:
                continue
            if not ist_windows_pfad(pfad):
                continue
            index[pfad.casefold()] = (pfad, art)
            eltern = ntpath.dirname(pfad)
            while eltern and eltern.casefold() not in index:
                index[eltern.casefold()] = (eltern, "ordner")
                if ntpath.dirname(eltern) == eltern:
                    break
                eltern = ntpath.dirname(eltern)
        for pfad in (self.home, self.cwd):
            index.setdefault(pfad.casefold(), (pfad, "ordner"))
        return index

    def _schreibweise(self, pfad: str) -> str:
        """Schreibweise aus den Daten – auch für Angelegtes, das es (noch) nicht gibt (Wert null/false)."""
        treffer = self._index().get(pfad.casefold())
        if treffer:
            return treffer[0]
        for k in self.z.werte:
            art, _, rest = k.partition(":")
            if art in ("datei", "verzeichnis") and rest.casefold() == pfad.casefold():
                return rest
        eltern, name = ntpath.split(pfad)
        if eltern and eltern != pfad and name:
            treffer = self._index().get(eltern.casefold())
            if treffer:
                return ntpath.join(treffer[0], name)
        return pfad

    def absolut(self, pfad: str) -> str:
        pfad = pfad.replace("/", "\\")
        if pfad == "~" or pfad.startswith("~\\"):
            pfad = self.home + pfad[1:]
        if re.match(r"^[A-Za-z]:$", pfad):
            # „C:“ ohne \ heißt: der aktuelle Ordner auf diesem Laufwerk
            pfad = self.cwd if self.cwd[:2].casefold() == pfad.casefold() else pfad + "\\"
        if pfad.startswith("\\"):
            pfad = self.cwd[:2] + pfad
        elif not _LAUFWERK.match(pfad):
            pfad = ntpath.join(self.cwd, pfad)
        pfad = ntpath.normpath(pfad)
        if re.match(r"^[a-z]:", pfad):
            pfad = pfad[0].upper() + pfad[1:]
        return self._schreibweise(pfad)

    def art(self, pfad: str) -> str | None:
        treffer = self._index().get(pfad.casefold())
        return treffer[1] if treffer else None

    def kinder(self, ordner: str) -> list[tuple[str, str]]:
        """(Pfad, Art) direkt im Ordner: erst Ordner, dann Dateien, je alphabetisch."""
        praefix = ordner.rstrip("\\").casefold() + "\\"
        kinder = [(p, a) for k, (p, a) in self._index().items()
                  if k.startswith(praefix) and "\\" not in k[len(praefix):] and k != praefix]
        return sorted(kinder, key=lambda e: (e[1] != "ordner", ntpath.basename(e[0]).casefold()))

    def inhalt(self, pfad: str) -> str:
        return self.z.get(f"datei:{pfad}") or ""

    def laenge(self, pfad: str) -> int:
        return len(self.inhalt(pfad).replace("\n", "\r\n").encode("utf-8"))

    def modus(self, pfad: str) -> str:
        m = self.z.get(f"modus:{pfad}")
        if m:
            return str(m)
        return "d-----" if self.art(pfad) == "ordner" else "-a----"

    def zeit(self, pfad: str) -> str:
        return str(self.z.get(f"zeit:{pfad}") or STANDARD_ZEIT)

    # ------------------------------------------------------------------ Änderungen

    def _alle_unter(self, pfad: str) -> list[str]:
        """Zustandsschlüssel des Pfads und von allem darunter."""
        p = pfad.casefold()
        ergebnis = []
        for k in self.z.werte:
            if ":" not in k:
                continue
            rest = k.split(":", 1)[1]
            if rest.casefold() == p or rest.casefold().startswith(p.rstrip("\\") + "\\"):
                ergebnis.append(k)
        return ergebnis

    def schreibe(self, pfad: str, inhalt: str) -> None:
        self.z.werte[f"datei:{pfad}"] = inhalt
        self.z.werte[f"zeit:{pfad}"] = _jetzt()

    def neuer_ordner(self, pfad: str) -> None:
        self.z.werte[f"verzeichnis:{pfad}"] = True
        self.z.werte[f"zeit:{pfad}"] = _jetzt()

    def entferne(self, pfad: str) -> None:
        eltern = ntpath.dirname(pfad)
        if eltern != pfad and self.art(eltern) == "ordner":
            # Der Ordner darüber bleibt, auch wenn er nur durch diesen Eintrag bestand.
            self.z.werte[f"verzeichnis:{eltern}"] = True
        for k in self._alle_unter(pfad):
            art = k.split(":", 1)[0]
            if art == "datei":
                self.z.werte[k] = None
            elif art == "verzeichnis":
                self.z.werte[k] = False
            else:
                self.z.werte.pop(k, None)

    def _kopiere_datei(self, quelle: str, ziel: str) -> None:
        # Wie File.Copy: Inhalt, Änderungszeit und Attribute bleiben.
        self.z.werte[f"datei:{ziel}"] = self.inhalt(quelle)
        self.z.werte[f"zeit:{ziel}"] = self.zeit(quelle)
        modus = self.z.get(f"modus:{quelle}")
        if modus:
            self.z.werte[f"modus:{ziel}"] = modus
        else:
            self.z.werte.pop(f"modus:{ziel}", None)

    def kopiere(self, quelle: str, ziel: str, rekursiv: bool = True) -> None:
        if self.art(quelle) == "datei":
            self._kopiere_datei(quelle, ziel)
            return
        unter = [(p, a) for k, (p, a) in self._index().items()
                 if k.startswith(quelle.rstrip("\\").casefold() + "\\")] if rekursiv else []
        self.neuer_ordner(ziel)
        for p, a in sorted(unter, key=lambda e: len(e[0])):
            neu = ziel + p[len(quelle.rstrip("\\")):]
            if a == "ordner":
                self.neuer_ordner(neu)
            else:
                self._kopiere_datei(p, neu)

    def verschiebe(self, quelle: str, ziel: str) -> None:
        """Umbenennen/Verschieben: alles zieht mit um (auch Zeit und Attribute)."""
        war_ordner = self.art(quelle) == "ordner"
        index = self._index()
        alte = {k: self.z.werte[k] for k in self._alle_unter(quelle)}
        # Ordner, die es nur durch ihre Dateien gibt, ausdrücklich mitnehmen
        for k, (p, a) in index.items():
            if a == "ordner" and (k == quelle.casefold() or k.startswith(quelle.rstrip("\\").casefold() + "\\")):
                alte.setdefault(f"verzeichnis:{p}", True)
        if self.art(ziel) is not None:
            self.entferne(ziel)
        self.entferne(quelle)
        laenge = len(quelle.rstrip("\\"))
        for k, v in alte.items():
            art, rest = k.split(":", 1)
            self.z.werte[f"{art}:{ziel}{rest[laenge:]}"] = v
        cwd = self.cwd.casefold()
        if war_ordner and (cwd == quelle.casefold() or cwd.startswith(quelle.rstrip("\\").casefold() + "\\")):
            self.z.werte["pfad"] = ziel + self.cwd[laenge:]


# ---------------------------------------------------------------------- Befehle

class Ergebnis:
    def __init__(self, zeilen: list[str] | None = None, fehler: bool = False, sim: str | None = None):
        self.zeilen = zeilen or []
        self.fehler = fehler
        self.sim = sim
        self.fehler_an: list[bool] | None = None  # je Zeile, wenn Fehler und Ausgabe gemischt sind

    def arten(self) -> list[bool]:
        return list(self.fehler_an) if self.fehler_an is not None else [self.fehler] * len(self.zeilen)


def _parameter(woerter: list[str], bekannte: dict[str, bool]) -> tuple[dict[str, Any], list[str], str | None]:
    """PowerShell-Parameter: -Name Wert oder Schalter. Abkürzungen gehen, wenn eindeutig.

    ``bekannte``: Name → True (Schalter ohne Wert) / False (mit Wert).
    Gibt (benannte, Positionen, unbekannter Parameter) zurück.
    """
    benannt: dict[str, Any] = {}
    positionen: list[str] = []
    i = 0
    while i < len(woerter):
        w = woerter[i]
        if w.startswith("-") and len(w) > 1 and not w[1:].isdigit():
            name = w[1:].rstrip(":").casefold()
            passend = [b for b in bekannte if b.casefold() == name] or \
                      [b for b in bekannte if b.casefold().startswith(name)]
            if len(passend) != 1:
                return benannt, positionen, w
            b = passend[0]
            if bekannte[b]:
                benannt[b] = True
            else:
                if i + 1 >= len(woerter):
                    return benannt, positionen, w
                benannt[b] = woerter[i + 1]
                i += 1
        else:
            positionen.append(w)
        i += 1
    return benannt, positionen, None


def _nicht_nachgebaut(name: str, parameter: str) -> Ergebnis:
    return Ergebnis(sim=f"Den Parameter {parameter} kennt diese Simulation bei {name} nicht "
                        f"(er ist nicht nachgebaut, oder es gibt ihn nicht). Beschreibung aller Parameter: "
                        f"Get-Help {name} -Full (im echten System).")


def _nicht_gefunden(aufruf: str, pfad: str) -> Ergebnis:
    return Ergebnis([f"{aufruf} : Cannot find path '{pfad}' because it does not exist."], fehler=True)


def _tabelle(fs: WinDateisystem, ordner: str, eintraege: list[tuple[str, str]]) -> list[str]:
    zeilen = ["", f"    Directory: {ordner}", "",
              f"{'Mode':<6}{'LastWriteTime':>27}{'Length':>15} Name",
              f"{'----':<6}{'-------------':>27}{'------':>15} ----"]
    for pfad, art in eintraege:
        datum, _, uhr = fs.zeit(pfad).partition(" ")
        laenge = "" if art == "ordner" else str(fs.laenge(pfad))
        zeilen.append(f"{fs.modus(pfad):<6}{datum:>17}{uhr:>10}{laenge:>15} {ntpath.basename(pfad)}")
    return zeilen + [""]


def get_location(fs: WinDateisystem, aufruf: str, woerter: list[str]) -> Ergebnis:
    benannt, pos, unbekannt = _parameter(woerter, {})
    if unbekannt or pos:
        return _nicht_nachgebaut("Get-Location", unbekannt or pos[0])
    return Ergebnis(["", "Path", "----", fs.cwd, ""])


def set_location(fs: WinDateisystem, aufruf: str, woerter: list[str]) -> Ergebnis:
    benannt, pos, unbekannt = _parameter(woerter, {"Path": False, "LiteralPath": False})
    if unbekannt:
        return _nicht_nachgebaut("Set-Location", unbekannt)
    ziel = benannt.get("Path") or benannt.get("LiteralPath") or (pos[0] if pos else None)
    if ziel is None:
        # Set-Location ohne Pfad wechselt in Windows PowerShell 5.1 nicht.
        return Ergebnis()
    pfad = fs.absolut(ziel)
    art = fs.art(pfad)
    if art is None:
        return _nicht_gefunden(aufruf, pfad)
    if art == "datei":
        return Ergebnis(sim=f"„{ntpath.basename(pfad)}“ ist eine Datei, kein Ordner. In Ordner wechseln geht "
                            "nur mit Ordnern – welche es gibt, zeigt Get-ChildItem.")
    fs.z.werte["pfad"] = pfad
    return Ergebnis()


def get_childitem(fs: WinDateisystem, aufruf: str, woerter: list[str]) -> Ergebnis:
    benannt, pos, unbekannt = _parameter(woerter, {"Path": False, "Filter": False, "Name": True,
                                                    "File": True, "Directory": True, "Force": True})
    if unbekannt:
        return _nicht_nachgebaut("Get-ChildItem", unbekannt)
    ziel = benannt.get("Path") or (pos[0] if pos else ".")
    muster = benannt.get("Filter") or (pos[1] if len(pos) > 1 else None)
    pfad = fs.absolut(ziel)
    if fs.art(pfad) is None and any(c in ntpath.basename(pfad) for c in "*?"):
        muster, pfad = ntpath.basename(pfad), ntpath.dirname(pfad)
    art = fs.art(pfad)
    if art is None:
        return _nicht_gefunden(aufruf, pfad)
    if art == "datei":
        eintraege, ordner = [(pfad, "datei")], ntpath.dirname(pfad)
    else:
        eintraege, ordner = fs.kinder(pfad), pfad
    if muster:
        eintraege = [e for e in eintraege if fnmatch.fnmatch(ntpath.basename(e[0]).casefold(), muster.casefold())]
    if art != "datei" and not benannt.get("Force"):
        # Versteckte (h) und Systemdateien (s) zeigt Get-ChildItem nur mit -Force.
        eintraege = [e for e in eintraege if fs.modus(e[0])[3] != "h" and fs.modus(e[0])[4] != "s"]
    if benannt.get("File"):
        eintraege = [e for e in eintraege if e[1] == "datei"]
    if benannt.get("Directory"):
        eintraege = [e for e in eintraege if e[1] == "ordner"]
    if not eintraege:
        return Ergebnis()
    if benannt.get("Name"):
        return Ergebnis([ntpath.basename(p) for p, _ in eintraege])
    return Ergebnis(_tabelle(fs, ordner, eintraege))


def get_content(fs: WinDateisystem, aufruf: str, woerter: list[str]) -> Ergebnis:
    benannt, pos, unbekannt = _parameter(woerter, {"Path": False, "TotalCount": False, "Head": False,
                                                    "First": False, "Tail": False, "Last": False})
    if unbekannt:
        return _nicht_nachgebaut("Get-Content", unbekannt)
    ziel = benannt.get("Path") or (pos[0] if pos else None)
    if ziel is None:
        return Ergebnis(sim="Get-Content braucht den Namen der Datei, z. B. Get-Content notiz.txt.")
    anzahl = benannt.get("TotalCount") or benannt.get("Head") or benannt.get("First")
    ende = benannt.get("Tail") or benannt.get("Last")
    try:
        anzahl = int(anzahl) if anzahl is not None else None
        ende = int(ende) if ende is not None else None
    except ValueError:
        return Ergebnis(sim="Hinter -TotalCount bzw. -Tail gehört eine Zahl, z. B. -Tail 5.")
    # In der Reihenfolge der Pfade: Inhalt bzw. Fehlermeldung (Get-Content a.txt,b.txt oder *.txt)
    eintraege: list[tuple[str, str | None]] = []  # (Pfad, Fehlertext)
    for teil in [t for t in ziel.split(",") if t]:
        pfad = fs.absolut(teil)
        if fs.art(pfad) is None and any(c in ntpath.basename(pfad) for c in "*?"):
            ordner, muster = ntpath.dirname(pfad), ntpath.basename(pfad).casefold()
            eintraege += [(p, None) for p, a in fs.kinder(ordner)
                          if a == "datei" and fnmatch.fnmatch(ntpath.basename(p).casefold(), muster)]
            continue
        art = fs.art(pfad)
        if art is None:
            eintraege.append((pfad, _nicht_gefunden(aufruf, pfad).zeilen[0]))
        elif art == "ordner":
            return Ergebnis(sim=f"„{ntpath.basename(pfad)}“ ist ein Ordner. Get-Content liest nur Dateien; "
                                "was im Ordner liegt, zeigt Get-ChildItem.")
        else:
            eintraege.append((pfad, None))
    erg = Ergebnis()
    erg.fehler_an = []
    for pfad, fehlertext in eintraege:
        if fehlertext:
            erg.zeilen.append(fehlertext)
            erg.fehler_an.append(True)
            continue
        inhalt = fs.inhalt(pfad)
        teil = inhalt.split("\n") if inhalt else []
        if anzahl is not None and anzahl >= 0:  # -TotalCount -1 heißt: alle Zeilen
            teil = teil[:anzahl]
        if ende is not None:
            teil = teil[-ende:] if ende > 0 else ([] if ende == 0 else teil)
        erg.zeilen += teil
        erg.fehler_an += [False] * len(teil)
    erg.fehler = bool(erg.fehler_an) and all(erg.fehler_an)
    return erg


def _neu(fs: WinDateisystem, aufruf: str, pfad: str, ordner: bool, wert: str | None, force: bool) -> Ergebnis:
    eltern = ntpath.dirname(pfad)
    fehlend = []
    while fs.art(eltern) is None and ntpath.dirname(eltern) != eltern:
        fehlend.append(eltern)
        eltern = ntpath.dirname(eltern)
    if fs.art(eltern) == "datei" or (fehlend and not ordner):
        return Ergebnis(sim=f"Den Ordner „{ntpath.dirname(pfad)}“ gibt es nicht. Leg ihn zuerst an oder prüf "
                            "den Pfad (Get-ChildItem zeigt, was da ist).")
    vorhanden = fs.art(pfad)
    if vorhanden == "ordner":
        if ordner and force:
            return Ergebnis(_tabelle(fs, ntpath.dirname(pfad), [(pfad, "ordner")]))
        return Ergebnis([f"{aufruf} : An item with the specified name {pfad} already exists."], fehler=True)
    if vorhanden == "datei" and ordner:
        return Ergebnis([f"{aufruf} : An item with the specified name {pfad} already exists."], fehler=True)
    if vorhanden == "datei" and not force:
        return Ergebnis([f"{aufruf} : The file '{pfad}' already exists."], fehler=True)
    eltern = ntpath.dirname(pfad)
    if ordner:
        # New-Item -ItemType Directory (und mkdir) legen fehlende Ordner davor mit an.
        for f in reversed(fehlend):
            fs.neuer_ordner(f)
        fs.neuer_ordner(pfad)
    else:
        fs.schreibe(pfad, wert or "")
    return Ergebnis(_tabelle(fs, eltern, [(pfad, "ordner" if ordner else "datei")]))


def new_item(fs: WinDateisystem, aufruf: str, woerter: list[str]) -> Ergebnis:
    benannt, pos, unbekannt = _parameter(woerter, {"Path": False, "Name": False, "ItemType": False,
                                                    "Value": False, "Force": True})
    if unbekannt:
        return _nicht_nachgebaut("New-Item", unbekannt)
    pfad_text = benannt.get("Path") or (pos[0] if pos else None)
    name = benannt.get("Name")
    if pfad_text is None and name is None:
        return Ergebnis(sim="New-Item braucht einen Namen, z. B. New-Item -Name notiz.txt -ItemType File "
                            "(die echte PowerShell fragt sonst nach dem Pfad).")
    pfad = fs.absolut(ntpath.join(pfad_text or ".", name) if name else pfad_text)
    typ = str(benannt.get("ItemType", "File")).casefold()
    if typ not in ("file", "directory"):
        return Ergebnis(sim="Hier gehen -ItemType File (Datei) und -ItemType Directory (Ordner).")
    return _neu(fs, aufruf, pfad, typ == "directory", benannt.get("Value"), bool(benannt.get("Force")))


def mkdir(fs: WinDateisystem, aufruf: str, woerter: list[str]) -> Ergebnis:
    benannt, pos, unbekannt = _parameter(woerter, {"Path": False, "Name": False, "Force": True})
    if unbekannt:
        return _nicht_nachgebaut("mkdir", unbekannt)
    pfad_text = benannt.get("Path") or (pos[0] if pos else None)
    name = benannt.get("Name")
    if pfad_text is None and name is None:
        return Ergebnis(sim="mkdir braucht den Namen des neuen Ordners, z. B. mkdir Projekt.")
    pfad = fs.absolut(ntpath.join(pfad_text or ".", name) if name else pfad_text)
    return _neu(fs, aufruf, pfad, True, None, bool(benannt.get("Force")))


def _quelle_ziel(fs: WinDateisystem, name: str, aufruf: str, woerter: list[str],
                 schalter: dict[str, bool]) -> tuple[str, str, dict, Ergebnis | None]:
    benannt, pos, unbekannt = _parameter(woerter, {"Path": False, "Destination": False, **schalter})
    if unbekannt:
        return "", "", benannt, _nicht_nachgebaut(name, unbekannt)
    quelle = benannt.get("Path") or (pos.pop(0) if pos else None)
    ziel = benannt.get("Destination") or (pos.pop(0) if pos else None)
    if quelle is None or ziel is None:
        return "", "", benannt, Ergebnis(sim=f"{name} braucht Quelle und Ziel, z. B. {name} notiz.txt Archiv.")
    q = fs.absolut(quelle)
    if fs.art(q) is None:
        return "", "", benannt, _nicht_gefunden(aufruf, q)
    z = fs.absolut(ziel)
    if fs.art(z) == "ordner":
        z = fs.absolut(ntpath.join(z, ntpath.basename(q)))
    elif fs.art(ntpath.dirname(z)) != "ordner":
        return "", "", benannt, Ergebnis(sim=f"Den Zielordner „{ntpath.dirname(z)}“ gibt es nicht.")
    return q, z, benannt, None


def copy_item(fs: WinDateisystem, aufruf: str, woerter: list[str]) -> Ergebnis:
    q, z, benannt, fehler = _quelle_ziel(fs, "Copy-Item", aufruf, woerter, {"Recurse": True, "Force": True})
    if fehler:
        return fehler
    if q.casefold() == z.casefold():
        return Ergebnis(sim="Quelle und Ziel sind dieselbe Datei.")
    if fs.art(q) == "ordner" and z.casefold().startswith(q.rstrip("\\").casefold() + "\\"):
        return Ergebnis(sim="Ein Ordner kann nicht in sich selbst kopiert werden.")
    rekursiv = bool(benannt.get("Recurse"))
    fs.kopiere(q, z, rekursiv=rekursiv)
    if fs.art(q) == "ordner" and not rekursiv and fs.kinder(q):
        return Ergebnis(sim="Ohne -Recurse kopiert Copy-Item nur den leeren Ordner, nicht seinen Inhalt.")
    return Ergebnis()


def move_item(fs: WinDateisystem, aufruf: str, woerter: list[str]) -> Ergebnis:
    q, z, benannt, fehler = _quelle_ziel(fs, "Move-Item", aufruf, woerter, {"Force": True})
    if fehler:
        return fehler
    if q.casefold() == z.casefold():
        return Ergebnis()
    if fs.art(z) == "datei" and not benannt.get("Force"):
        return Ergebnis([f"{aufruf} : Cannot create a file when that file already exists."], fehler=True)
    if fs.art(q) == "ordner" and z.casefold().startswith(q.casefold() + "\\"):
        return Ergebnis(sim="Ein Ordner kann nicht in sich selbst verschoben werden.")
    fs.verschiebe(q, z)
    return Ergebnis()


def remove_item(fs: WinDateisystem, aufruf: str, woerter: list[str]) -> Ergebnis:
    benannt, pos, unbekannt = _parameter(woerter, {"Path": False, "Recurse": True, "Force": True})
    if unbekannt:
        return _nicht_nachgebaut("Remove-Item", unbekannt)
    ziel = benannt.get("Path") or (pos[0] if pos else None)
    if ziel is None:
        return Ergebnis(sim="Remove-Item braucht den Namen dessen, was weg soll, z. B. Remove-Item alt.txt.")
    pfad = fs.absolut(ziel)
    if fs.art(pfad) is None and any(c in ntpath.basename(pfad) for c in "*?"):
        ordner, muster = ntpath.dirname(pfad), ntpath.basename(pfad).casefold()
        ziele = [p for p, _ in fs.kinder(ordner) if fnmatch.fnmatch(ntpath.basename(p).casefold(), muster)]
        if not ziele:
            return Ergebnis()
    elif fs.art(pfad) is None:
        return _nicht_gefunden(aufruf, pfad)
    else:
        ziele = [pfad]
    for p in ziele:
        if fs.art(p) == "ordner" and fs.kinder(p) and not benannt.get("Recurse"):
            return Ergebnis(sim=f"Der Ordner „{ntpath.basename(p)}“ ist nicht leer. Die echte PowerShell fragt "
                                "jetzt nach, ob alles darin mit gelöscht werden soll (Ja/Nein) – hier wird nichts "
                                "gelöscht. Wenn du sicher bist: Remove-Item <Ordner> -Recurse.")
        if fs.cwd.casefold() == p.casefold() or fs.cwd.casefold().startswith(p.casefold() + "\\"):
            return Ergebnis(sim="Du stehst gerade in diesem Ordner. Wechsle zuerst hinaus (cd ..).")
    for p in ziele:
        fs.entferne(p)
    return Ergebnis()


BEFEHLE: dict[str, Callable[[WinDateisystem, str, list[str]], Ergebnis]] = {}
for _namen, _f in (
    (("Get-Location", "gl", "pwd"), get_location),
    (("Set-Location", "sl", "cd", "chdir"), set_location),
    (("Get-ChildItem", "gci", "ls", "dir"), get_childitem),
    (("Get-Content", "gc", "cat", "type"), get_content),
    (("New-Item", "ni"), new_item),
    (("mkdir", "md"), mkdir),
    (("Copy-Item", "copy", "cp", "cpi"), copy_item),
    (("Move-Item", "move", "mv", "mi"), move_item),
    (("Remove-Item", "del", "erase", "rd", "ri", "rm", "rmdir"), remove_item),
):
    for _n in _namen:
        BEFEHLE[_n.casefold()] = _f

NAMEN = ["Get-Location", "Set-Location", "Get-ChildItem", "Get-Content", "New-Item", "mkdir",
         "Copy-Item", "Move-Item", "Remove-Item"]

BEDEUTUNG = {
    "Get-Location": "Aktuellen Ordner anzeigen (Alias: pwd, gl)",
    "Set-Location": "Ordner wechseln (Alias: cd, sl); cd .. eine Ebene hoch",
    "Get-ChildItem": "Inhalt eines Ordners anzeigen (Alias: dir, ls, gci)",
    "Get-Content": "Inhalt einer Datei anzeigen (Alias: type, cat, gc)",
    "New-Item": "Datei oder Ordner anlegen (-ItemType File/Directory)",
    "mkdir": "Ordner anlegen",
    "Copy-Item": "Kopieren (Alias: copy, cp)",
    "Move-Item": "Verschieben oder umbenennen (Alias: move, mv)",
    "Remove-Item": "Löschen (Alias: del, rm) – ohne Papierkorb!",
}


def ausfuehren(fs: WinDateisystem, woerter: list[str]) -> Ergebnis | None:
    """Führt einen eingebauten Dateibefehl aus. None = kein Dateibefehl."""
    if not woerter:
        return None
    aufruf = woerter[0]
    name = aufruf.casefold()
    # Windows PowerShell kennt „cd..“ und „cd\“ als eigene Funktionen (wie in der cmd).
    if name in ("cd..", "cd\\"):
        return set_location(fs, "Set-Location", [name[2:]] + woerter[1:])
    befehl = BEFEHLE.get(name)
    if befehl is None:
        return None
    # Fehlermeldungen beginnen in Windows PowerShell mit dem Namen, so wie er getippt wurde (z. B. „cd : …“).
    return befehl(fs, aufruf, woerter[1:])
