# Szenario-Format

Jedes Szenario ist eine JSON-Datei: `daten/szenarien/<system>/<id>.json`.
Eigene Szenarien kannst du auch in deinen Datenordner legen, dann brauchst du keine neue
Programmversion: Windows `%APPDATA%\N3XTBYT3\szenarien\<system>\`, Linux
`~/.local/share/n3xtbyt3/szenarien/<system>/`. Das Programm lädt beide Ordner.

`<system>` ist eines von: `windows`, `windows_server`, `linux`, `linux_server`.

Felder, die mit `_` beginnen (z. B. `"_notiz"`), sind Kommentare und werden nicht geprüft.

## Pflichtfelder

| Feld | Inhalt |
|---|---|
| `id` | Kurzname, nur Kleinbuchstaben, Ziffern, Bindestriche. **Gleich dem Dateinamen** (ohne `.json`). Beispiel: `win-dns-cache` |
| `system` | `windows`, `windows_server`, `linux` oder `linux_server`. Muss zum Ordner passen. |
| `titel` | Kurzer Titel, wie ein Ticket-Betreff. |
| `kategorie` | Themengebiet, z. B. `Netzwerk`, `Dienste`, `Drucker`, `Speicher`, `Benutzer`. |
| `schwierigkeit` | `1` leicht, `2` mittel, `3` schwer. |
| `pruefstatus` | `ungeprueft` oder `bestaetigt`. Szenarien von Claude sind immer `ungeprueft`. Nur Tobi setzt `bestaetigt`. |
| `quelle` | Adresse (URL) der offiziellen Doku, oder eine Liste von Adressen. |
| `datum` | Datum der Erstellung, `JJJJ-MM-TT`. |
| `ausgangslage` | Was Tobi am Anfang sieht: Meldung, Anruf, Fehlertext. Text oder Liste von Zeilen. |
| `zustand` | Startwerte der Simulation, z. B. `{"dienst_spooler": "Stopped"}`. |
| `befehle` | Liste der Befehle, die das Szenario kennt (siehe unten). |
| `ziel` | Bedingung für „gelöst“, z. B. `{"dienst_spooler": "Running"}`. Eine Liste von Bedingungen heißt: eine davon reicht. |
| `hinweise` | Genau 3 Texte: 1 Richtung → 2 Werkzeug → 3 fast die Lösung. |
| `erklaerung` | Warum das die Lösung ist. Erscheint nach dem Lösen. Text oder Liste von Zeilen. |
| `begriffe` | Fachbegriffe mit kurzer Erklärung: `{"DNS": "übersetzt Namen in IP-Adressen"}`. |
| `loesung` | Liste der Befehle, die das Szenario lösen. Ein Test spielt sie automatisch durch. |

## Freiwillige Felder

| Feld | Inhalt |
|---|---|
| `shell` | Womit das Szenario startet. Windows: `powershell` (Standard) oder `cmd`. Linux: `bash`. |

## Zustand

Der Zustand ist eine flache Liste aus Schlüssel und Wert. Werte sind Text, Zahl,
`true`/`false` oder `null`. Schlüssel frei wählbar, am besten sprechend:
`dienst_spooler`, `frei_gb`, `dns_cache_alt`.

Allgemeine Startwerte stehen in `daten/allgemein/<system>.json` (z. B. `hostname`,
`benutzer`, `admin`, `pfad`). Ein Szenario kann sie im eigenen `zustand` überschreiben,
z. B. `"admin": false` für ein Fenster ohne Administratorrechte.

In Ausgaben wird `{schluessel}` durch den aktuellen Wert ersetzt, z. B. `{hostname}`.

## Befehle

```json
{
  "muster": ["Restart-Service -Name Spooler", "Restart-Service Spooler"],
  "bedeutung": "Einen Dienst neu starten",
  "shell": "powershell",
  "faelle": [
    {"wenn": {"admin": false}, "ausgabe": "…Fehlertext…", "fehler": true},
    {"setze": {"dienst_spooler": "Running"}}
  ]
}
```

| Feld | Inhalt |
|---|---|
| `muster` | Eine oder mehrere Schreibweisen des Befehls (siehe „Wie Eingaben verglichen werden“). |
| `faelle` | Liste möglicher Ergebnisse. Der **erste** Fall, dessen `wenn` passt, gilt. Ein Fall ohne `wenn` passt immer – also ans Ende. |
| `bedeutung` | Freiwillig. Was der Befehl tut, in einfachen Worten. Wird für das Befehls-Training genutzt. |
| `shell` | Freiwillig. In welcher Shell der Befehl geht: `powershell`, `cmd`, `bash` oder eine Liste. Ohne Angabe: Befehle der Form Verb-Nomen (`Get-Service`) nur in der PowerShell, alle anderen in jeder Shell des Systems. Aliase wie `gsv` bitte mit `"shell": "powershell"` kennzeichnen. |
| `falsch` | Freiwillig. `true`, wenn der Befehl zwar echt ist, aber hier die falsche Wahl (z. B. Neustart als Holzhammer). Dann **muss** `warum` dabei sein. Zählt als falscher Befehl. |
| `warum` | Erklärung, warum der Befehl hier falsch ist. Erscheint rechts im Hinweisbereich. |

### Felder eines Falls

| Feld | Inhalt |
|---|---|
| `wenn` | Bedingung (siehe unten). Ohne Angabe passt der Fall immer. |
| `ausgabe` | Was das System ausgibt. Text oder Liste von Zeilen. Leer lassen, wenn der echte Befehl nichts ausgibt (viele PowerShell-Befehle). |
| `fehler` | `true`, wenn die Ausgabe eine Fehlermeldung ist (wird rot angezeigt). |
| `sim` | `true`, wenn die Ausgabe eine Meldung der Simulation ist und kein echter Systemtext (blau, mit `[N3XTBYT3]`). Für Fälle, in denen die echte Ausgabe nicht sicher bekannt ist, ein Fenster aufgehen würde oder eine Rückfrage nicht nachgebaut ist. |
| `setze` | Änderungen am Zustand, z. B. `{"dienst_spooler": "Stopped"}`. Mit `{"+": 1}` oder `{"-": 1}` wird gerechnet. Die Änderung gilt schon für `{…}`-Platzhalter in der Ausgabe dieses Falls. |
| `aktion` | Nur für allgemeine Befehle: `leeren` (Bildschirm), `hilfe`, `exit`, `wechsel:<shell>`. |

### Bedingungen (`wenn` und `ziel`)

Alle genannten Schlüssel müssen passen.

* Gleichheit: `{"dienst_spooler": "Running", "admin": true}`
* Vergleich: `{"frei_gb": {">=": 10}}` – erlaubt sind `<`, `<=`, `>`, `>=` (nur Zahlen),
  `nicht` (`{"status": {"nicht": "Stopped"}}`) und `in` (`{"status": {"in": ["A", "B"]}}`).

Jeder Schlüssel in `wenn`, `setze` und `ziel` muss im Zustand vorkommen (Szenario oder
allgemein). Tippfehler meldet der Lader.

## Wie Eingaben verglichen werden

* **Windows:** Groß-/Kleinschreibung egal, `ipconfig.exe` = `ipconfig`.
* **Linux:** Groß-/Kleinschreibung zählt.
* Mehrere Leerzeichen sind egal. Anführungszeichen fassen Wörter zusammen und werden entfernt:
  `tasklist /FI "IMAGENAME eq EXCEL.EXE"`.
* **Optionen in beliebiger Reihenfolge:** Eine Option (beginnt mit `/` oder `-`, unter Linux
  nur `-`) gehört mit den Wörtern dahinter zusammen. `taskkill /IM EXCEL.EXE /F` passt
  auch zu `taskkill /F /IM EXCEL.EXE`, aber nicht zu `taskkill /IM /F EXCEL.EXE`.
* Wörter vor der ersten Option stehen fest in ihrer Reihenfolge.
* Ein `*` im Muster steht für genau ein beliebiges Wort (`ping *`).
* Pipes (`|`) trennen Abschnitte, die einzeln verglichen werden.
* Andere Schreibweisen (z. B. ohne `-Name`, mit Alias) als weiteres Muster angeben.

## Was die Simulation bei anderen Eingaben meldet

Alle Meldungen der Simulation beginnen mit `[N3XTBYT3]` und sind keine echten Systemtexte.

* Befehl im Szenario unbekannt: „In dieser Simulation nicht vorhanden“ plus Hinweis.
* Befehlsname bekannt, aber andere Parameter: „kennt diese Simulation, aber nicht in dieser Form“.
* Befehl gehört in die andere Shell (z. B. `Get-Service` in cmd): Hinweis zum Wechseln.

## Regeln für den Inhalt

* Jede Ausgabe muss zur offiziellen Doku passen (Microsoft Learn, man-Pages).
  Bei Unsicherheit lieber kürzen als erfinden.
* Nur erfundene Namen, Firmen und Adressen. IP-Adressen aus `192.168.x.x` oder `10.x.x.x`.
  Interne Namen enden auf `.internal` (für interne Netze reserviert), z. B. `intranet.firma.internal`.
* Ausgaben wie im englischen System (so stehen sie in der Microsoft-Doku). Ein deutsches
  Windows zeigt übersetzte Texte – das kann in `begriffe` oder `erklaerung` stehen.
