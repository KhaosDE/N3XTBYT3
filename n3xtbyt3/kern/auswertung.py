"""Auswertung je System: Stärken, Schwächen, häufige Fehler, Empfehlung.

Schreibt ``auswertung_<system>.json`` (für Programme, z. B. Claude) und
``auswertung_<system>.md`` (zum Lesen) in den Datenordner.
"""

from __future__ import annotations

import datetime as _dt
from collections import Counter, defaultdict
from typing import Any, Sequence

from .befehle import Vergleicher, zerlege
from .dateien import schreibe_json, schreibe_text
from .lernkartei import Lernkartei
from .spielstand import Spielstand
from .systeme import SYSTEME
from .szenario import Szenario
from .training import sammle_karten


def _letzter(eintrag: dict) -> dict:
    return eintrag["verlauf"][-1] if eintrag.get("verlauf") else {}


def _kategorie_bewertung(werte: list[dict]) -> str:
    gespielt = [w for w in werte if w["versuche"]]
    if not gespielt:
        return "noch nicht geübt"
    if any(not w["letzter_geloest"] for w in gespielt):
        return "schwach"
    schnitt_hinweise = sum(w["letzte_hinweise"] for w in gespielt) / len(gespielt)
    if schnitt_hinweise >= 2:
        return "schwach"
    if schnitt_hinweise <= 0.5 and all(w["fach"] >= 2 for w in gespielt):
        return "stark"
    return "mittel"


def erstelle(system_id: str, szenarien: Sequence[Szenario], stand: Spielstand,
             jetzt: _dt.datetime | None = None, lektionen=None, buch=None) -> dict[str, Any]:
    jetzt = (jetzt or _dt.datetime.now()).replace(microsecond=0)
    from . import befehlsbuch, grundkurs
    if lektionen is None:
        lektionen = grundkurs.lade_kurs(system_id).lektionen
    if buch is None:
        buch = befehlsbuch.lade(system_id)
    system = SYSTEME[system_id]
    vergleicher = Vergleicher(system)
    kartei: Lernkartei = stand.kartei

    szenario_werte = []
    for sz in sorted(szenarien, key=lambda s: (s.kategorie, s.titel)):
        e = stand.eintrag(sz.id)
        letzter = _letzter(e)
        karte = kartei.szenario(sz.id)
        szenario_werte.append({
            "id": sz.id,
            "titel": sz.titel,
            "kategorie": sz.kategorie,
            "schwierigkeit": sz.schwierigkeit,
            "pruefstatus": sz.pruefstatus,
            "versuche": e["versuche"],
            "geloest": e["geloest"],
            "letzter_geloest": bool(letzter.get("geloest", False)),
            "letzte_hinweise": int(letzter.get("hinweise", 0)),
            "falsche_befehle": e["falsche_befehle"],
            "unbekannte_befehle": e["unbekannte_befehle"],
            "zeit_minuten": round(e["zeit_sekunden"] / 60, 1),
            "fach": karte["fach"] if stand.gesehen(sz.id) else None,
            "faellig": karte["faellig"],
        })

    kategorien = defaultdict(list)
    for w in szenario_werte:
        kategorien[w["kategorie"]].append({**w, "fach": w["fach"] or 0})
    kategorie_werte = []
    for name, werte in sorted(kategorien.items()):
        gespielt = [w for w in werte if w["versuche"]]
        kategorie_werte.append({
            "kategorie": name,
            "szenarien": len(werte),
            "gespielt": len(gespielt),
            "geloest": sum(1 for w in werte if w["geloest"]),
            "hinweise_schnitt": round(sum(w["letzte_hinweise"] for w in gespielt) / len(gespielt), 1) if gespielt else None,
            "bewertung": _kategorie_bewertung(werte),
        })

    # Häufige Fehler: falsche und unbekannte Eingaben aus allen Versuchen
    falsch_namen: Counter[str] = Counter()
    unbekannt_namen: Counter[str] = Counter()
    beispiele: dict[str, dict[str, str]] = {"falsch": {}, "unbekannt": {}}
    for sz in szenarien:
        for versuch in stand.eintrag(sz.id)["verlauf"]:
            for liste, zaehler in ((versuch.get("falsch", []), falsch_namen),
                                   (versuch.get("unbekannt", []), unbekannt_namen)):
                for eingabe in liste:
                    abschnitte = zerlege(eingabe)
                    if not abschnitte or not abschnitte[0]:
                        continue
                    name = vergleicher.norm_name(abschnitte[0][0])
                    zaehler[name] += 1
                    beispiele["falsch" if zaehler is falsch_namen else "unbekannt"].setdefault(name, eingabe)

    befehl_werte = []
    for karte in sammle_karten(szenarien, buch, stand, lektionen):
        k = kartei.befehl(karte.schluessel)
        if not (k["richtig"] or k["falsch"] or k["zuletzt"]):
            continue
        befehl_werte.append({
            "befehl": karte.beispiel,
            "bedeutung": karte.bedeutung,
            "fach": k["fach"],
            "richtig": k["richtig"],
            "falsch": k["falsch"],
        })
    befehl_werte.sort(key=lambda b: (b["fach"], -b["falsch"], b["befehl"]))

    gespielt = [w for w in szenario_werte if w["versuche"]]
    staerken = [f"Kategorie {k['kategorie']}: sicher gelöst" for k in kategorie_werte if k["bewertung"] == "stark"]
    staerken += [f"Befehl „{b['befehl']}“ sitzt (Fach {b['fach']})"
                 for b in sorted(befehl_werte, key=lambda b: (-b["fach"], b["befehl"])) if b["fach"] >= 4][:5]
    schwaechen = [f"Kategorie {k['kategorie']}: noch unsicher" for k in kategorie_werte if k["bewertung"] == "schwach"]
    schwaechen += [f"Szenario „{w['titel']}“: zuletzt nicht gelöst" for w in gespielt if not w["letzter_geloest"]]
    schwaechen += [f"Szenario „{w['titel']}“: brauchte {w['letzte_hinweise']} Hinweise"
                   for w in gespielt if w["letzter_geloest"] and w["letzte_hinweise"] >= 2]
    schwaechen += [f"Befehl „{b['befehl']}“ ({b['bedeutung']}): {b['falsch']}× falsch im Training"
                   for b in befehl_werte if b["falsch"] and b["fach"] <= 2][:5]

    kurs_fertig = [l for l in lektionen if stand.lektion(l.id)["fertig"]]
    kurs_offen = next((l for l in lektionen if not stand.lektion(l.id)["fertig"]), None)
    grundkurs_werte = {
        "lektionen": len(lektionen),
        "fertig": len(kurs_fertig),
        "naechste": f"Lektion {kurs_offen.nr}: {kurs_offen.titel}" if kurs_offen else None,
        "liste": [{"nr": l.nr, "id": l.id, "titel": l.titel, "fertig": stand.lektion(l.id)["fertig"]}
                  for l in lektionen],
    }

    empfehlung: list[str] = []
    if kurs_offen:
        empfehlung.append(f"Grundkurs weitermachen: Lektion {kurs_offen.nr} – {kurs_offen.titel}")
    dran = sorted(
        (w for w in szenario_werte if w["versuche"] and kartei.ist_faellig(kartei.szenario(w["id"]), jetzt.date())),
        key=lambda w: (w["fach"] or 0, w["titel"]))
    for w in dran[:3]:
        empfehlung.append(f"Wiederholen: „{w['titel']}“ (Fach {w['fach']}, fällig)")
    neu = [w for w in szenario_werte if not w["versuche"]]
    if neu:
        empfehlung.append(f"Neu ausprobieren: {len(neu)} Szenario(s), z. B. „{neu[0]['titel']}“")
    for k in kategorie_werte:
        if k["bewertung"] == "schwach":
            empfehlung.append(f"Kategorie {k['kategorie']} gezielt üben (Szenarioliste, nach Kategorie sortiert)")
    schwache_befehle = [b for b in befehl_werte if b["fach"] <= 2 and b["falsch"]]
    if schwache_befehle:
        empfehlung.append("Befehls-Training: " + ", ".join(f"„{b['befehl']}“" for b in schwache_befehle[:3]))
    if not empfehlung:
        empfehlung.append("Alles wiederholt, was fällig ist. Befehls-Training oder ein neues System ausprobieren.")

    return {
        "erstellt": jetzt.isoformat(),
        "system": system_id,
        "system_name": system.name,
        "gesamt": {
            "szenarien": len(szenario_werte),
            "gespielt": len(gespielt),
            "geloest": sum(1 for w in szenario_werte if w["geloest"]),
            "versuche": sum(w["versuche"] for w in szenario_werte),
            "zeit_minuten": round(sum(w["zeit_minuten"] for w in szenario_werte), 1),
            "faecher": dict(Counter(str(w["fach"]) for w in szenario_werte if w["fach"])),
        },
        "grundkurs": grundkurs_werte,
        "staerken": staerken,
        "schwaechen": schwaechen,
        "empfehlung": empfehlung,
        "kategorien": kategorie_werte,
        "befehle": befehl_werte,
        "haeufige_fehler": {
            "falsch": [{"befehl": n, "anzahl": c, "beispiel": beispiele["falsch"][n]}
                       for n, c in falsch_namen.most_common(10)],
            "unbekannt": [{"befehl": n, "anzahl": c, "beispiel": beispiele["unbekannt"][n]}
                          for n, c in unbekannt_namen.most_common(10)],
        },
        "szenarien": szenario_werte,
    }


def _zelle(wert: Any) -> str:
    """Text für eine Markdown-Tabellenzelle: | und Zeilenumbrüche würden die Spalten verschieben."""
    return str(wert).replace("|", "\\|").replace("\n", " ")


def _grundkurs_md(g: dict[str, Any] | None) -> list[str]:
    if not g or not g["lektionen"]:
        return []
    z = ["## Grundkurs", "", f"{g['fertig']} von {g['lektionen']} Lektionen geschafft"
         + (f" · als Nächstes: {g['naechste']}" if g["naechste"] else " · alles geschafft") + ".", ""]
    z += [f"- [{'x' if l['fertig'] else ' '}] Lektion {l['nr']}: {l['titel']}" for l in g["liste"]]
    return z + [""]


def als_markdown(a: dict[str, Any]) -> str:
    g = a["gesamt"]
    z = [
        f"# Auswertung {a['system_name']}",
        "",
        f"Erstellt: {a['erstellt'].replace('T', ' ')} · {g['gespielt']} von {g['szenarien']} Szenarien gespielt, "
        f"{g['geloest']} gelöst, {g['versuche']} Versuche, {g['zeit_minuten']} Minuten.",
        "",
        "## Empfehlung",
        "",
        *[f"- {e}" for e in a["empfehlung"]],
        "",
        *_grundkurs_md(a.get("grundkurs")),
        "## Stärken",
        "",
        *([f"- {s}" for s in a["staerken"]] or ["- (noch keine)"]),
        "",
        "## Schwächen",
        "",
        *([f"- {s}" for s in a["schwaechen"]] or ["- (keine erkennbar)"]),
        "",
        "## Kategorien",
        "",
        "| Kategorie | Szenarien | gespielt | gelöst | Hinweise (Schnitt) | Bewertung |",
        "|---|---|---|---|---|---|",
    ]
    for k in a["kategorien"]:
        h = "–" if k["hinweise_schnitt"] is None else str(k["hinweise_schnitt"])
        z.append(f"| {_zelle(k['kategorie'])} | {k['szenarien']} | {k['gespielt']} | {k['geloest']} | {h} | {k['bewertung']} |")
    z += ["", "## Häufige Fehler", ""]
    fehler = a["haeufige_fehler"]
    if not fehler["falsch"] and not fehler["unbekannt"]:
        z.append("- (keine)")
    for f in fehler["falsch"]:
        z.append(f"- falsch eingesetzt: `{f['beispiel']}` ({f['anzahl']}×)")
    for f in fehler["unbekannt"]:
        z.append(f"- der Simulation unbekannt: `{f['beispiel']}` ({f['anzahl']}×)")
    if a["befehle"]:
        z += ["", "## Befehls-Training", "", "| Befehl | Bedeutung | Fach | richtig | falsch |", "|---|---|---|---|---|"]
        for b in a["befehle"]:
            z.append(f"| `{_zelle(b['befehl'])}` | {_zelle(b['bedeutung'])} | {b['fach']} | {b['richtig']} | {b['falsch']} |")
    z += ["", "## Szenarien", "", "| Szenario | Kategorie | Versuche | gelöst | Fach | fällig |", "|---|---|---|---|---|---|"]
    for w in a["szenarien"]:
        fach = "–" if w["fach"] is None else str(w["fach"])
        faellig = w["faellig"] or "–"
        z.append(f"| {_zelle(w['titel'])} | {_zelle(w['kategorie'])} | {w['versuche']} | {'ja' if w['geloest'] else 'nein'} | {fach} | {faellig} |")
    z += ["", "Fächer: 1 = gleich wieder, 2 = nach 1 Tag, 3 = nach 3 Tagen, 4 = nach 7 Tagen, 5 = nach 14 Tagen.", ""]
    return "\n".join(z)


def schreibe(system_id: str, szenarien: Sequence[Szenario], stand: Spielstand) -> dict[str, Any]:
    daten = erstelle(system_id, szenarien, stand)
    schreibe_json(f"auswertung_{system_id}.json", daten)
    schreibe_text(f"auswertung_{system_id}.md", als_markdown(daten))
    return daten
