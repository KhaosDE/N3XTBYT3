"""Eingaben zerlegen und mit den Befehlsmustern der Szenarien vergleichen.

Ein Muster ist eine Befehlszeile, wie sie im echten System eingegeben würde, z. B.
``taskkill /IM EXCEL.EXE /F``. Eine Eingabe passt, wenn

* die Wörter genau übereinstimmen, oder
* der Befehlsname und die Wörter vor der ersten Option gleich sind und die Optionen
  (eine Option samt den Werten dahinter) in beliebiger Reihenfolge vorkommen.
  ``taskkill /F /IM EXCEL.EXE`` passt also auch.

Unter Windows zählt Groß-/Kleinschreibung nicht, unter Linux schon.
Ein ``*`` im Muster steht für genau ein beliebiges Wort.
Pipes (``|``) trennen Abschnitte, die einzeln und der Reihe nach verglichen werden.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .systeme import System

PLATZHALTER = "*"

# Standard-Aliase der Windows PowerShell 5.1 (nur in der PowerShell, nicht in der cmd). Belegt auf
# learn.microsoft.com: Abschnitt „Notes“ der Cmdlets (z. B. Get-Service: gsv) und „Using aliases“
# (Kompatibilitäts-Aliase). „help“ ist dort eine Funktion, die Get-Help aufruft (seitenweise).
# curl und wget fehlen bewusst: in 5.1 Aliase für Invoke-WebRequest, anders als curl.exe.
PS_ALIASE = {
    "gsv": "get-service", "sasv": "start-service", "spsv": "stop-service",
    "gps": "get-process", "ps": "get-process", "spps": "stop-process", "kill": "stop-process",
    "gcm": "get-command",
    "gci": "get-childitem", "dir": "get-childitem", "ls": "get-childitem",
    "sl": "set-location", "cd": "set-location", "chdir": "set-location",
    "gc": "get-content", "cat": "get-content", "type": "get-content",
    "gl": "get-location", "pwd": "get-location",
    "ni": "new-item",
    "cpi": "copy-item", "copy": "copy-item", "cp": "copy-item",
    "mi": "move-item", "move": "move-item", "mv": "move-item",
    "ri": "remove-item", "del": "remove-item", "rm": "remove-item", "erase": "remove-item",
    "rd": "remove-item", "rmdir": "remove-item",
    "cls": "clear-host", "clear": "clear-host",
    "help": "get-help",
}

# Bei diesen Cmdlets ist -Name der erste Positionsparameter (Syntax auf learn.microsoft.com, 5.1):
# „Get-Service Spooler“ ist dasselbe wie „Get-Service -Name Spooler“. Nicht bei Stop-Process (dort: -Id).
NAME_ZUERST = frozenset({"get-service", "start-service", "stop-service", "restart-service",
                         "get-process", "get-command", "get-help"})


def abstand(a: str, b: str) -> int:
    """Tippfehler-Abstand (Damerau-Levenshtein): einfügen, löschen, ersetzen, Nachbarn vertauschen = je 1."""
    if a == b:
        return 0
    vorvorher: list[int] = []
    vorher = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        jetzt = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            kosten = 0 if a[i - 1] == b[j - 1] else 1
            jetzt[j] = min(vorher[j] + 1, jetzt[j - 1] + 1, vorher[j - 1] + kosten)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                jetzt[j] = min(jetzt[j], vorvorher[j - 2] + 1)
        vorvorher, vorher = vorher, jetzt
    return vorher[len(b)]


def tippfehler_grenze(richtig: str) -> int:
    """Bis 5 Zeichen höchstens 1 Fehler, länger höchstens 2."""
    return 1 if len(richtig) <= 5 else 2


def aehnlich(getippt: str, richtig: str) -> bool:
    """Ist ``getippt`` ein Tippfehler von ``richtig``? (Beide schon normiert.)"""
    return getippt != richtig and len(richtig) >= 2 and abstand(getippt, richtig) <= tippfehler_grenze(richtig)


def vorschlag(wort: str, kandidaten, norm=lambda x: x) -> str | None:
    """Der nächste Kandidat mit Tippfehler-Abstand – oder None (auch wenn ``wort`` selbst vorkommt)."""
    w = norm(wort)
    bester, bester_abstand = None, 99
    for k in kandidaten:
        kn = norm(k)
        if kn == w:
            return None
        if len(kn) < 2:
            continue
        d = abstand(w, kn)
        if d <= tippfehler_grenze(kn) and (d, k) < (bester_abstand, bester or ""):
            bester, bester_abstand = k, d
    return bester


def _teile(getippt: str, richtig: str) -> tuple[str, str]:
    """Nur den falschen Teil zeigen: „*-Prcoess“/„*-Process“ → „Prcoess“/„Process“."""
    a, b = re.split(r"(\W+)", getippt), re.split(r"(\W+)", richtig)
    if len(a) == len(b) and all(x == y for x, y in zip(a[1::2], b[1::2])):
        anders = [(x, y) for x, y in zip(a[0::2], b[0::2]) if x.casefold() != y.casefold()]
        if len(anders) == 1 and anders[0][0] and anders[0][1]:
            return anders[0]
    return getippt, richtig


def tippfehler_text(paare: list[tuple[str, str]]) -> str:
    """„Fast! Schau dir „prcoess“ an – gemeint ist vermutlich „Process“.“"""
    teile = [_teile(e, m) for e, m in paare]
    falsch = " und ".join(f"„{e}“" for e, _ in teile)
    richtig = " und ".join(f"„{m}“" for _, m in teile)
    return f"Fast! Schau dir {falsch} an – gemeint ist vermutlich {richtig}."


_VERB_NOMEN = re.compile(r"[A-Za-z]+-[A-Za-z][A-Za-z0-9]*")


def zerlege(text: str) -> list[list[str]]:
    """Teilt eine Eingabe in Abschnitte (getrennt durch |) und Wörter.

    Anführungszeichen (" und ') fassen Wörter mit Leerzeichen zusammen und werden
    entfernt. Ein Backslash ist ein normales Zeichen (Windows-Pfade).
    """
    abschnitte: list[list[str]] = [[]]
    wort: list[str] = []
    hat_wort = False
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
            hat_wort = True
        elif zeichen.isspace():
            if hat_wort:
                abschnitte[-1].append("".join(wort))
                wort, hat_wort = [], False
        elif zeichen == "|":
            if hat_wort:
                abschnitte[-1].append("".join(wort))
                wort, hat_wort = [], False
            abschnitte.append([])
        else:
            wort.append(zeichen)
            hat_wort = True
    if hat_wort:
        abschnitte[-1].append("".join(wort))
    return abschnitte


def befehlsname(text: str) -> str:
    """Das erste Wort einer Eingabe (oder leerer Text)."""
    abschnitte = zerlege(text)
    if abschnitte and abschnitte[0]:
        return abschnitte[0][0]
    return ""


def ist_cmdlet_name(name: str) -> bool:
    """PowerShell-Befehle heißen Verb-Nomen, z. B. Get-Service."""
    return bool(_VERB_NOMEN.fullmatch(name))


@dataclass(frozen=True)
class _Abschnitt:
    woerter: tuple[str, ...]
    name: str
    positionen: tuple[str, ...]
    einheiten: tuple[tuple[str, ...], ...]


class Vergleicher:
    """Vergleicht Eingaben und Muster nach den Regeln eines Systems."""

    def __init__(self, system: System):
        self.system = system

    def norm(self, wort: str) -> str:
        return wort.casefold() if self.system.gross_klein_egal else wort

    def norm_name(self, name: str) -> str:
        name = self.norm(name)
        # Unter Windows ist "ipconfig.exe" dasselbe Programm wie "ipconfig".
        if self.system.gross_klein_egal and name.endswith(".exe") and len(name) > 4:
            name = name[:-4]
        return name

    def _ist_option(self, wort: str) -> bool:
        return len(wort) > 1 and wort[0] in self.system.options_zeichen

    def _ohne_name_parameter(self, woerter: list[str]) -> list[str]:
        """„Get-Service -Name Spooler“ → „Get-Service Spooler“ (wo -Name der erste Positionsparameter ist)."""
        if not self.system.gross_klein_egal or len(woerter) < 3:
            return woerter
        if PS_ALIASE.get(self.norm_name(woerter[0]), self.norm_name(woerter[0])) not in NAME_ZUERST:
            return woerter
        if not self._ist_option(woerter[1]):
            return woerter  # es gibt schon einen Wert an erster Position
        for i in range(1, len(woerter) - 1):
            if woerter[i].casefold() == "-name" and not self._ist_option(woerter[i + 1]):
                return [woerter[0], woerter[i + 1]] + woerter[1:i] + woerter[i + 2:]
        return woerter

    def _abschnitt(self, woerter: list[str]) -> _Abschnitt:
        woerter = self._ohne_name_parameter(list(woerter))
        normiert = [self.norm(w) for w in woerter]
        if normiert:
            normiert[0] = self.norm_name(woerter[0])
        name = normiert[0] if normiert else ""
        rest = normiert[1:]
        positionen: list[str] = []
        einheiten: list[list[str]] = []
        for wort in rest:
            if self._ist_option(wort):
                einheiten.append([wort])
            elif einheiten:
                einheiten[-1].append(wort)
            else:
                positionen.append(wort)
        return _Abschnitt(tuple(normiert), name, tuple(positionen), tuple(tuple(e) for e in einheiten))

    def vorbereiten(self, text: str) -> tuple[_Abschnitt, ...]:
        return tuple(self._abschnitt(a) for a in zerlege(text))

    @staticmethod
    def _folge_passt(muster: tuple[str, ...], eingabe: tuple[str, ...]) -> bool:
        if len(muster) != len(eingabe):
            return False
        return all(m == PLATZHALTER or m == e for m, e in zip(muster, eingabe))

    def _abschnitt_passt(self, muster: _Abschnitt, eingabe: _Abschnitt, aliase: bool = False) -> bool:
        if self._folge_passt(muster.woerter, eingabe.woerter):
            return True
        m_name, e_name = muster.name, eingabe.name
        if aliase:
            m_name, e_name = PS_ALIASE.get(m_name, m_name), PS_ALIASE.get(e_name, e_name)
        if m_name != e_name:
            return False
        if not self._folge_passt(muster.positionen, eingabe.positionen):
            return False
        if len(muster.einheiten) != len(eingabe.einheiten):
            return False
        return self._zuordnen(muster.einheiten, eingabe.einheiten)

    def _zuordnen(self, einheiten: tuple, frei: tuple) -> bool:
        """Jede Option des Musters bekommt eine eigene Option der Eingabe.

        Mit Rückschritt: Ein Platzhalter (*) darf nicht die Option „wegnehmen“, die ein
        genaueres Muster braucht (z. B. -a * und -a x gegen -a x -a y).
        """
        if not einheiten:
            return True
        erste, rest = einheiten[0], einheiten[1:]
        for i, kandidat in enumerate(frei):
            if self._folge_passt(erste, kandidat) and self._zuordnen(rest, frei[:i] + frei[i + 1:]):
                return True
        return False

    def passt(self, muster: tuple[_Abschnitt, ...], eingabe: tuple[_Abschnitt, ...], aliase: bool = False) -> bool:
        """aliase=True: PowerShell-Aliase (gsv, dir, …) gelten wie der volle Cmdlet-Name."""
        if len(muster) != len(eingabe):
            return False
        return all(self._abschnitt_passt(m, e, aliase) for m, e in zip(muster, eingabe))

    def name_mit_alias(self, name: str, aliase: bool) -> str:
        name = self.norm_name(name)
        return PS_ALIASE.get(name, name) if aliase else name

    # ------------------------------------------------------------------ Tippfehler

    def tippfehler(self, eingabe: str, muster, aliase: bool = False) -> list[tuple[str, str]] | None:
        """Weicht die Eingabe nur in ein, zwei Wörtern um einen Tippfehler von einem Muster ab?

        Gibt die Paare (getippt, gemeint) zurück – vom Muster mit den wenigsten Abweichungen –
        oder None. Ein ``*`` im Muster passt auf jedes Wort.
        """
        e_ab = zerlege(eingabe)
        bestes: list[tuple[str, str]] | None = None
        for m in muster:
            m_ab = zerlege(m)
            if len(m_ab) != len(e_ab):
                continue
            paare: list[tuple[str, str]] = []
            for ms, es in zip(m_ab, e_ab):
                p = self._abweichung(ms, es, aliase)
                if p is None:
                    break
                paare += p
            else:
                if paare and len(paare) <= 2 and (bestes is None or len(paare) < len(bestes)):
                    bestes = paare
        return bestes

    def _wort_paar(self, m: str, e: str, erstes: bool, aliase: bool) -> tuple[str, str] | None | bool:
        """True = gleich, (e, m) = Tippfehler, None = passt nicht."""
        mn = self.name_mit_alias(m, aliase) if erstes else self.norm(m)
        en = self.name_mit_alias(e, aliase) if erstes else self.norm(e)
        if mn == en or (not erstes and m == PLATZHALTER):
            return True
        if aehnlich(en, mn):
            return (e, m)
        return None

    def _paare(self, m: list[str], e: list[str], start: int, aliase: bool) -> list | None:
        if len(m) != len(e):
            return None
        ergebnis = []
        for i, (mw, ew) in enumerate(zip(m, e)):
            p = self._wort_paar(mw, ew, start + i == 0, aliase)
            if p is None:
                return None
            if p is not True:
                ergebnis.append(p)
        return ergebnis

    def _gliedern(self, woerter: list[str]) -> tuple[list[str], list[list[str]]]:
        positionen: list[str] = []
        einheiten: list[list[str]] = []
        for w in woerter:
            if self._ist_option(w):
                einheiten.append([w])
            elif einheiten:
                einheiten[-1].append(w)
            else:
                positionen.append(w)
        return positionen, einheiten

    def _abweichung(self, m: list[str], e: list[str], aliase: bool) -> list | None:
        # Mit und ohne „-Name“ versuchen (ein Tippfehler in „-Nmae“ verhindert sonst den Vergleich)
        bestes = None
        for mm, ee in ((self._ohne_name_parameter(list(m)), self._ohne_name_parameter(list(e))), (list(m), list(e))):
            p = self._abweichung_genau(mm, ee, aliase)
            if p is not None and (bestes is None or len(p) < len(bestes)):
                bestes = p
        return bestes

    def _abweichung_genau(self, m: list[str], e: list[str], aliase: bool) -> list | None:
        if not m or len(m) != len(e):
            return None
        der_reihe_nach = self._paare(m, e, 0, aliase)
        if der_reihe_nach is not None:
            return der_reihe_nach
        # Optionen dürfen in anderer Reihenfolge stehen (wie beim normalen Vergleich)
        mp, me = self._gliedern(m[1:])
        ep, ee = self._gliedern(e[1:])
        kopf = self._paare([m[0]] + mp, [e[0]] + ep, 0, aliase)
        if kopf is None or len(me) != len(ee):
            return None

        def zuordnen(rest_m, frei):
            if not rest_m:
                return []
            bestes = None
            for i, kandidat in enumerate(frei):
                p = self._paare(rest_m[0], kandidat, 1, aliase)
                if p is None:
                    continue
                weiter = zuordnen(rest_m[1:], frei[:i] + frei[i + 1:])
                if weiter is not None and (bestes is None or len(p) + len(weiter) < len(bestes)):
                    bestes = p + weiter
            return bestes

        einheiten = zuordnen(me, ee)
        return None if einheiten is None else kopf + einheiten
