"""Simuliertes Dateisystem für Linux-Szenarien.

Dateien stehen im Szenario unter ``dateien`` und landen als flache Schlüssel im Zustand:

* ``datei:/pfad``        – Inhalt (Text); ``null`` = existiert (noch) nicht
* ``verzeichnis:/pfad``  – ``true`` für ausdrücklich angelegte (auch leere) Verzeichnisse
* ``rechte:/pfad``       – z. B. ``rw-r--r--``
* ``besitzer:/pfad``     – ``benutzer:gruppe``
* ``zeit:/pfad``         – Änderungszeit für ``ls -l``, z. B. ``Nov  4 09:12``

Verzeichnisse, in denen Dateien liegen, gibt es automatisch.
Allgemeine Befehle, die hier eingebaut sind: pwd, cd, ls, cat, less, head, tail, grep,
chmod, chown, nano (Editor), mkdir, touch, cp, mv, rm – Szenarien können jeden davon mit eigenen Mustern überschreiben.
Alle Ausgaben entstehen nur aus diesen Daten; es wird nie auf echte Dateien zugegriffen.
"""

from __future__ import annotations

import fnmatch
import math
import posixpath
import re
from typing import Any, Callable

from .zustand import Zustand

STANDARD_ZEIT = "Nov  4 09:12"
STANDARD_DATEI_RECHTE = "rw-r--r--"
STANDARD_ORDNER_RECHTE = "rwxr-xr-x"
_OKTAL = re.compile(r"^[0-7]{3,4}$")       # in den Szenario-Daten
_OKTAL_CHMOD = re.compile(r"^[0-7]{1,4}$")  # chmod 0, chmod 1777 …
_RECHTE = re.compile(r"^[r-][w-][xsS-][r-][w-][xsS-][r-][w-][xtT-]$")
_BITS = (0o400, 0o200, 0o100, 0o040, 0o020, 0o010, 0o004, 0o002, 0o001)


def rechte_zu_modus(rechte: str) -> int:
    """„rwsr-xr-x“ → 0o4755."""
    modus = 0
    for i, (zeichen, bit) in enumerate(zip(rechte, _BITS)):
        if (zeichen in "xst") if i % 3 == 2 else zeichen != "-":
            modus |= bit
    if rechte[2] in "sS":
        modus |= 0o4000
    if rechte[5] in "sS":
        modus |= 0o2000
    if rechte[8] in "tT":
        modus |= 0o1000
    return modus


def modus_zu_rechte(modus: int) -> str:
    zeichen = ["rwx"[i % 3] if modus & bit else "-" for i, bit in enumerate(_BITS)]
    for stelle, bit, klein, gross in ((2, 0o4000, "s", "S"), (5, 0o2000, "s", "S"), (8, 0o1000, "t", "T")):
        if modus & bit:
            zeichen[stelle] = klein if zeichen[stelle] == "x" else gross
    return "".join(zeichen)


def oktal_zu_rechte(oktal: str) -> str:
    return modus_zu_rechte(int(oktal, 8))


def rechte_zu_oktal(rechte: str) -> str:
    modus = rechte_zu_modus(rechte)
    return f"{modus:04o}" if modus > 0o777 else f"{modus:03o}"


def dateien_zu_zustand(roh: Any, ort: str, fehler: list[str]) -> dict[str, Any]:
    """Wandelt das Feld ``dateien`` in Zustandsschlüssel um."""
    werte: dict[str, Any] = {}
    if roh is None:
        return werte
    if not isinstance(roh, dict):
        fehler.append(f"{ort}: muss ein Objekt sein: „/pfad“: Inhalt.")
        return werte
    for pfad, eintrag in roh.items():
        stelle = f"{ort}[{pfad}]"
        if not isinstance(pfad, str) or not pfad.startswith("/"):
            fehler.append(f"{stelle}: Pfade beginnen mit „/“.")
            continue
        ist_ordner = pfad.endswith("/") and pfad != "/"
        pfad = posixpath.normpath(pfad)
        if eintrag is None and not ist_ordner:
            werte[f"datei:{pfad}"] = None
            continue
        if isinstance(eintrag, (str, list)):
            eintrag = {"inhalt": eintrag}
        if not isinstance(eintrag, dict):
            fehler.append(f"{stelle}: Text, Liste von Zeilen oder Objekt mit „inhalt“.")
            continue
        for k in eintrag:
            if k not in ("inhalt", "rechte", "besitzer", "zeit") and not k.startswith("_"):
                fehler.append(f"{stelle}: unbekanntes Feld „{k}“.")
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
        rechte = eintrag.get("rechte")
        if rechte is not None:
            if isinstance(rechte, str) and _OKTAL.match(rechte):
                rechte = oktal_zu_rechte(rechte)
            if not isinstance(rechte, str) or not _RECHTE.match(rechte):
                fehler.append(f"{stelle}.rechte: z. B. „rw-r--r--“ oder „644“.")
            else:
                werte[f"rechte:{pfad}"] = rechte
        besitzer = eintrag.get("besitzer")
        if besitzer is not None:
            if not isinstance(besitzer, str) or not re.match(r"^[a-z_][\w-]*:[a-z_][\w-]*$", besitzer):
                fehler.append(f"{stelle}.besitzer: „benutzer:gruppe“, z. B. „root:root“.")
            else:
                werte[f"besitzer:{pfad}"] = besitzer
        zeit = eintrag.get("zeit")
        if zeit is not None:
            if not isinstance(zeit, str):
                fehler.append(f"{stelle}.zeit: Text, z. B. „Nov  4 09:12“.")
            else:
                werte[f"zeit:{pfad}"] = zeit
    return werte


def menschlich(groesse: int) -> str:
    """Größe wie bei ls -h / df -h: aufgerundet, unter 10 mit einer Nachkommastelle.

    Wird beim Aufrunden 10 bzw. 1024 erreicht, gilt die nächste Form (10K, 1.0M) – wie GNU.
    """
    if groesse < 1024:
        return str(groesse)
    wert = float(groesse)
    for einheit in "KMGTPE":
        wert /= 1024
        if wert < 10:
            gerundet = math.ceil(wert * 10) / 10
            if gerundet < 10:
                return f"{gerundet:.1f}{einheit}"
            return f"10{einheit}"
        gerundet_ganz = math.ceil(wert)
        if gerundet_ganz < 1024 or einheit == "E":
            return f"{gerundet_ganz}{einheit}"
    return str(groesse)


class Dateisystem:
    """Sicht auf die Datei-Schlüssel im Zustand einer Sitzung."""

    def __init__(self, zustand: Zustand):
        self.z = zustand
        self.in_pipe = False  # True, solange die Ausgabe in eine Pipe geht (ls: ein Name pro Zeile)

    # ------------------------------------------------------------------ Benutzer

    @property
    def benutzer(self) -> str:
        return "root" if self.z.get("root") else str(self.z.get("benutzer", "root"))

    def gruppen(self) -> set[str]:
        if self.z.get("root"):
            return {"root"}
        gruppen = {self.benutzer}
        extra = self.z.get("gruppen")
        if isinstance(extra, str):
            gruppen.update(g for g in extra.split(",") if g)
        return gruppen

    @property
    def home(self) -> str:
        # Bei „sudo befehl ~/x“ ersetzt die Shell ~ schon vorher – also gilt das Home des Benutzers.
        # Nur in einer echten root-Shell (sudo -i) ist ~ = /root.
        if self.z.get("root_shell"):
            return "/root"
        return str(self.z.get("home") or f"/home/{self.z.get('benutzer', 'root')}")

    @property
    def cwd(self) -> str:
        return str(self.z.get("pfad") or self.home)

    def pfad_anzeige(self) -> str:
        cwd = self.cwd
        if cwd == self.home:
            return "~"
        if cwd.startswith(self.home + "/"):
            return "~" + cwd[len(self.home):]
        return cwd

    def absolut(self, pfad: str) -> str:
        if pfad == "~" or pfad.startswith("~/"):
            pfad = self.home + pfad[1:]
        if not pfad.startswith("/"):
            pfad = posixpath.join(self.cwd, pfad)
        return posixpath.normpath(pfad).replace("//", "/") or "/"

    # ------------------------------------------------------------------ Abfragen

    def _alle_pfade(self) -> list[str]:
        pfade = []
        for k, v in self.z.werte.items():
            if k.startswith("datei:") and v is not None:
                pfade.append(k[6:])
            elif k.startswith("verzeichnis:") and v:
                pfade.append(k[12:])
        return pfade

    def ist_datei(self, pfad: str) -> bool:
        return self.z.get(f"datei:{pfad}") is not None

    def ist_verzeichnis(self, pfad: str) -> bool:
        if pfad in ("/", self.home, self.cwd):
            return True
        if self.z.get(f"verzeichnis:{pfad}"):
            return True
        praefix = pfad.rstrip("/") + "/"
        return any(p.startswith(praefix) for p in self._alle_pfade())

    def existiert(self, pfad: str) -> bool:
        return self.ist_datei(pfad) or self.ist_verzeichnis(pfad)

    def eintraege(self, pfad: str) -> list[str]:
        praefix = pfad.rstrip("/") + "/"
        namen = set()
        kandidaten = self._alle_pfade() + [self.home]
        for p in kandidaten:
            if p.startswith(praefix) and p != pfad:
                namen.add(p[len(praefix):].split("/")[0])
        return sorted(namen, key=lambda n: (n.lstrip(".").casefold(), n))

    def inhalt(self, pfad: str) -> str:
        return self.z.get(f"datei:{pfad}") or ""

    def rechte(self, pfad: str) -> str:
        r = self.z.get(f"rechte:{pfad}")
        if r:
            return r
        if not self.ist_verzeichnis(pfad):
            return STANDARD_DATEI_RECHTE
        if pfad == "/root":
            return "rwx------"  # Debian/Ubuntu: /root nur für root
        if posixpath.dirname(pfad) == "/home":
            return "rwxr-x---"  # Ubuntu ab 21.04: Home-Verzeichnisse 750
        return STANDARD_ORDNER_RECHTE

    def besitzer(self, pfad: str) -> tuple[str, str]:
        b = self.z.get(f"besitzer:{pfad}")
        if not b:
            home = str(self.z.get("home") or "")
            nutzer = str(self.z.get("benutzer", "root"))
            if home and (pfad == home or pfad.startswith(home + "/")) and nutzer != "root":
                return nutzer, nutzer
            return "root", "root"
        u, g = b.split(":", 1)
        return u, g

    def groesse(self, pfad: str) -> int:
        if self.ist_verzeichnis(pfad):
            return 4096
        inhalt = self.inhalt(pfad)
        return len(inhalt.encode("utf-8")) + (1 if inhalt else 0)

    def _darf(self, pfad: str, art: int) -> bool:
        """art: 0 = lesen, 1 = schreiben, 2 = ausführen."""
        if self.z.get("root"):
            return True
        rechte = self.rechte(pfad)
        u, g = self.besitzer(pfad)
        if u == self.benutzer:
            teil = rechte[0:3]
        elif g in self.gruppen():
            teil = rechte[3:6]
        else:
            teil = rechte[6:9]
        return teil[art] not in "-ST"

    def darf_lesen(self, pfad: str) -> bool:
        return self._darf(pfad, 0)

    def darf_schreiben(self, pfad: str) -> bool:
        return self._darf(pfad, 1)

    def darf_betreten(self, pfad: str) -> bool:
        return self._darf(pfad, 2)

    def erreichbar(self, pfad: str) -> bool:
        """Darf der Benutzer alle Verzeichnisse auf dem Weg zu pfad betreten (Recht x)?"""
        if self.z.get("root"):
            return True
        ordner = posixpath.dirname(pfad)
        weg = []
        while ordner not in ("/", ""):
            weg.append(ordner)
            ordner = posixpath.dirname(ordner)
        return all(self.darf_betreten(o) for o in weg if self.ist_verzeichnis(o))

    def sticky_verbietet(self, pfad: str) -> bool:
        """Sticky-Bit (z. B. /tmp): nur Besitzer der Datei oder des Ordners dürfen löschen/umbenennen."""
        if self.z.get("root"):
            return False
        ordner = posixpath.dirname(pfad) or "/"
        if self.rechte(ordner)[8] not in "tT":
            return False
        return self.benutzer not in (self.besitzer(pfad)[0], self.besitzer(ordner)[0])

    def alle_unter(self, pfad: str) -> list[str]:
        """Alle Dateien und Verzeichnisse unterhalb von pfad (ohne pfad selbst), sortiert."""
        praefix = pfad.rstrip("/") + "/"
        gefunden: set[str] = set()
        for p in self._alle_pfade():
            if not p.startswith(praefix):
                continue
            # auch die Ordner dazwischen, die es nur durch ihre Dateien gibt
            while p.startswith(praefix) and p not in gefunden:
                gefunden.add(p)
                p = posixpath.dirname(p)
        gefunden.discard(pfad)
        gefunden.discard("/")
        return sorted(gefunden)

    # ------------------------------------------------------------------ Änderungen

    def schreibe(self, pfad: str, inhalt: str) -> None:
        self.z.werte[f"datei:{pfad}"] = inhalt

    def setze_rechte(self, pfad: str, rechte: str) -> None:
        self.z.werte[f"rechte:{pfad}"] = rechte

    def setze_besitzer(self, pfad: str, besitzer: str) -> None:
        self.z.werte[f"besitzer:{pfad}"] = besitzer


# ---------------------------------------------------------------------- Befehle

class Ergebnis:
    """Ergebnis eines eingebauten Dateibefehls.

    ``fehler`` färbt alle Zeilen als Fehlermeldung. Gemischte Ausgaben (z. B. cat a fehlt b)
    sammeln mit ``aus()`` und ``err()`` – dann zählt die Art je Zeile.
    """

    def __init__(self, zeilen: list[str] | None = None, fehler: bool = False, sim: str | None = None,
                 editor: dict | None = None):
        self.zeilen = zeilen or []
        self.fehler = fehler
        self.sim = sim
        self.editor = editor
        self._arten: list[bool] | None = None

    def _gemischt(self) -> list[bool]:
        if self._arten is None:
            self._arten = [self.fehler] * len(self.zeilen)
        return self._arten

    def aus(self, *zeilen: str) -> None:
        arten = self._gemischt()
        self.zeilen.extend(zeilen)
        arten.extend([False] * len(zeilen))

    def err(self, *zeilen: str) -> None:
        arten = self._gemischt()
        self.zeilen.extend(zeilen)
        arten.extend([True] * len(zeilen))
        self.fehler = True

    def arten(self) -> list[bool]:
        """Je Zeile: True = Fehlermeldung (stderr)."""
        if self._arten is None:
            return [self.fehler] * len(self.zeilen)
        return list(self._arten)


def _optionen(woerter: list[str]) -> tuple[set[str], list[str]]:
    """Trennt kurze Optionen (-la → l, a) von Argumenten."""
    optionen: set[str] = set()
    argumente: list[str] = []
    for w in woerter:
        if w.startswith("--"):
            optionen.add(w)
        elif w.startswith("-") and len(w) > 1 and not w[1:].isdigit():
            optionen.update(w[1:])
        else:
            argumente.append(w)
    return optionen, argumente


def _zeilen(inhalt: str) -> list[str]:
    return inhalt.split("\n") if inhalt else []


def _umask(fs: Dateisystem) -> int:
    # Ubuntu: umask 002 für normale Benutzer (eigene Gruppe), 022 für root
    return 0o022 if fs.z.get("root") else 0o002


# ---------------------------------------------------------------------- Platzhalter der Shell

def _woerter_mit_quote(text: str) -> list[tuple[str, bool]]:
    """Wie zerlege(), aber nur der erste Abschnitt und mit der Info „hatte Anführungszeichen“."""
    woerter: list[tuple[str, bool]] = []
    wort: list[str] = []
    hat_wort = quotiert = False
    quote: str | None = None
    for zeichen in text:
        if quote:
            if zeichen == quote:
                quote = None
            else:
                wort.append(zeichen)
            continue
        if zeichen in ("\"", "'"):
            quote = zeichen
            hat_wort = quotiert = True
        elif zeichen.isspace() or zeichen == "|":
            if hat_wort:
                woerter.append(("".join(wort), quotiert))
                wort, hat_wort, quotiert = [], False, False
            if zeichen == "|":
                break
        else:
            wort.append(zeichen)
            hat_wort = True
    if hat_wort:
        woerter.append(("".join(wort), quotiert))
    return woerter


def _tilde(fs: Dateisystem, wort: str) -> str:
    if not wort.startswith("~"):
        return wort
    name, schraeg, rest = wort[1:].partition("/")
    if name == "":
        basis = fs.home
    elif name == "root":
        basis = "/root"
    elif name == str(fs.z.get("benutzer")):
        basis = str(fs.z.get("home") or f"/home/{name}")
    elif fs.ist_verzeichnis(f"/home/{name}"):
        basis = f"/home/{name}"
    else:
        return wort  # unbekannter Benutzer: die Bash lässt ~name stehen
    return basis + (schraeg + rest if schraeg else "")


def _glob(fs: Dateisystem, muster: str) -> list[str]:
    """Bash-Platzhalter * ? [..] gegen das simulierte Dateisystem. Keine Treffer: leere Liste."""
    absolut = muster.startswith("/")
    teile = [t for t in muster.split("/") if t]
    kandidaten = ["/" if absolut else ""]
    for i, teil in enumerate(teile):
        letzter = i == len(teile) - 1
        neu = []
        for k in kandidaten:
            ordner = fs.absolut(k or ".")
            if not any(c in teil for c in "*?["):
                pfad = (k.rstrip("/") + "/" + teil) if k else teil
                if letzter or fs.ist_verzeichnis(fs.absolut(pfad)):
                    neu.append(pfad)
                continue
            if not fs.ist_verzeichnis(ordner) or not fs.darf_lesen(ordner):
                continue
            for name in fs.eintraege(ordner):
                if name.startswith(".") and not teil.startswith("."):
                    continue
                if fnmatch.fnmatchcase(name, teil):
                    pfad = (k.rstrip("/") + "/" + name) if k else name
                    if letzter or fs.ist_verzeichnis(fs.absolut(pfad)):
                        neu.append(pfad)
        kandidaten = neu
    if muster.endswith("/"):
        kandidaten = [k + "/" for k in kandidaten]
    return [k for k in kandidaten if fs.existiert(fs.absolut(k))]


def erweitere(fs: Dateisystem, text: str) -> list[str]:
    """Die Wörter des ersten Abschnitts, mit ~ und Platzhaltern (*, ?) aufgelöst wie in der Bash.

    Wörter in Anführungszeichen bleiben, wie sie sind. Passt ein Platzhalter auf nichts,
    bleibt er stehen (so macht es die Bash auch).
    """
    ergebnis: list[str] = []
    for i, (wort, quotiert) in enumerate(_woerter_mit_quote(text)):
        if quotiert or i == 0:
            ergebnis.append(wort)
            continue
        wort = _tilde(fs, wort)
        if any(c in wort for c in "*?["):
            treffer = _glob(fs, wort)
            if treffer:
                ergebnis += sorted(treffer, key=lambda n: (n.lstrip(".").casefold(), n))
                continue
        ergebnis.append(wort)
    return ergebnis


# ---------------------------------------------------------------------- pwd, cd, ls

def befehl_pwd(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    return Ergebnis([fs.cwd])


def befehl_cd(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    ziel = woerter[0] if woerter else "~"
    if ziel == "-":
        ziel = str(fs.z.get("pfad_vorher") or fs.cwd)
    pfad = fs.absolut(ziel)
    if not fs.erreichbar(pfad):
        return Ergebnis([f"bash: cd: {ziel}: Permission denied"], fehler=True)
    if fs.ist_datei(pfad):
        return Ergebnis([f"bash: cd: {ziel}: Not a directory"], fehler=True)
    if not fs.ist_verzeichnis(pfad):
        return Ergebnis([f"bash: cd: {ziel}: No such file or directory"], fehler=True)
    if not fs.darf_betreten(pfad):
        return Ergebnis([f"bash: cd: {ziel}: Permission denied"], fehler=True)
    fs.z.werte["pfad_vorher"] = fs.cwd
    fs.z.werte["pfad"] = pfad
    return Ergebnis([pfad] if woerter and woerter[0] == "-" else [])


def _links(fs: Dateisystem, pfad: str) -> int:
    if not fs.ist_verzeichnis(pfad):
        return 1
    return 2 + sum(1 for n in fs.eintraege(pfad) if fs.ist_verzeichnis(posixpath.join(pfad, n)))


def _ls_zeilen(fs: Dateisystem, eintraege: list[tuple[str, str]], mensch: bool) -> list[str]:
    breiten = {"l": 1, "u": 1, "g": 1, "s": 1}
    for p, _ in eintraege:
        u, g = fs.besitzer(p)
        groesse = fs.groesse(p)
        breiten["l"] = max(breiten["l"], len(str(_links(fs, p))))
        breiten["u"] = max(breiten["u"], len(u))
        breiten["g"] = max(breiten["g"], len(g))
        breiten["s"] = max(breiten["s"], len(menschlich(groesse) if mensch else str(groesse)))
    zeilen = []
    for p, name in eintraege:
        typ = "d" if fs.ist_verzeichnis(p) else "-"
        u, g = fs.besitzer(p)
        groesse = fs.groesse(p)
        g_text = menschlich(groesse) if mensch else str(groesse)
        zeit = fs.z.get(f"zeit:{p}") or STANDARD_ZEIT
        zeilen.append(f"{typ}{fs.rechte(p)} {str(_links(fs, p)).rjust(breiten['l'])} {u.ljust(breiten['u'])} "
                      f"{g.ljust(breiten['g'])} {g_text.rjust(breiten['s'])} {zeit} {name}")
    return zeilen


_LS_OPTIONEN = set("laAhd1r")


def befehl_ls(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    optionen: set[str] = set()
    argumente: list[str] = []
    for w in woerter:
        if w in ("--all", "--almost-all", "--human-readable", "--directory", "--reverse"):
            optionen.add({"--all": "a", "--almost-all": "A", "--human-readable": "h",
                          "--directory": "d", "--reverse": "r"}[w])
        elif w.startswith("--color") or w.startswith("--colour"):
            pass
        elif w.startswith("--"):
            optionen.add(w)
        elif w.startswith("-") and len(w) > 1:
            optionen.update(w[1:])
        else:
            argumente.append(w)
    lang, mensch, nur_ordner = "l" in optionen, "h" in optionen, "d" in optionen
    alle, fast_alle, umgekehrt = "a" in optionen, "A" in optionen, "r" in optionen
    # In eine Pipe schreibt ls einen Namen pro Zeile (wie mit -1).
    einzeln = "1" in optionen or getattr(fs, "in_pipe", False)
    erg = Ergebnis()

    def namen_ausgeben(eintraege: list[tuple[str, str]], summe: bool) -> None:
        if umgekehrt:
            eintraege = list(reversed(eintraege))
        if lang:
            if summe:
                bloecke = sum(4 if fs.ist_verzeichnis(p) else math.ceil(fs.groesse(p) / 4096) * 4
                              for p, _ in eintraege)
                erg.aus(f"total {menschlich(bloecke * 1024) if mensch else bloecke}")
            erg.aus(*_ls_zeilen(fs, eintraege, mensch))
        elif einzeln:
            erg.aus(*[n for _, n in eintraege])
        elif eintraege:
            erg.aus("  ".join(n for _, n in eintraege))

    ziele = argumente or ["."]
    dateien: list[tuple[str, str]] = []
    ordner: list[tuple[str, str]] = []
    for ziel in ziele:
        pfad = fs.absolut(ziel)
        if not fs.erreichbar(pfad):
            erg.err(f"ls: cannot access '{ziel}': Permission denied")
        elif not fs.existiert(pfad):
            erg.err(f"ls: cannot access '{ziel}': No such file or directory")
        elif fs.ist_datei(pfad) or nur_ordner:
            dateien.append((pfad, ziel))
        else:
            ordner.append((pfad, ziel))
    dateien.sort(key=lambda e: (e[1].lstrip(".").casefold(), e[1]))
    ordner.sort(key=lambda e: (e[1].lstrip(".").casefold(), e[1]))
    ueberschrift = len(ziele) > 1
    if dateien:
        namen_ausgeben(dateien, summe=False)
    for nr, (pfad, ziel) in enumerate(ordner):
        if dateien or nr:
            erg.aus("")
        if ueberschrift:
            erg.aus(f"{ziel}:")
        if not fs.darf_lesen(pfad):
            erg.err(f"ls: cannot open directory '{ziel}': Permission denied")
            continue
        namen = fs.eintraege(pfad)
        if not (alle or fast_alle):
            namen = [n for n in namen if not n.startswith(".")]
        eintraege = [(posixpath.join(pfad, n), n) for n in namen]
        if alle:
            eintraege = [(pfad, "."), (posixpath.dirname(pfad) or "/", "..")] + eintraege
        namen_ausgeben(eintraege, summe=True)
    fremd = sorted(o for o in optionen if o not in _LS_OPTIONEN and not o.startswith("--"))
    fremd_lang = sorted(o for o in optionen if o.startswith("--"))
    if fremd or fremd_lang:
        liste = ", ".join([f"-{o}" for o in fremd] + fremd_lang)
        erg.sim = (f"ls: {liste} ist hier nicht nachgebaut – gezeigt wird die normale Liste "
                   "(sortiert nach Namen). Nachgebaut: -l -a -A -h -d -1 -r")
    if erg.zeilen and all(erg.arten()):
        erg.fehler = True
    return erg


# ---------------------------------------------------------------------- Lesen: cat, less, head, tail

def _lesbar(fs: Dateisystem, befehl: str, ziel: str) -> tuple[str | None, Ergebnis | None]:
    pfad = fs.absolut(ziel)
    if not fs.erreichbar(pfad):
        return None, Ergebnis([f"{befehl}: {ziel}: Permission denied"], fehler=True)
    if fs.ist_verzeichnis(pfad):
        return None, Ergebnis([f"{befehl}: {ziel}: Is a directory"], fehler=True)
    if not fs.ist_datei(pfad):
        return None, Ergebnis([f"{befehl}: {ziel}: No such file or directory"], fehler=True)
    if not fs.darf_lesen(pfad):
        return None, Ergebnis([f"{befehl}: {ziel}: Permission denied"], fehler=True)
    return pfad, None


def _fehler_nur(ergebnis: Ergebnis) -> Ergebnis:
    """Färbt rot, wenn alle Zeilen Fehler sind (sonst bleibt die Art je Zeile)."""
    if ergebnis.zeilen and all(ergebnis.arten()):
        ergebnis.fehler = True
    return ergebnis


def befehl_cat(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    optionen, argumente = _optionen(woerter)
    if not argumente:
        return Ergebnis(sim="cat ohne Datei liest von der Tastatur – das ist hier nicht nachgebaut.")
    erg = Ergebnis()
    nr = 0
    for ziel in argumente:
        pfad, fehler = _lesbar(fs, "cat", ziel)
        if fehler:
            erg.err(*fehler.zeilen)
            continue
        teile = _zeilen(fs.inhalt(pfad))
        if "n" in optionen:
            teile = [f"{i:6}\t{z}" for i, z in enumerate(teile, start=nr + 1)]
            nr += len(teile)
        erg.aus(*teile)
    return _fehler_nur(erg)


class _KopfFehler(Exception):
    pass


def _kopf_optionen(name: str, woerter: list[str]) -> dict:
    """Optionen von head/tail: -n N, -N, -n +N/-N, --lines=N, -c N, --bytes=N, -f, -q, -v."""
    werte = {"n": 10, "zeichen": "", "bytes": False, "folgen": False, "still": False, "laut": False,
             "dateien": []}

    def zahl(text: str | None, bytes_: bool) -> None:
        m = re.fullmatch(r"([+-]?)(\d+)", text or "")
        if not m:
            art = "bytes" if bytes_ else "lines"
            raise _KopfFehler(f"{name}: invalid number of {art}: '{text}'")
        werte["zeichen"], werte["n"], werte["bytes"] = m.group(1), int(m.group(2)), bytes_

    i = 0
    while i < len(woerter):
        w = woerter[i]
        lang = re.fullmatch(r"--(lines|bytes)=(.*)", w)
        if lang:
            zahl(lang.group(2), lang.group(1) == "bytes")
        elif w in ("--lines", "--bytes"):
            i += 1
            zahl(woerter[i] if i < len(woerter) else None, w == "--bytes")
        elif w in ("--follow", "-F") and name == "tail":
            werte["folgen"] = True
        elif w in ("--quiet", "--silent"):
            werte["still"] = True
        elif w == "--verbose":
            werte["laut"] = True
        elif w.startswith("--"):
            raise KeyError(w)
        elif re.fullmatch(r"-\d+", w):
            werte["n"], werte["zeichen"], werte["bytes"] = int(w[1:]), "", False
        elif w.startswith("-") and len(w) > 1:
            j = 1
            while j < len(w):
                c = w[j]
                if c in "nc":
                    rest = w[j + 1:]
                    if not rest:
                        i += 1
                        rest = woerter[i] if i < len(woerter) else None
                    zahl(rest, c == "c")
                    break
                if c == "f" and name == "tail":
                    werte["folgen"] = True
                elif c == "q":
                    werte["still"] = True
                elif c == "v":
                    werte["laut"] = True
                else:
                    raise KeyError(c)
                j += 1
        else:
            werte["dateien"].append(w)
        i += 1
    return werte


def _kopf_anwenden(name: str, werte: dict, zeilen: list[str]) -> list[str]:
    n, zeichen = werte["n"], werte["zeichen"]
    if werte["bytes"]:
        daten = ("\n".join(zeilen) + "\n" if zeilen else "").encode("utf-8")
        if name == "head":
            teil = daten[:-n] if zeichen == "-" else daten[:n]
        else:
            teil = daten[max(n - 1, 0):] if zeichen == "+" else (daten[-n:] if n else b"")
        text = teil.decode("utf-8", errors="ignore")
        if text.endswith("\n"):
            text = text[:-1]
        return text.split("\n") if teil else []
    if name == "head":
        if zeichen == "-":
            return zeilen[:-n] if n else list(zeilen)  # head -n -N: alles außer den letzten N
        return zeilen[:n]
    if zeichen == "+":
        return zeilen[max(n - 1, 0):]
    return zeilen[-n:] if n else []


def filter_head(zeilen: list[str], woerter: list[str]) -> list[str]:
    return _kopf_anwenden("head", _kopf_optionen("head", woerter), zeilen)


def filter_tail(zeilen: list[str], woerter: list[str]) -> list[str]:
    return _kopf_anwenden("tail", _kopf_optionen("tail", woerter), zeilen)


def befehl_head_tail(name: str) -> Callable[[Dateisystem, list[str]], Ergebnis]:
    def befehl(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
        try:
            werte = _kopf_optionen(name, woerter)
        except _KopfFehler as e:
            return Ergebnis([str(e)], fehler=True)
        except KeyError as e:
            return Ergebnis(sim=f"Die Option „{e.args[0]}“ von {name} ist hier nicht nachgebaut. "
                                "Nachgebaut: -n (Anzahl, auch +N/-N), -c, -q, -v" + (", -f" if name == "tail" else ""))
        dateien = werte["dateien"]
        if not dateien:
            return Ergebnis(sim=f"{name} ohne Datei liest von der Tastatur – das ist hier nicht nachgebaut.")
        kopf = (len(dateien) > 1 or werte["laut"]) and not werte["still"]
        erg = Ergebnis()
        erstes = True
        for ziel in dateien:
            pfad, fehler = _lesbar(fs, name, ziel)
            if fehler:
                grund = fehler.zeilen[0].rsplit(": ", 1)[1]
                if grund == "Is a directory":
                    erg.err(f"{name}: error reading '{ziel}': Is a directory")
                else:
                    erg.err(f"{name}: cannot open '{ziel}' for reading: {grund}")
                continue
            if kopf:
                if not erstes:
                    erg.aus("")
                erg.aus(f"==> {ziel} <==")
            erstes = False
            erg.aus(*_kopf_anwenden(name, werte, _zeilen(fs.inhalt(pfad))))
        if name == "tail" and werte["folgen"]:
            erg.sim = ("tail -f wartet danach auf neue Zeilen (Strg+C zum Beenden) – "
                       "hier werden nur die letzten Zeilen gezeigt.")
        return _fehler_nur(erg)
    return befehl


def befehl_less(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    ergebnis = befehl_cat(fs, [w for w in woerter if not w.startswith("-")])
    if not ergebnis.fehler and ergebnis.zeilen:
        ergebnis.sim = "less zeigt die Datei seitenweise (q beendet). Hier steht der ganze Inhalt im Terminal."
    return ergebnis


# ---------------------------------------------------------------------- grep

_KLASSEN = {"digit": "0-9", "alpha": "A-Za-z", "alnum": "A-Za-z0-9", "upper": "A-Z", "lower": "a-z",
            "space": r" \t\n\r\f\v", "blank": r" \t", "punct": r"!-/:-@\[-`{-~", "xdigit": "0-9A-Fa-f"}


def _klammer(muster: str, i: int) -> tuple[str, int]:
    """Eine Klammer-Liste [..] (POSIX) ab Stelle i in Python-Schreibweise."""
    j = i + 1
    teile = ["["]
    if j < len(muster) and muster[j] == "^":
        teile.append("^")
        j += 1
    if j < len(muster) and muster[j] == "]":
        teile.append(r"\]")
        j += 1
    while j < len(muster) and muster[j] != "]":
        if muster.startswith("[:", j):
            ende = muster.find(":]", j + 2)
            if ende < 0 or muster[j + 2:ende] not in _KLASSEN:
                raise re.error("Klasse")
            teile.append(_KLASSEN[muster[j + 2:ende]])
            j = ende + 2
            continue
        c = muster[j]
        teile.append("\\" + c if c in "\\[&~|" else c)  # in POSIX-Klammern ist \ ein normales Zeichen
        j += 1
    if j >= len(muster):
        raise re.error("Klammer offen")
    teile.append("]")
    return "".join(teile), j + 1


def _regex_aus(muster: str, erweitert: bool) -> str:
    """POSIX-Muster (BRE wie grep, ERE wie grep -E) in Python-Regex übersetzen."""
    aus: list[str] = []
    i = 0
    sonder_bre = "|+?(){}"
    while i < len(muster):
        c = muster[i]
        if c == "\\" and i + 1 < len(muster):
            n = muster[i + 1]
            if n in "<>":
                aus.append(r"\b")
            elif n in "wWsSb" or n.isdigit():
                aus.append("\\" + n)
            elif not erweitert and n in sonder_bre:
                aus.append("(" if n == "(" else n)
            else:
                aus.append(re.escape(n))
            i += 2
            continue
        if c == "[":
            teil, i = _klammer(muster, i)
            aus.append(teil)
            continue
        anfang = not aus or aus[-1] in ("^", "(", "|")
        if erweitert:
            if c in "*+?" and anfang:
                aus.append("\\" + c)
            elif c == "{" and not re.match(r"\{\d+(,\d*)?\}", muster[i:]):
                aus.append(r"\{")
            elif c in ".^$()|*+?{}":
                aus.append(c)
            else:
                aus.append(re.escape(c))
        else:
            if c in sonder_bre:
                aus.append("\\" + c)
            elif c == "*" and anfang:
                aus.append(r"\*")
            elif c == "^" and not anfang:
                aus.append(r"\^")
            elif c == "$" and i != len(muster) - 1 and not muster.startswith(("\\)", "\\|"), i + 1):
                aus.append(r"\$")
            elif c in ".*^$":
                aus.append(c)
            else:
                aus.append(re.escape(c))
        i += 1
    return "".join(aus)


_GREP_SCHALTER = set("ivncEFGwxolLrRhHsqy")
_GREP_WERT = set("ABCme")
_GREP_LANG = {"--ignore-case": "i", "--invert-match": "v", "--line-number": "n", "--count": "c",
              "--extended-regexp": "E", "--fixed-strings": "F", "--basic-regexp": "G",
              "--word-regexp": "w", "--line-regexp": "x", "--only-matching": "o",
              "--files-with-matches": "l", "--files-without-match": "L", "--recursive": "r",
              "--dereference-recursive": "R", "--no-filename": "h", "--with-filename": "H",
              "--no-messages": "s", "--quiet": "q", "--silent": "q"}


def _grep_optionen(woerter: list[str]) -> tuple[set[str], dict, list[str], list[str]]:
    """(Schalter, Werte, Muster, Dateien). KeyError = nicht nachgebaute Option."""
    schalter: set[str] = set()
    werte: dict = {"e": []}
    rest: list[str] = []
    i = 0
    while i < len(woerter):
        w = woerter[i]
        if w == "--":
            rest += woerter[i + 1:]
            break
        if w.startswith("--"):
            name, gleich, wert = w.partition("=")
            if name in _GREP_LANG:
                schalter.add(_GREP_LANG[name])
            elif name in ("--color", "--colour"):
                pass
            elif name in ("--after-context", "--before-context", "--context", "--max-count", "--regexp"):
                if not gleich:
                    i += 1
                    wert = woerter[i] if i < len(woerter) else ""
                k = {"--after-context": "A", "--before-context": "B", "--context": "C",
                     "--max-count": "m", "--regexp": "e"}[name]
                werte["e"].append(wert) if k == "e" else werte.__setitem__(k, wert)
            else:
                raise KeyError(w)
        elif w.startswith("-") and len(w) > 1:
            j = 1
            while j < len(w):
                c = w[j]
                if c in _GREP_WERT:
                    wert = w[j + 1:]
                    if not wert:
                        i += 1
                        wert = woerter[i] if i < len(woerter) else ""
                    werte["e"].append(wert) if c == "e" else werte.__setitem__(c, wert)
                    break
                if c not in _GREP_SCHALTER:
                    raise KeyError(f"-{c}")
                schalter.add("i" if c == "y" else c)
                j += 1
        else:
            rest.append(w)
        i += 1
    muster = werte.pop("e")
    if not muster and rest:
        muster = [rest.pop(0)]
    return schalter, werte, muster, rest


def _grep_regex(muster: list[str], schalter: set[str]):
    teile = []
    for m in muster:
        if "F" in schalter:
            teile.append(re.escape(m))
        else:
            teile.append(_regex_aus(m, erweitert="E" in schalter))
    ausdruck = "|".join(f"(?:{t})" for t in teile)
    if "x" in schalter:
        ausdruck = f"^(?:{ausdruck})$"
    elif "w" in schalter:
        ausdruck = rf"(?<!\w)(?:{ausdruck})(?!\w)"
    return re.compile(ausdruck, re.IGNORECASE if "i" in schalter else 0)


def _grep_datei(zeilen: list[str], regex, schalter: set[str], werte: dict, name: str | None) -> list[str]:
    """Ausgabe für eine Quelle. name = Dateiname als Präfix (oder None)."""
    umkehren = "v" in schalter
    treffer = [i for i, z in enumerate(zeilen) if bool(regex.search(z)) != umkehren]
    if "m" in werte:
        treffer = treffer[:int(werte["m"])]
    vorne = f"{name}:" if name is not None else ""
    if "c" in schalter:
        return [f"{vorne}{len(treffer)}"]
    if "l" in schalter or "L" in schalter:
        if bool(treffer) == ("l" in schalter):
            return [name if name is not None else "(standard input)"]
        return []
    if "q" in schalter:
        return []

    def zeile(i: int, trenner: str) -> str:
        nr = f"{i + 1}{trenner}" if "n" in schalter else ""
        kopf = f"{name}{trenner}" if name is not None else ""
        return f"{kopf}{nr}{zeilen[i]}"

    if "o" in schalter:
        aus = []
        if umkehren:
            return []
        for i in treffer:
            for m in regex.finditer(zeilen[i]):
                if m.group(0):
                    nr = f"{i + 1}:" if "n" in schalter else ""
                    aus.append(f"{vorne}{nr}{m.group(0)}")
        return aus
    nach = int(werte.get("A", werte.get("C", 0)) or 0)
    vor = int(werte.get("B", werte.get("C", 0)) or 0)
    if not (nach or vor):
        return [zeile(i, ":") for i in treffer]
    aus: list[str] = []
    gezeigt = -1
    ist_treffer = set(treffer)
    for i in treffer:
        von, bis = max(i - vor, 0), min(i + nach, len(zeilen) - 1)
        if gezeigt >= 0 and von > gezeigt + 1:
            aus.append("--")
        for k in range(max(von, gezeigt + 1), bis + 1):
            aus.append(zeile(k, ":" if k in ist_treffer else "-"))
        gezeigt = max(gezeigt, bis)
    return aus


def filter_grep(zeilen: list[str], woerter: list[str]) -> tuple[list[str], str | None]:
    """grep hinter einer Pipe. Gibt (Treffer, Fehlertext) zurück; Fehlertext "nicht" = nicht nachgebaut."""
    try:
        schalter, werte, muster, _ = _grep_optionen(woerter)
    except KeyError:
        return [], "nicht"
    if not muster:
        return [], "Usage: grep [OPTION]... PATTERNS [FILE]..."
    if {"r", "R"} & schalter:
        return [], "nicht"
    try:
        regex = _grep_regex(muster, schalter)
        for k in ("A", "B", "C", "m"):
            if k in werte:
                int(werte[k])
    except (re.error, ValueError):
        return [], "nicht"
    return _grep_datei(zeilen, regex, schalter, werte, "(standard input)" if "H" in schalter else None), None


def befehl_grep(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    try:
        schalter, werte, muster, dateien = _grep_optionen(woerter)
    except KeyError as e:
        return Ergebnis(sim=f"Die grep-Option „{e.args[0]}“ ist hier nicht nachgebaut. Nachgebaut: "
                            "-i -v -n -c -E -F -w -x -o -l -L -r -h -H -s -q -A -B -C -m -e")
    rekursiv = bool({"r", "R"} & schalter)
    if not muster or (not dateien and not rekursiv):
        return Ergebnis(sim="grep braucht hier ein Suchmuster und eine Datei, z. B. grep error /var/log/syslog "
                            "(oder hinter einer Pipe: … | grep error).")
    try:
        regex = _grep_regex(muster, schalter)
        for k in ("A", "B", "C", "m"):
            if k in werte:
                int(werte[k])
    except (re.error, ValueError):
        return Ergebnis(sim="Dieses Suchmuster bzw. diese Zahl kann die Simulation nicht auswerten.")
    quellen: list[tuple[str, str | None]] = []  # (Anzeigename, Pfad oder None bei Fehler)
    erg = Ergebnis()
    leise = "s" in schalter
    if rekursiv and not dateien:
        dateien = ["."]
        ohne_punkt = True
    else:
        ohne_punkt = False
    for ziel in dateien:
        pfad = fs.absolut(ziel)
        if rekursiv and fs.ist_verzeichnis(pfad) and fs.erreichbar(pfad):
            for unter in fs.alle_unter(pfad):
                if fs.ist_datei(unter):
                    rel = unter[len(pfad.rstrip("/")) + 1:]
                    quellen.append((rel if ohne_punkt else posixpath.join(ziel, rel), unter))
            continue
        quellen.append((ziel, None))
    mehrere = (len(quellen) > 1 or rekursiv) and "h" not in schalter or "H" in schalter
    for anzeige, pfad in quellen:
        if pfad is None:
            pfad, fehler = _lesbar(fs, "grep", anzeige)
            if fehler:
                if not leise:
                    erg.err(fehler.zeilen[0])
                continue
        elif not fs.darf_lesen(pfad) or not fs.erreichbar(pfad):
            if not leise:
                erg.err(f"grep: {anzeige}: Permission denied")
            continue
        erg.aus(*_grep_datei(_zeilen(fs.inhalt(pfad)), regex, schalter, werte,
                             anzeige if mehrere else None))
    return _fehler_nur(erg)


# ---------------------------------------------------------------------- chmod, chown

_SYMBOLISCH = re.compile(r"[ugoa]*(?:[-+=][rwxXst]*)+")


def _ist_modus(wort: str) -> bool:
    return bool(_OKTAL_CHMOD.match(wort)) or all(_SYMBOLISCH.fullmatch(k) for k in wort.split(","))


def _neuer_modus(modus_text: str, alt: int, ordner: bool, umask: int) -> int:
    if _OKTAL_CHMOD.match(modus_text):
        neu = int(modus_text, 8)
        if ordner and len(modus_text) <= 4:
            neu |= alt & 0o6000  # GNU: bei Ordnern bleiben setuid/setgid ohne 5. Ziffer erhalten
        return neu
    modus = alt
    for klausel in modus_text.split(","):
        wer_text = re.match(r"[ugoa]*", klausel).group(0)
        ohne_wer = not wer_text
        wer = "ugo" if not wer_text or "a" in wer_text else wer_text
        for op, rechte in re.findall(r"([-+=])([rwxXst]*)", klausel[len(wer_text):]):
            bits = 0
            for teil in wer:
                schieben = {"u": 6, "g": 3, "o": 0}[teil]
                for r in rechte:
                    if r == "r":
                        bits |= 4 << schieben
                    elif r == "w":
                        bits |= 2 << schieben
                    elif r == "x" or (r == "X" and (ordner or modus & 0o111)):
                        bits |= 1 << schieben
                    elif r == "s" and teil in "ug":
                        bits |= 0o4000 if teil == "u" else 0o2000
                    elif r == "t" and teil == "o":
                        bits |= 0o1000
            if ohne_wer:
                bits &= ~umask  # ohne u/g/o/a gilt die umask (GNU)
            if op == "+":
                modus |= bits
            elif op == "-":
                modus &= ~bits
            else:
                loeschen = 0
                for teil in wer:
                    loeschen |= 7 << {"u": 6, "g": 3, "o": 0}[teil]
                if not ordner:
                    loeschen |= (0o4000 if "u" in wer else 0) | (0o2000 if "g" in wer else 0)
                if "o" in wer:
                    loeschen |= 0o1000
                modus = (modus & ~loeschen) | bits
    return modus


def _mit_unterpfaden(fs: Dateisystem, ziel: str, pfad: str, rekursiv: bool) -> list[tuple[str, str]]:
    eintraege = [(ziel, pfad)]
    if rekursiv and fs.ist_verzeichnis(pfad):
        basis = pfad.rstrip("/")
        eintraege += [(posixpath.join(ziel, p[len(basis) + 1:]), p) for p in fs.alle_unter(pfad)]
    return eintraege


def befehl_chmod(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    optionen: set[str] = set()
    modus: str | None = None
    dateien: list[str] = []
    for w in woerter:
        if w == "--recursive":
            optionen.add("R")
        elif w.startswith("--"):
            optionen.add(w)
        elif modus is None and w.startswith("-") and _ist_modus(w):
            modus = w  # chmod -x datei: „-x“ ist der Modus, keine Option
        elif w.startswith("-") and len(w) > 1:
            optionen.update(w[1:])
        elif modus is None:
            modus = w
        else:
            dateien.append(w)
    hilfe = "Try 'chmod --help' for more information."
    if modus is None:
        return Ergebnis(["chmod: missing operand", hilfe], fehler=True)
    if not dateien:
        return Ergebnis([f"chmod: missing operand after '{modus}'", hilfe], fehler=True)
    if not _ist_modus(modus):
        return Ergebnis([f"chmod: invalid mode: '{modus}'", hilfe], fehler=True)
    zeilen: list[str] = []
    for ziel in dateien:
        pfad = fs.absolut(ziel)
        if not fs.erreichbar(pfad):
            zeilen.append(f"chmod: cannot access '{ziel}': Permission denied")
            continue
        if not fs.existiert(pfad):
            zeilen.append(f"chmod: cannot access '{ziel}': No such file or directory")
            continue
        for anzeige, p in _mit_unterpfaden(fs, ziel, pfad, "R" in optionen):
            if not fs.z.get("root") and fs.besitzer(p)[0] != fs.benutzer:
                zeilen.append(f"chmod: changing permissions of '{anzeige}': Operation not permitted")
                continue
            alt = rechte_zu_modus(fs.rechte(p))
            neu = _neuer_modus(modus, alt, fs.ist_verzeichnis(p), _umask(fs))
            fs.setze_rechte(p, modus_zu_rechte(neu))
    return Ergebnis(zeilen, fehler=bool(zeilen))


def befehl_chown(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    optionen, argumente = _optionen(woerter)
    if len(argumente) < 2:
        return Ergebnis(["chown: missing operand" if not argumente
                         else f"chown: missing operand after '{argumente[0]}'",
                         "Try 'chown --help' for more information."], fehler=True)
    neu, dateien = argumente[0], argumente[1:]
    u, doppelpunkt, g = neu.partition(":")
    zeilen: list[str] = []
    for ziel in dateien:
        pfad = fs.absolut(ziel)
        if not fs.erreichbar(pfad):
            zeilen.append(f"chown: cannot access '{ziel}': Permission denied")
            continue
        if not fs.existiert(pfad):
            zeilen.append(f"chown: cannot access '{ziel}': No such file or directory")
            continue
        for anzeige, p in _mit_unterpfaden(fs, ziel, pfad, bool({"R", "--recursive"} & optionen)):
            alt_u, alt_g = fs.besitzer(p)
            neu_u = u or alt_u
            neu_g = g or (u if doppelpunkt and not g and u else alt_g)
            if not fs.z.get("root"):
                # Ohne root: nur die Gruppe der eigenen Datei ändern, und nur in eine eigene Gruppe.
                if alt_u != fs.benutzer or neu_u != alt_u or (neu_g != alt_g and neu_g not in fs.gruppen()):
                    zeilen.append(f"chown: changing ownership of '{anzeige}': Operation not permitted")
                    continue
            fs.setze_besitzer(p, f"{neu_u}:{neu_g}")
    return Ergebnis(zeilen, fehler=bool(zeilen))


# ---------------------------------------------------------------------- nano, crontab

def befehl_nano(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    _, argumente = _optionen(woerter)
    if not argumente:
        return Ergebnis(sim="Gib die Datei an, die du bearbeiten willst, z. B. nano /etc/hosts.")
    ziel = argumente[0]
    pfad = fs.absolut(ziel)
    if fs.ist_verzeichnis(pfad):
        return Ergebnis(sim=f"{ziel} ist ein Verzeichnis.")
    if not fs.erreichbar(pfad):
        return Ergebnis(sim=f"Kein Zugriff auf den Ordner von {ziel}. Mit sudo öffnen: sudo nano {ziel}")
    neu = not fs.ist_datei(pfad)
    if neu:
        ordner = posixpath.dirname(pfad)
        schreiben = fs.ist_verzeichnis(ordner) and fs.darf_schreiben(ordner)
        lesen = True
    else:
        lesen = fs.darf_lesen(pfad)
        schreiben = fs.darf_schreiben(pfad)
    if not lesen:
        return Ergebnis(sim=f"Keine Leserechte für {ziel}. Mit sudo öffnen: sudo nano {ziel}")
    return Ergebnis(editor={"pfad": pfad, "inhalt": "" if neu else fs.inhalt(pfad),
                            "nur_lesen": not schreiben, "neu": neu})


def befehl_crontab(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    """crontab -l (anzeigen) und crontab -e (bearbeiten) für den aktuellen Benutzer."""
    nutzer = fs.benutzer
    if "-u" in woerter and woerter.index("-u") + 1 < len(woerter):
        if not fs.z.get("root"):
            return Ergebnis(["crontab: must be privileged to use -u"], fehler=True)
        nutzer = woerter[woerter.index("-u") + 1]
    pfad = f"/var/spool/cron/crontabs/{nutzer}"
    if "-l" in woerter:
        if not fs.ist_datei(pfad):
            return Ergebnis([f"no crontab for {nutzer}"], fehler=True)
        return Ergebnis(_zeilen(fs.inhalt(pfad)))
    if "-e" in woerter:
        # crontab darf die eigene Datei immer bearbeiten (das Programm hat dafür besondere Rechte).
        return Ergebnis(editor={"pfad": pfad, "inhalt": fs.inhalt(pfad), "nur_lesen": False,
                                "neu": not fs.ist_datei(pfad)})
    return Ergebnis(sim="Hier gehen crontab -l (anzeigen) und crontab -e (bearbeiten).")


# ---------------------------------------------------------------------- Anlegen, kopieren, verschieben, löschen

def _jetzt_ls() -> str:
    import datetime as _dt
    j = _dt.datetime.now()
    monat = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")[j.month - 1]
    return f"{monat} {j.day:2d} {j.hour:02d}:{j.minute:02d}"


def _neu_angelegt(fs: Dateisystem, pfad: str, ordner: bool, modus: int | None = None) -> None:
    """Besitzer, Rechte und Zeit für etwas Neues (Ubuntu: umask 002 für Benutzer, 022 für root).

    modus: gewünschte Rechte vor der umask (Standard 777 für Ordner, 666 für Dateien).
    """
    if ordner:
        fs.z.werte[f"verzeichnis:{pfad}"] = True
    if modus is None:
        modus = 0o777 if ordner else 0o666
    fs.setze_rechte(pfad, modus_zu_rechte(modus & 0o777 & ~_umask(fs)))
    nutzer = fs.benutzer
    fs.setze_besitzer(pfad, f"{nutzer}:{nutzer}")
    fs.z.werte[f"zeit:{pfad}"] = _jetzt_ls()


def _unter(fs: Dateisystem, pfad: str) -> list[str]:
    """Alle Zustandsschlüssel des Pfads und darunter."""
    ergebnis = []
    for k in fs.z.werte:
        art, _, rest = k.partition(":")
        if art in ("datei", "verzeichnis", "rechte", "besitzer", "zeit") and (
                rest == pfad or rest.startswith(pfad.rstrip("/") + "/")):
            ergebnis.append(k)
    return ergebnis


def _entferne(fs: Dateisystem, pfad: str) -> None:
    eltern = posixpath.dirname(pfad)
    if eltern and fs.ist_verzeichnis(eltern):
        # Der Ordner darüber bleibt, auch wenn er nur durch diesen Eintrag bestand.
        fs.z.werte[f"verzeichnis:{eltern}"] = True
    for k in _unter(fs, pfad):
        art = k.split(":", 1)[0]
        if art == "datei":
            fs.z.werte[k] = None
        elif art == "verzeichnis":
            fs.z.werte[k] = False
        else:
            fs.z.werte.pop(k, None)


def _erster_vorhandener(fs: Dateisystem, pfad: str) -> tuple[str, list[str]]:
    """(erster vorhandener Ordner darüber, fehlende Ordner von unten nach oben)."""
    fehlend = [pfad]
    while not fs.existiert(posixpath.dirname(fehlend[-1])):
        fehlend.append(posixpath.dirname(fehlend[-1]))
    return posixpath.dirname(fehlend[-1]), fehlend


def befehl_mkdir(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    optionen, argumente = _optionen(woerter)
    if not argumente:
        return Ergebnis(["mkdir: missing operand", "Try 'mkdir --help' for more information."], fehler=True)
    zeilen: list[str] = []
    for ziel in argumente:
        pfad = fs.absolut(ziel)
        if not fs.erreichbar(pfad):
            zeilen.append(f"mkdir: cannot create directory '{ziel}': Permission denied")
            continue
        if fs.existiert(pfad):
            if "p" not in optionen or fs.ist_datei(pfad):
                zeilen.append(f"mkdir: cannot create directory '{ziel}': File exists")
            continue
        oben, fehlend = _erster_vorhandener(fs, pfad)
        if fs.ist_datei(oben):
            zeilen.append(f"mkdir: cannot create directory '{ziel}': Not a directory")
            continue
        if len(fehlend) > 1 and "p" not in optionen:
            zeilen.append(f"mkdir: cannot create directory '{ziel}': No such file or directory")
            continue
        if not fs.darf_schreiben(oben) or not fs.darf_betreten(oben):
            zeilen.append(f"mkdir: cannot create directory '{ziel}': Permission denied")
            continue
        for p in reversed(fehlend):
            _neu_angelegt(fs, p, ordner=True)
    return Ergebnis(zeilen, fehler=bool(zeilen))


def befehl_touch(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    _, argumente = _optionen(woerter)
    if not argumente:
        return Ergebnis(["touch: missing file operand", "Try 'touch --help' for more information."], fehler=True)
    zeilen: list[str] = []
    for ziel in argumente:
        pfad = fs.absolut(ziel)
        if not fs.erreichbar(pfad):
            zeilen.append(f"touch: cannot touch '{ziel}': Permission denied")
            continue
        if fs.existiert(pfad):
            if not fs.darf_schreiben(pfad) and fs.besitzer(pfad)[0] != fs.benutzer:
                zeilen.append(f"touch: cannot touch '{ziel}': Permission denied")
            else:
                fs.z.werte[f"zeit:{pfad}"] = _jetzt_ls()
            continue
        ordner = posixpath.dirname(pfad)
        if fs.ist_datei(ordner):
            zeilen.append(f"touch: cannot touch '{ziel}': Not a directory")
        elif not fs.ist_verzeichnis(ordner):
            zeilen.append(f"touch: cannot touch '{ziel}': No such file or directory")
        elif not fs.darf_schreiben(ordner):
            zeilen.append(f"touch: cannot touch '{ziel}': Permission denied")
        else:
            fs.schreibe(pfad, "")
            _neu_angelegt(fs, pfad, ordner=False)
    return Ergebnis(zeilen, fehler=bool(zeilen))


def _ziel_von(fs: Dateisystem, quelle: str, ziel: str) -> tuple[str, str]:
    """(absoluter Zielpfad, Ziel so, wie cp/mv es in Meldungen nennen)."""
    pfad = fs.absolut(ziel)
    if fs.ist_verzeichnis(pfad):
        name = posixpath.basename(quelle)
        return posixpath.join(pfad, name), posixpath.join(ziel, name)
    return pfad, ziel


def _kopiere(fs: Dateisystem, quelle: str, ziel: str, behalten: bool) -> None:
    """Kopiert Datei oder Ordner. Ohne -p: neue Einträge bekommen die Rechte der Quelle
    ohne die umask und den aktuellen Benutzer; eine vorhandene Zieldatei behält ihre Rechte."""
    basis = quelle.rstrip("/")
    for q in [quelle] + fs.alle_unter(quelle):
        z = ziel + q[len(basis):]
        ordner = fs.ist_verzeichnis(q)
        vorhanden = fs.existiert(z)
        if not ordner:
            fs.schreibe(z, fs.inhalt(q))
        if behalten:
            if ordner:
                fs.z.werte[f"verzeichnis:{z}"] = True
            fs.setze_rechte(z, fs.rechte(q))
            if fs.z.get("root"):
                fs.setze_besitzer(z, ":".join(fs.besitzer(q)))
            elif not vorhanden:
                fs.setze_besitzer(z, f"{fs.benutzer}:{fs.benutzer}")
            fs.z.werte[f"zeit:{z}"] = fs.z.get(f"zeit:{q}") or STANDARD_ZEIT
        elif vorhanden:
            fs.z.werte[f"zeit:{z}"] = _jetzt_ls()
        else:
            _neu_angelegt(fs, z, ordner=ordner, modus=rechte_zu_modus(fs.rechte(q)))


def befehl_cp(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    optionen, argumente = _optionen(woerter)
    if len(argumente) < 2:
        return Ergebnis([f"cp: missing destination file operand after '{argumente[0]}'" if argumente
                         else "cp: missing file operand", "Try 'cp --help' for more information."], fehler=True)
    *quellen, ziel = argumente
    if len(quellen) > 1 and not fs.ist_verzeichnis(fs.absolut(ziel)):
        return Ergebnis([f"cp: target '{ziel}' is not a directory"], fehler=True)
    rekursiv = bool({"r", "R", "a", "--recursive"} & optionen)
    behalten = bool({"p", "a", "--preserve"} & optionen)
    zeilen: list[str] = []
    for q_text in quellen:
        q = fs.absolut(q_text)
        if not fs.erreichbar(q):
            zeilen.append(f"cp: cannot stat '{q_text}': Permission denied")
            continue
        if not fs.existiert(q):
            zeilen.append(f"cp: cannot stat '{q_text}': No such file or directory")
            continue
        ist_ordner = fs.ist_verzeichnis(q)
        if ist_ordner and not rekursiv:
            zeilen.append(f"cp: -r not specified; omitting directory '{q_text}'")
            continue
        z, z_text = _ziel_von(fs, q, ziel)
        if ist_ordner and (z == q or z.startswith(q.rstrip("/") + "/")):
            zeilen.append(f"cp: cannot copy a directory, '{q_text}', into itself, '{z_text}'")
            continue
        if not ist_ordner and z == q:
            zeilen.append(f"cp: '{q_text}' and '{z_text}' are the same file")
            continue
        if not fs.darf_lesen(q):
            zeilen.append(f"cp: cannot open '{q_text}' for reading: Permission denied")
            continue
        ordner = posixpath.dirname(z)
        art = "directory" if ist_ordner else "regular file"
        if fs.ist_datei(ordner):
            zeilen.append(f"cp: cannot create {art} '{z_text}': Not a directory")
            continue
        if not fs.ist_verzeichnis(ordner):
            zeilen.append(f"cp: cannot create {art} '{z_text}': No such file or directory")
            continue
        if not ist_ordner and fs.ist_verzeichnis(z):
            zeilen.append(f"cp: cannot overwrite directory '{z_text}' with non-directory")
            continue
        if ist_ordner and fs.ist_datei(z):
            zeilen.append(f"cp: cannot overwrite non-directory '{z_text}' with directory '{q_text}'")
            continue
        if not fs.erreichbar(z):
            zeilen.append(f"cp: cannot create {art} '{z_text}': Permission denied")
            continue
        darf = fs.darf_schreiben(z) if fs.ist_datei(z) else (fs.existiert(z) or fs.darf_schreiben(ordner))
        if not darf:
            zeilen.append(f"cp: cannot create {art} '{z_text}': Permission denied")
            continue
        _kopiere(fs, q, z, behalten)
    return Ergebnis(zeilen, fehler=bool(zeilen))


def befehl_mv(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    _, argumente = _optionen(woerter)
    if len(argumente) < 2:
        return Ergebnis([f"mv: missing destination file operand after '{argumente[0]}'" if argumente
                         else "mv: missing file operand", "Try 'mv --help' for more information."], fehler=True)
    *quellen, ziel = argumente
    if len(quellen) > 1 and not fs.ist_verzeichnis(fs.absolut(ziel)):
        return Ergebnis([f"mv: target '{ziel}' is not a directory"], fehler=True)
    zeilen: list[str] = []
    for q_text in quellen:
        q = fs.absolut(q_text)
        if not fs.erreichbar(q):
            zeilen.append(f"mv: cannot stat '{q_text}': Permission denied")
            continue
        if not fs.existiert(q):
            zeilen.append(f"mv: cannot stat '{q_text}': No such file or directory")
            continue
        z, z_text = _ziel_von(fs, q, ziel)
        ist_ordner = fs.ist_verzeichnis(q)
        if z == q and not ist_ordner:
            zeilen.append(f"mv: '{q_text}' and '{z_text}' are the same file")
            continue
        if ist_ordner and (z == q or z.startswith(q.rstrip("/") + "/")):
            zeilen.append(f"mv: cannot move '{q_text}' to a subdirectory of itself, '{z_text}'")
            continue
        ordner = posixpath.dirname(z)
        if not fs.ist_verzeichnis(ordner) or fs.ist_datei(ordner):
            grund = "Not a directory" if fs.ist_datei(ordner) else "No such file or directory"
            zeilen.append(f"mv: cannot move '{q_text}' to '{z_text}': {grund}")
            continue
        if ist_ordner and fs.ist_datei(z):
            zeilen.append(f"mv: cannot overwrite non-directory '{z_text}' with directory '{q_text}'")
            continue
        if not ist_ordner and fs.ist_verzeichnis(z):
            zeilen.append(f"mv: cannot overwrite directory '{z_text}' with non-directory")
            continue
        if ist_ordner and fs.ist_verzeichnis(z) and fs.eintraege(z):
            zeilen.append(f"mv: cannot move '{q_text}' to '{z_text}': Directory not empty")
            continue
        quelle_ordner = posixpath.dirname(q)
        if (not fs.erreichbar(z) or not fs.darf_schreiben(quelle_ordner) or not fs.darf_schreiben(ordner)):
            zeilen.append(f"mv: cannot move '{q_text}' to '{z_text}': Permission denied")
            continue
        if fs.sticky_verbietet(q) or (fs.existiert(z) and fs.sticky_verbietet(z)):
            zeilen.append(f"mv: cannot move '{q_text}' to '{z_text}': Operation not permitted")
            continue
        alte = {k: fs.z.werte[k] for k in _unter(fs, q)}
        if fs.existiert(z):
            _entferne(fs, z)
        _entferne(fs, q)
        basis = q.rstrip("/")
        for k, v in alte.items():
            art, _, rest = k.partition(":")
            fs.z.werte[f"{art}:{z}{rest[len(basis):]}"] = v
    return Ergebnis(zeilen, fehler=bool(zeilen))


def befehl_rm(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    optionen, argumente = _optionen(woerter)
    if not argumente:
        return Ergebnis(["rm: missing operand", "Try 'rm --help' for more information."], fehler=True)
    rekursiv = bool({"r", "R", "--recursive"} & optionen)
    erzwingen = bool({"f", "--force"} & optionen)
    erg = Ergebnis()
    for ziel in argumente:
        pfad = fs.absolut(ziel)
        if pfad == "/":
            return Ergebnis(sim="Das würde das ganze System löschen. Das echte rm verweigert „rm -r /“ "
                                "ohnehin (Schutz --preserve-root) – hier passiert nichts.")
        if rekursiv and posixpath.basename(ziel.rstrip("/")) in (".", ".."):
            erg.err(f"rm: refusing to remove '.' or '..' directory: skipping '{ziel}'")
            continue
        if not fs.erreichbar(pfad):
            erg.err(f"rm: cannot remove '{ziel}': Permission denied")
            continue
        if not fs.existiert(pfad):
            if not erzwingen:
                erg.err(f"rm: cannot remove '{ziel}': No such file or directory")
            continue
        if fs.ist_verzeichnis(pfad) and not rekursiv:
            erg.err(f"rm: cannot remove '{ziel}': Is a directory")
            continue
        if not fs.darf_schreiben(posixpath.dirname(pfad)):
            erg.err(f"rm: cannot remove '{ziel}': Permission denied")
            continue
        if fs.sticky_verbietet(pfad):
            erg.err(f"rm: cannot remove '{ziel}': Operation not permitted")
            continue
        if fs.ist_datei(pfad) and not erzwingen and not fs.darf_schreiben(pfad):
            art = "regular empty file" if not fs.inhalt(pfad) else "regular file"
            erg.aus(f"rm: remove write-protected {art} '{ziel}'? y")
            erg.sim = ("rm fragt bei schreibgeschützten Dateien nach. Die Simulation antwortet mit y (ja). "
                       "Ohne Rückfrage: rm -f")
        if fs.cwd == pfad or fs.cwd.startswith(pfad + "/"):
            fs.z.werte["pfad"] = posixpath.dirname(pfad)
        _entferne(fs, pfad)
    return _fehler_nur(erg)


EINGEBAUT: dict[str, Callable[[Dateisystem, list[str]], Ergebnis]] = {
    "crontab": befehl_crontab,
    "pwd": befehl_pwd,
    "cd": befehl_cd,
    "ls": befehl_ls,
    "cat": befehl_cat,
    "less": befehl_less,
    "more": befehl_less,
    "head": befehl_head_tail("head"),
    "tail": befehl_head_tail("tail"),
    "grep": befehl_grep,
    "chmod": befehl_chmod,
    "chown": befehl_chown,
    "nano": befehl_nano,
    "mkdir": befehl_mkdir,
    "touch": befehl_touch,
    "cp": befehl_cp,
    "mv": befehl_mv,
    "rm": befehl_rm,
}

BEDEUTUNG = {
    "pwd": "Aktuelles Verzeichnis anzeigen",
    "cd": "Verzeichnis wechseln",
    "ls": "Dateien auflisten (-l ausführlich, -a auch versteckte, -h lesbare Größen)",
    "cat": "Inhalt einer Datei ausgeben",
    "less": "Datei seitenweise anzeigen",
    "head": "Die ersten Zeilen einer Datei (-n Anzahl)",
    "tail": "Die letzten Zeilen einer Datei (-n Anzahl, -f weiter mitlesen)",
    "grep": "Zeilen suchen, die ein Muster enthalten (-i ohne Groß/Klein, -n mit Zeilennummer)",
    "chmod": "Dateirechte ändern (z. B. 644, u+x)",
    "chown": "Besitzer einer Datei ändern (benutzer:gruppe, nur root)",
    "nano": "Datei im Editor bearbeiten (Strg+O speichern, Strg+X beenden)",
    "crontab": "Geplante Aufgaben anzeigen (-l) oder bearbeiten (-e)",
    "mkdir": "Verzeichnis anlegen (-p auch die Ordner davor)",
    "touch": "Leere Datei anlegen (oder Zeit aktualisieren)",
    "cp": "Kopieren (-r ganze Verzeichnisse)",
    "mv": "Verschieben oder umbenennen",
    "rm": "Löschen (-r Verzeichnisse) – ohne Papierkorb!",
}

FILTER = ("grep", "head", "tail", "wc", "less", "more", "sort")


def _sort(zeilen: list[str], woerter: list[str]) -> list[str] | None:
    optionen: set[str] = set()
    lang = {"--reverse": "r", "--numeric-sort": "n", "--unique": "u", "--ignore-case": "f"}
    for w in woerter:
        if w in lang:
            optionen.add(lang[w])
        elif re.fullmatch(r"-[rnuf]+", w):
            optionen.update(w[1:])
        else:
            return None

    def zahl(z: str) -> float:
        m = re.match(r"\s*(-?\d+(?:\.\d+)?)", z)
        return float(m.group(1)) if m else 0.0

    if "n" in optionen:
        schluessel = lambda z: (zahl(z), z)  # noqa: E731 – bei gleicher Zahl entscheidet die ganze Zeile
        gleich = zahl
    elif "f" in optionen:
        schluessel = lambda z: (z.upper(), z)  # noqa: E731
        gleich = str.upper
    else:
        schluessel = gleich = lambda z: z  # noqa: E731
    ergebnis = sorted(zeilen, key=schluessel, reverse="r" in optionen)
    if "u" in optionen:
        eindeutig: list[str] = []
        for z in ergebnis:
            if not eindeutig or gleich(eindeutig[-1]) != gleich(z):
                eindeutig.append(z)
        ergebnis = eindeutig
    return ergebnis


def _wc(zeilen: list[str], woerter: list[str]) -> list[str] | None:
    optionen: set[str] = set()
    lang = {"--lines": "l", "--words": "w", "--bytes": "c"}
    for w in woerter:
        if w in lang:
            optionen.add(lang[w])
        elif re.fullmatch(r"-[lwc]+", w):
            optionen.update(w[1:])
        else:
            return None
    if not optionen:
        optionen = {"l", "w", "c"}
    werte = []
    if "l" in optionen:
        werte.append(len(zeilen))
    if "w" in optionen:
        werte.append(sum(len(z.split()) for z in zeilen))
    if "c" in optionen:
        werte.append(sum(len(z.encode("utf-8")) + 1 for z in zeilen))
    if len(werte) == 1:
        return [str(werte[0])]
    return [" ".join(str(v).rjust(7) for v in werte)]  # wc liest von der Pipe: Breite 7


def filter_anwenden(name: str, woerter: list[str], zeilen: list[str]) -> tuple[list[str], str | None]:
    """Wendet einen Filter hinter einer Pipe auf Ausgabezeilen an. Fehlertext "nicht" = nicht nachgebaut."""
    if name == "grep":
        return filter_grep(zeilen, woerter)
    if name in ("head", "tail"):
        try:
            werte = _kopf_optionen(name, woerter)
        except _KopfFehler as e:
            return [], str(e)
        except KeyError:
            return [], "nicht"
        if werte["dateien"]:
            return [], "nicht"
        return _kopf_anwenden(name, werte, zeilen), None
    if name == "sort":
        ergebnis = _sort(zeilen, woerter)
        return (ergebnis, None) if ergebnis is not None else ([], "nicht")
    if name == "wc":
        ergebnis = _wc(zeilen, woerter)
        return (ergebnis, None) if ergebnis is not None else ([], "nicht")
    if name in ("less", "more"):
        return zeilen, None
    return zeilen, "nicht"
