# N3XTBYT3

Lern-Simulator für Systemwartung. Über ein **nachgebautes Terminal** erkennst und behebst du
Fehler an Windows, Windows Server, Linux und Linux Server. Reine Simulation: Das Programm
führt nie echte Befehle aus und ändert nichts an deinem PC.

Fortschritt: `STAND.md` · Plan: `PLAN.md` · Regeln: `CLAUDE.md`

## Starten

### Windows-Programm (.exe)

1. Auf GitHub im Repository oben auf **Actions** klicken.
2. Den neuesten grünen Lauf „Tests und Windows-Programm“ öffnen. Bist du in einem Job gelandet
   (Liste mit Schritten), links ganz oben auf **Summary** klicken.
3. Auf der Summary-Seite ganz nach unten scrollen zum Abschnitt **Artifacts** und auf
   **N3XTBYT3-Windows** klicken. Es kommt eine ZIP-Datei (rund 16 MB). Artefakte bleiben 30 Tage.
   (Das zweite Artefakt **N3XTBYT3-MCP-Windows** brauchst du nur für Claude Desktop.)
4. ZIP entpacken, `N3XTBYT3.exe` doppelklicken.
5. Windows warnt beim ersten Start („Der Computer wurde durch Windows geschützt“), weil die
   Datei nicht signiert ist: **Weitere Informationen** → **Trotzdem ausführen**.

### Mit Python (zum Entwickeln)

Python 3.12, dann im Projektordner:

```bash
pip install -r requirements.txt
```

```bash
python -m n3xtbyt3
```

## Neu an der Konsole? Der Grundkurs

Beim ersten Start begrüßt dich N3XTBYT3 und bietet den **Grundkurs** an (Enter). Er fängt ganz vorn an –
was ist ein Prompt, wie tippe ich einen Befehl – und führt Schritt für Schritt durch die wichtigsten
Befehle: erst erklären, dann mittippen (rechts steht genau, was du tippen sollst, und danach, was die
Ausgabe bedeutet), dann selbst probieren (mit Hinweisen über F1).

- Windows (10 Lektionen, PowerShell zuerst), Windows Server (8), Linux (10), Linux Server (7).
- Später erreichst du ihn in jeder Szenarioliste über den ersten Eintrag „Grundkurs“.
- Szenarien zeigen „braucht: Lektion 6“, wenn die passende Lektion noch fehlt – nur ein Hinweis, gesperrt
  wird nichts.
- **F4 Befehlsbuch** (überall): jeder Befehl mit Beispiel, Parametern und „Wann brauche ich das?“;
  mit Tab die Sicht **„Was tippe ich, wenn …?“**. Einfach lostippen zum Suchen.
- **F5 Lexikon** (überall): alle Fachbegriffe mit Erklärung und wo sie vorkommen.

## Spielen

1. Im Hauptmenü ein System wählen (Pfeiltasten oder 1–4, dann Enter) – oder 5 für die Tickets.
   Bereiche ohne Szenarien stehen grau als „kommt noch“ da.
2. In der Liste **Zufälliges Szenario** nehmen (ungelöste und schwache kommen öfter) oder ein
   bestimmtes wählen.
3. Rechts steht die Ausgangslage. Links tippst du Befehle wie im echten System.
4. Nicht weiter? **F1** zeigt einen Hinweis – Stufe für Stufe: Richtung → Werkzeug → fast die Lösung.
5. Gelöst? Rechts erscheint die Erklärung. **F2** holt das nächste Szenario.

| Taste | Wirkung |
|---|---|
| F1 | nächster Hinweis |
| F2 | nächstes Szenario |
| F3 | Ticket schließen (nur bei Tickets, wenn das Problem behoben ist) |
| F4 | Befehlsbuch (Tab: „Was tippe ich, wenn …?“) |
| F5 | Lexikon |
| Esc | zurück zur Liste / zum Menü |
| Pfeil hoch/runter | frühere Befehle |
| Bild hoch/runter, Mausrad | blättern |
| Strg + / Strg − / Strg 0 | Schrift größer / kleiner / normal |
| F11 | Vollbild |
| Strg+V | Text einfügen |

Außerdem in der Liste:

- **Befehls-Training:** kurze Fragen „Welcher Befehl …?“ aus den Befehlen der Szenarien.
  Richtig → die Karte wandert ein Fach weiter; falsch → zurück in Fach 1, sie kommt bald wieder.
- **Auswertung:** Stärken, Schwächen nach Kategorie und Befehl, häufige Fehler und was du als
  Nächstes üben solltest. Sie liegt auch als Datei im Datenordner (`auswertung_<system>.md`),
  damit Claude sie lesen kann.

**Tickets:** Die fünfte Kachel im Hauptmenü mischt Störungsmeldungen aus allen Systemen – mit
Ticketnummer, Absender und Dringlichkeit. Manche gehen über mehrere Rechner: vom PC aus per
`ssh admin@srv-web01` (Linux) oder `Enter-PSSession -ComputerName srv-datei01` (Windows) auf den
Server, dort beheben, mit `exit` zurück, vom PC aus nachprüfen. Ist das Problem behoben, schließt
**F3** das Ticket mit einer kurzen Lösungsnotiz.

**Lernkartei:** Jedes Szenario und jeder Befehl liegt in einem Fach (1–5). Fach 1 kommt sofort
wieder, Fach 2 nach einem Tag, Fach 3 nach drei, Fach 4 nach sieben, Fach 5 nach 14 Tagen.
Ohne Hinweis gelöst → ein Fach weiter; nicht gelöst → zurück in Fach 1.

Gut zu wissen:

- Unter Windows gibt es zwei Befehlszeilen: **PowerShell** und **cmd**. Wechseln mit `cmd`,
  `powershell`, zurück mit `exit`. Befehle wie `Get-Service` gehen nur in der PowerShell.
- Unter Linux zählt Groß-/Kleinschreibung. Root-Rechte bekommst du mit `sudo` vor dem Befehl
  (oder `sudo -i` für eine root-Shell, zurück mit `exit`). Dateibefehle wie `ls -l`, `cd`, `cat`,
  `grep`, `tail -n`, `chmod`, `chown`, `mkdir`, `cp`, `mv`, `rm` und Pipes (`… | grep fehler`)
  funktionieren in jedem Szenario.
- In der Windows-PowerShell gehen `Get-Location`, `cd`, `dir`, `Get-Content`, `New-Item`, `Copy-Item`,
  `Move-Item` und `Remove-Item`, wo ein Szenario oder eine Lektion Dateien mitbringt.
- Dateien bearbeitest du unter Linux mit `nano <datei>` (bzw. `sudo nano …`): **Strg+O** speichert,
  **Strg+X** beendet, **Strg+K** schneidet eine Zeile aus. Es ist ein vereinfachter Ersatz für nano.
- `help` zeigt die Hilfe der Simulation (nicht die echte Hilfe des Systems).
- Blaue Zeilen mit `[N3XTBYT3]` sind Meldungen der Simulation, keine echten Systemtexte.
- **UNGEPRÜFT** (orange) heißt: Das Szenario hat Claude geschrieben, du hast es noch nicht mit
  dem echten System verglichen. Die Quelle steht rechts unten.

## Spielstand

Liegt als lesbare JSON-Datei je System in deinem Datenordner:

- Windows: `%APPDATA%\N3XTBYT3\` (im Explorer in die Adresszeile eingeben)
- Linux: `~/.local/share/n3xtbyt3/`

Dort liegen auch die Einstellungen (Schriftgröße) und deine eigenen Szenarien.

## Eigenes Szenario hinzufügen

Echte Fehler, die du gelöst hast, werden zu neuen Übungen – ohne neue Programmversion.
Anleitung: [`docs/eigenes_szenario.md`](docs/eigenes_szenario.md).
Vorlage: [`vorlagen/szenario_vorlage.json`](vorlagen/szenario_vorlage.json).
Alle Felder: [`daten/szenarien/SCHEMA.md`](daten/szenarien/SCHEMA.md).
Lektionen und Befehlsbuch: [`daten/grundkurs/SCHEMA.md`](daten/grundkurs/SCHEMA.md).

## Mit Claude Desktop verbinden

Ein kleiner MCP-Server lässt Claude Desktop deine Auswertung lesen und Szenario-Entwürfe anlegen
(immer „ungeprüft“). Er läuft nur lokal, ohne Netzwerk. Anleitung: [`docs/mcp.md`](docs/mcp.md).

## Prüfen

```bash
python -m unittest
```

Prüft unter anderem: jedes Szenario lädt und ist mit seinem Lösungsweg lösbar, jede Lektion lässt sich
durchspielen, jedes Beispiel im Befehlsbuch funktioniert in der Simulation, und im Programm kommen keine
Systemaufrufe oder Netzwerkzugriffe vor.

Die `.exe` kann sich selbst prüfen (PowerShell, im Ordner der `.exe`):

```powershell
.\N3XTBYT3.exe --selbsttest
```

Das Ergebnis steht danach in `%APPDATA%\N3XTBYT3\selbsttest.txt`.

## Lizenzen

Beigelegte Schriften: DejaVu Sans und DejaVu Sans Mono (freie Lizenz, siehe
`n3xtbyt3/oberflaeche/schriften/LIZENZ-DejaVu.txt`).
