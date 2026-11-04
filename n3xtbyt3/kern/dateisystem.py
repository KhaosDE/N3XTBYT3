"""Simuliertes Dateisystem für Linux-Szenarien.

Dateien stehen im Szenario unter ``dateien`` und landen als flache Schlüssel im Zustand:

* ``datei:/pfad``        – Inhalt (Text); ``null`` = existiert (noch) nicht
* ``verzeichnis:/pfad``  – ``true`` für ausdrücklich angelegte (auch leere) Verzeichnisse
* ``rechte:/pfad``       – z. B. ``rw-r--r--``
* ``besitzer:/pfad``     – ``benutzer:gruppe``
* ``zeit:/pfad``         – Änderungszeit für ``ls -l``, z. B. ``Nov  4 09:12``

Verzeichnisse, in denen Dateien liegen, gibt es automatisch.
Allgemeine Befehle, die hier eingebaut sind: pwd, cd, ls, cat, less, head, tail, grep,
chmod, chown, nano (Editor) – Szenarien können jeden davon mit eigenen Mustern überschreiben.
Alle Ausgaben entstehen nur aus diesen Daten; es wird nie auf echte Dateien zugegriffen.
"""

from __future__ import annotations

import math
import posixpath
import re
from typing import Any, Callable

from .zustand import Zustand

STANDARD_ZEIT = "Nov  4 09:12"
STANDARD_DATEI_RECHTE = "rw-r--r--"
STANDARD_ORDNER_RECHTE = "rwxr-xr-x"
_OKTAL = re.compile(r"^[0-7]{3,4}$")
_RECHTE = re.compile(r"^[r-][w-][xsS-][r-][w-][xsS-][r-][w-][xtT-]$")


def oktal_zu_rechte(oktal: str) -> str:
    oktal = oktal[-3:]
    teile = []
    for ziffer in oktal:
        n = int(ziffer)
        teile.append(("r" if n & 4 else "-") + ("w" if n & 2 else "-") + ("x" if n & 1 else "-"))
    return "".join(teile)


def rechte_zu_oktal(rechte: str) -> str:
    werte = []
    for i in range(0, 9, 3):
        teil = rechte[i:i + 3]
        werte.append(str((4 if teil[0] == "r" else 0) + (2 if teil[1] == "w" else 0)
                         + (1 if teil[2] in "xst" else 0)))
    return "".join(werte)


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
    """Größe wie bei ls -h / df -h (aufgerundet, eine Nachkommastelle unter 10)."""
    if groesse < 1024:
        return str(groesse)
    for einheit in "KMGTP":
        groesse_neu = groesse / 1024
        if groesse_neu < 1024 or einheit == "P":
            if groesse_neu < 10:
                return f"{math.ceil(groesse_neu * 10) / 10:.1f}{einheit}"
            return f"{math.ceil(groesse_neu)}{einheit}"
        groesse = groesse_neu
    return str(groesse)


class Dateisystem:
    """Sicht auf die Datei-Schlüssel im Zustand einer Sitzung."""

    def __init__(self, zustand: Zustand):
        self.z = zustand

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
        return STANDARD_ORDNER_RECHTE if self.ist_verzeichnis(pfad) else STANDARD_DATEI_RECHTE

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

    # ------------------------------------------------------------------ Änderungen

    def schreibe(self, pfad: str, inhalt: str) -> None:
        self.z.werte[f"datei:{pfad}"] = inhalt

    def setze_rechte(self, pfad: str, rechte: str) -> None:
        self.z.werte[f"rechte:{pfad}"] = rechte

    def setze_besitzer(self, pfad: str, besitzer: str) -> None:
        self.z.werte[f"besitzer:{pfad}"] = besitzer


# ---------------------------------------------------------------------- Befehle

class Ergebnis:
    """Ergebnis eines eingebauten Dateibefehls."""

    def __init__(self, zeilen: list[str] | None = None, fehler: bool = False, sim: str | None = None,
                 editor: dict | None = None):
        self.zeilen = zeilen or []
        self.fehler = fehler
        self.sim = sim
        self.editor = editor


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


def befehl_pwd(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    return Ergebnis([fs.cwd])


def befehl_cd(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    ziel = woerter[0] if woerter else "~"
    if ziel == "-":
        ziel = str(fs.z.get("pfad_vorher") or fs.cwd)
    pfad = fs.absolut(ziel)
    if fs.ist_datei(pfad):
        return Ergebnis([f"bash: cd: {ziel}: Not a directory"], fehler=True)
    if not fs.ist_verzeichnis(pfad):
        return Ergebnis([f"bash: cd: {ziel}: No such file or directory"], fehler=True)
    if not fs.darf_betreten(pfad):
        return Ergebnis([f"bash: cd: {ziel}: Permission denied"], fehler=True)
    fs.z.werte["pfad_vorher"] = fs.cwd
    fs.z.werte["pfad"] = pfad
    return Ergebnis([pfad] if woerter and woerter[0] == "-" else [])


def _ls_zeile(fs: Dateisystem, pfad: str, name: str, breiten: dict, menschlich_an: bool) -> str:
    typ = "d" if fs.ist_verzeichnis(pfad) else "-"
    links = 2 + sum(1 for n in fs.eintraege(pfad) if fs.ist_verzeichnis(posixpath.join(pfad, n))) if typ == "d" else 1
    u, g = fs.besitzer(pfad)
    groesse = fs.groesse(pfad)
    g_text = menschlich(groesse) if menschlich_an else str(groesse)
    zeit = fs.z.get(f"zeit:{pfad}") or STANDARD_ZEIT
    return (f"{typ}{fs.rechte(pfad)} {str(links).rjust(breiten['l'])} {u.ljust(breiten['u'])} "
            f"{g.ljust(breiten['g'])} {g_text.rjust(breiten['s'])} {zeit} {name}")


def befehl_ls(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    optionen, argumente = _optionen(woerter)
    ziel = argumente[0] if argumente else "."
    pfad = fs.absolut(ziel)
    if not fs.existiert(pfad):
        return Ergebnis([f"ls: cannot access '{ziel}': No such file or directory"], fehler=True)
    lang = "l" in optionen
    alle = "a" in optionen
    mensch = "h" in optionen
    if fs.ist_datei(pfad):
        eintraege = [(pfad, ziel)]
        mit_summe = False
    else:
        if not fs.darf_lesen(pfad):
            return Ergebnis([f"ls: cannot open directory '{ziel}': Permission denied"], fehler=True)
        namen = fs.eintraege(pfad)
        if not alle:
            namen = [n for n in namen if not n.startswith(".")]
        eintraege = [(posixpath.join(pfad, n), n) for n in namen]
        if alle:
            eintraege = [(pfad, "."), (posixpath.dirname(pfad) or "/", "..")] + eintraege
        mit_summe = True
    if not lang:
        return Ergebnis(["  ".join(n for _, n in eintraege)] if eintraege else [])
    breiten = {"l": 1, "u": 1, "g": 1, "s": 1}
    for p, _ in eintraege:
        u, g = fs.besitzer(p)
        links = 2 + sum(1 for n in fs.eintraege(p) if fs.ist_verzeichnis(posixpath.join(p, n))) \
            if fs.ist_verzeichnis(p) else 1
        groesse = fs.groesse(p)
        breiten["l"] = max(breiten["l"], len(str(links)))
        breiten["u"] = max(breiten["u"], len(u))
        breiten["g"] = max(breiten["g"], len(g))
        breiten["s"] = max(breiten["s"], len(menschlich(groesse) if mensch else str(groesse)))
    zeilen = []
    if mit_summe:
        bloecke = sum(4 if fs.ist_verzeichnis(p) else math.ceil(fs.groesse(p) / 4096) * 4 for p, _ in eintraege)
        zeilen.append(f"total {menschlich(bloecke * 1024) if mensch else bloecke}")
    zeilen += [_ls_zeile(fs, p, n, breiten, mensch) for p, n in eintraege]
    return Ergebnis(zeilen)


def _lesbar(fs: Dateisystem, befehl: str, ziel: str) -> tuple[str | None, Ergebnis | None]:
    pfad = fs.absolut(ziel)
    if fs.ist_verzeichnis(pfad):
        return None, Ergebnis([f"{befehl}: {ziel}: Is a directory"], fehler=True)
    if not fs.ist_datei(pfad):
        return None, Ergebnis([f"{befehl}: {ziel}: No such file or directory"], fehler=True)
    if not fs.darf_lesen(pfad):
        return None, Ergebnis([f"{befehl}: {ziel}: Permission denied"], fehler=True)
    return pfad, None


def befehl_cat(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    optionen, argumente = _optionen(woerter)
    if not argumente:
        return Ergebnis(sim="cat ohne Datei liest von der Tastatur – das ist hier nicht nachgebaut.")
    zeilen: list[str] = []
    for ziel in argumente:
        pfad, fehler = _lesbar(fs, "cat", ziel)
        if fehler:
            return Ergebnis(zeilen + fehler.zeilen, fehler=True)
        inhalt = fs.inhalt(pfad)
        teile = inhalt.split("\n") if inhalt else []
        if "n" in optionen:
            teile = [f"{i:6}\t{z}" for i, z in enumerate(teile, start=1)]
        zeilen += teile
    return Ergebnis(zeilen)


def _anzahl(woerter: list[str]) -> tuple[int, list[str]]:
    n = 10
    rest: list[str] = []
    i = 0
    while i < len(woerter):
        w = woerter[i]
        if w == "-n" and i + 1 < len(woerter) and woerter[i + 1].lstrip("+-").isdigit():
            n = int(woerter[i + 1].lstrip("+-"))
            i += 2
            continue
        if re.match(r"^-n?\d+$", w):
            n = int(re.sub(r"\D", "", w))
        elif w != "-f":
            rest.append(w)
        i += 1
    return n, rest


def filter_head(zeilen: list[str], woerter: list[str]) -> list[str]:
    n, _ = _anzahl(woerter)
    return zeilen[:n]


def filter_tail(zeilen: list[str], woerter: list[str]) -> list[str]:
    n, _ = _anzahl(woerter)
    return zeilen[-n:] if n else []


def filter_grep(zeilen: list[str], woerter: list[str]) -> tuple[list[str], str | None]:
    """Gibt (Treffer, Fehlertext) zurück. Unterstützt -i, -v, -n, -c und einfache Muster."""
    optionen, argumente = _optionen(woerter)
    if not argumente:
        return [], "Usage: grep [OPTION]... PATTERNS [FILE]..."
    muster = argumente[0]
    flags = re.IGNORECASE if "i" in optionen else 0
    try:
        regex = re.compile(muster if any(c in muster for c in "^$[].*") else re.escape(muster), flags)
    except re.error:
        regex = re.compile(re.escape(muster), flags)
    treffer = []
    for nr, zeile in enumerate(zeilen, start=1):
        passt = bool(regex.search(zeile))
        if passt != ("v" in optionen):
            treffer.append(f"{nr}:{zeile}" if "n" in optionen else zeile)
    if "c" in optionen:
        return [str(len(treffer))], None
    return treffer, None


def befehl_head_tail(name: str) -> Callable[[Dateisystem, list[str]], Ergebnis]:
    def befehl(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
        _, rest = _anzahl(woerter)
        if not rest:
            return Ergebnis(sim=f"{name} ohne Datei liest von der Tastatur – das ist hier nicht nachgebaut.")
        pfad, fehler = _lesbar(fs, name, rest[0])
        if fehler:
            return fehler
        inhalt = fs.inhalt(pfad)
        zeilen = inhalt.split("\n") if inhalt else []
        zeilen = filter_head(zeilen, woerter) if name == "head" else filter_tail(zeilen, woerter)
        sim = None
        if name == "tail" and "-f" in woerter:
            sim = "tail -f wartet danach auf neue Zeilen (Strg+C zum Beenden) – hier werden nur die letzten Zeilen gezeigt."
        return Ergebnis(zeilen, sim=sim)
    return befehl


def befehl_less(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    ergebnis = befehl_cat(fs, [w for w in woerter if not w.startswith("-")])
    if not ergebnis.fehler and ergebnis.zeilen:
        ergebnis.sim = "less zeigt die Datei seitenweise (q beendet). Hier steht der ganze Inhalt im Terminal."
    return ergebnis


def befehl_grep(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    optionen, argumente = _optionen(woerter)
    if len(argumente) < 2:
        return Ergebnis(sim="grep braucht hier ein Suchmuster und eine Datei, z. B. grep error /var/log/syslog "
                            "(oder hinter einer Pipe: … | grep error).")
    zeilen_gesamt: list[str] = []
    dateien = argumente[1:]
    for ziel in dateien:
        pfad, fehler = _lesbar(fs, "grep", ziel)
        if fehler:
            zeilen_gesamt += fehler.zeilen
            continue
        inhalt = fs.inhalt(pfad)
        treffer, _ = filter_grep(inhalt.split("\n") if inhalt else [], [*[f"-{o}" for o in optionen], argumente[0]])
        if len(dateien) > 1 and "c" not in optionen:
            treffer = [f"{ziel}:{t}" for t in treffer]
        zeilen_gesamt += treffer
    return Ergebnis(zeilen_gesamt)


def befehl_chmod(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    optionen, argumente = _optionen([w for w in woerter if not re.match(r"^[ugoa]*[+-=][rwx]+$", w)])
    modus = next((w for w in woerter if re.match(r"^([0-7]{3,4}|[ugoa]*[+-=][rwx]+)$", w)), None)
    dateien = [a for a in argumente if a != modus]
    if not modus or not dateien:
        return Ergebnis(["chmod: missing operand"], fehler=True)
    zeilen: list[str] = []
    for ziel in dateien:
        pfad = fs.absolut(ziel)
        if not fs.existiert(pfad):
            zeilen.append(f"chmod: cannot access '{ziel}': No such file or directory")
            continue
        if not fs.z.get("root") and fs.besitzer(pfad)[0] != fs.benutzer:
            zeilen.append(f"chmod: changing permissions of '{ziel}': Operation not permitted")
            continue
        if _OKTAL.match(modus):
            neu = oktal_zu_rechte(modus)
        else:
            m = re.match(r"^([ugoa]*)([+-=])([rwx]+)$", modus)
            wer, op, was = m.group(1) or "a", m.group(2), m.group(3)
            if "a" in wer:
                wer = "ugo"
            neu = list(fs.rechte(pfad))
            for teil, start in (("u", 0), ("g", 3), ("o", 6)):
                if teil not in wer:
                    continue
                for recht, versatz in (("r", 0), ("w", 1), ("x", 2)):
                    if op == "=":
                        neu[start + versatz] = recht if recht in was else "-"
                    elif recht in was:
                        neu[start + versatz] = recht if op == "+" else "-"
            neu = "".join(neu)
        fs.setze_rechte(pfad, neu)
    return Ergebnis(zeilen, fehler=bool(zeilen))


def befehl_chown(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    _, argumente = _optionen(woerter)
    if len(argumente) < 2:
        return Ergebnis(["chown: missing operand"], fehler=True)
    neu, dateien = argumente[0], argumente[1:]
    zeilen: list[str] = []
    for ziel in dateien:
        pfad = fs.absolut(ziel)
        if not fs.existiert(pfad):
            zeilen.append(f"chown: cannot access '{ziel}': No such file or directory")
            continue
        if not fs.z.get("root"):
            zeilen.append(f"chown: changing ownership of '{ziel}': Operation not permitted")
            continue
        alt_u, alt_g = fs.besitzer(pfad)
        u, _, g = neu.partition(":")
        fs.setze_besitzer(pfad, f"{u or alt_u}:{g or (u if neu.endswith(':') else alt_g)}")
    return Ergebnis(zeilen, fehler=bool(zeilen))


def befehl_nano(fs: Dateisystem, woerter: list[str]) -> Ergebnis:
    _, argumente = _optionen(woerter)
    if not argumente:
        return Ergebnis(sim="Gib die Datei an, die du bearbeiten willst, z. B. nano /etc/hosts.")
    ziel = argumente[0]
    pfad = fs.absolut(ziel)
    if fs.ist_verzeichnis(pfad):
        return Ergebnis(sim=f"{ziel} ist ein Verzeichnis.")
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
        inhalt = fs.inhalt(pfad)
        return Ergebnis(inhalt.split("\n") if inhalt else [])
    if "-e" in woerter:
        # crontab darf die eigene Datei immer bearbeiten (das Programm hat dafür besondere Rechte).
        return Ergebnis(editor={"pfad": pfad, "inhalt": fs.inhalt(pfad), "nur_lesen": False,
                                "neu": not fs.ist_datei(pfad)})
    return Ergebnis(sim="Hier gehen crontab -l (anzeigen) und crontab -e (bearbeiten).")


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
}

FILTER = ("grep", "head", "tail", "wc", "less", "more", "sort")


def filter_anwenden(name: str, woerter: list[str], zeilen: list[str]) -> tuple[list[str], str | None]:
    """Wendet einen Filter hinter einer Pipe auf Ausgabezeilen an."""
    if name == "grep":
        return filter_grep(zeilen, woerter)
    if name == "head":
        return filter_head(zeilen, woerter), None
    if name == "tail":
        return filter_tail(zeilen, woerter), None
    if name == "sort":
        return sorted(zeilen, reverse="-r" in woerter), None
    if name == "wc" and "-l" in woerter:
        return [str(len(zeilen))], None
    if name in ("less", "more"):
        return zeilen, None
    return zeilen, "nicht"
