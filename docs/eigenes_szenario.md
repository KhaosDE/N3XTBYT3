# Einen echten Fehler als Szenario anlegen

Du hast im Alltag einen Fehler gelöst? Dann mach ein Szenario daraus. So übst du ihn
wieder, bis du ihn im Schlaf kannst. Das Programm braucht dafür **keine neue Version** –
eine Datei reicht.

## Weg A: Claude schreibt das Szenario (empfohlen)

1. Notiere kurz:
   - **Was war los?** (Meldung, Anruf, was auf dem Bildschirm stand – Fehlermeldungen wörtlich)
   - **Was hast du gemacht?** (alle Befehle der Reihe nach, mit den Ausgaben – am besten kopiert
     oder als Screenshot)
   - **Was war die Ursache?**
   - **Woher wusstest du es?** (Doku-Link, falls vorhanden)
2. Gib Claude im Chat diesen Text, die Datei `vorlagen/szenario_vorlage.json` und deine Notizen:

   > Mach aus meinem gelösten Fehler ein N3XTBYT3-Szenario. Halte dich an die Vorlage
   > und an `daten/szenarien/SCHEMA.md`. Übernimm meine Befehle und Ausgaben wörtlich,
   > erfinde keine Ausgaben. Ersetze echte Namen, Firmen und IP-Adressen durch erfundene
   > (IPs aus 192.168.x.x oder 10.x.x.x). Setze `"pruefstatus": "ungeprueft"`.
   > Gib mir die fertige JSON-Datei und sag mir den Dateinamen.

3. Lies das Ergebnis durch. Stimmt alles mit dem echten Fehler überein, ändere
   `"pruefstatus"` auf `"bestaetigt"`.
4. Speichere die Datei wie unten bei „Wohin mit der Datei?“ beschrieben.

## Weg B: Selbst ausfüllen

1. Kopiere `vorlagen/szenario_vorlage.json`.
2. Benenne die Kopie um, z. B. `win-drucker-offline.json`. Der Dateiname muss genau der `id` in
   der Datei entsprechen.
3. Fülle die Felder aus. Die Erklärungen stehen direkt in der Vorlage (Felder mit `_` vorne).
   Alle Regeln stehen in `daten/szenarien/SCHEMA.md`.
4. Die wichtigsten Punkte:
   - Für jeden Teil des Problems einen Schlüssel im `zustand` (z. B. `"dienst_spooler": "Stopped"`).
   - In `befehle` alles, was man zum **Nachschauen** und zum **Beheben** braucht – mit der echten Ausgabe.
   - `ziel` sagt, wann es gelöst ist.
   - Drei `hinweise`: Richtung → Werkzeug → fast die Lösung.
   - `loesung`: deine Befehle in der richtigen Reihenfolge.

## Wohin mit der Datei?

- **Nur für dich, sofort nutzbar:** in deinen Datenordner, Unterordner für das System:
  - Windows-PC: `%APPDATA%\N3XTBYT3\szenarien\windows\`
    (im Explorer in die Adresszeile `%APPDATA%\N3XTBYT3` eingeben; fehlende Ordner einfach anlegen)
  - Andere Systeme: `szenarien\windows_server\`, `szenarien\linux\`, `szenarien\linux_server\`
- **Dauerhaft im Projekt:** in `daten/szenarien/<system>/` im Repository. Dann prüfen die Tests
  bei jedem Push, dass das Szenario lädt und lösbar ist.

## Prüfen

Programm starten, System wählen. In der Szenarioliste steht dein Szenario mit der Markierung
„eigen“. Ist in der Datei ein Fehler, steht unten in Rot, welche Datei und was genau falsch ist
(z. B. „Es fehlen Pflichtfelder: hinweise“ oder „Kein gültiges JSON (Zeile 12, Spalte 5)“).

Häufige Fehler:

- Komma vergessen oder ein Komma zu viel (vor `]` oder `}` darf keins stehen).
- Backslash in Pfaden doppelt schreiben: `"C:\\Windows\\System32"`.
- Anführungszeichen in Texten mit `\"` schreiben – oder deutsche „…“ nehmen.
- Ein Schlüssel in `wenn`, `setze` oder `ziel`, der im `zustand` fehlt (Tippfehler).
