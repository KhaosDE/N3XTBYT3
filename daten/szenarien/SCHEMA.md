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
| `erklaerung` | Warum das die Lösung ist. Erscheint nach dem Lösen. Text oder Liste von Zeilen; die Zeilen werden zu Fließtext verbunden, eine leere Zeile beginnt einen neuen Absatz. |
| `begriffe` | Fachbegriffe mit kurzer Erklärung: `{"DNS": "übersetzt Namen in IP-Adressen"}`. |
| `loesung` | Liste der Befehle, die das Szenario lösen. Ein Test spielt sie automatisch durch. Unter Linux darf ein Schritt auch `{"speichern": "/pfad", "inhalt": …}` sein: das Speichern der Datei im Editor nach `nano`. |

## Freiwillige Felder

| Feld | Inhalt |
|---|---|
| `shell` | Womit das Szenario startet. Windows: `powershell` (Standard) oder `cmd`. Linux: `bash`. |
| `dateien` | Simulierte Dateien (siehe „Dateien (Linux)“ und „Dateien (Windows)“). |
| `voraussetzung` | id einer Grundkurs-Lektion, die zu diesem Szenario passt, z. B. `gk-win-dienste`. Die Liste zeigt dann „braucht: Lektion 7“, solange die Lektion nicht fertig ist – nur ein Hinweis, keine Sperre. |
| `rechner` | Weitere Rechner, die man per `ssh` bzw. `Enter-PSSession` erreicht (siehe „Mehrere Rechner“). |
| `ticket` | Das Szenario erscheint auch im Ticket-Modus (siehe „Tickets“). |

## Mehrere Rechner

```json
"rechner": {
  "srv-web01": {
    "system": "linux_server",
    "zustand": {"php_aktiv": false},
    "dateien": {"/var/log/nginx/error.log": ["…"]},
    "befehle": [ … wie oben … ],
    "zugang": ["ssh admin@srv-web01", "ssh srv-web01"]
  }
}
```

* Der Name ist der Rechnername (klein geschrieben). Der Rechner, an dem das Szenario beginnt, heißt
  wie sein `hostname` (z. B. `pc-buero-07`).
* `zugang` ist freiwillig. Standard: Linux `ssh <benutzer>@<name>` und `ssh <name>`;
  Windows `Enter-PSSession -ComputerName <name>` und `Enter-PSSession <name>` (nur in der PowerShell).
  Zurück geht es mit `exit` (Windows auch `Exit-PSSession`).
* Jeder Rechner hat seinen eigenen Zustand und die allgemeinen Befehle seines Systems.
* Auf Werte eines anderen Rechners zeigt man mit Vorsilbe: `"srv-web01:php_aktiv"`. Im `ziel` und in den
  Befehlen des Startrechners gelten Schlüssel ohne Vorsilbe für den Startrechner, in den Befehlen eines
  weiteren Rechners für diesen Rechner.

## Tickets

```json
"ticket": {"nummer": "T-2026-0412", "von": "Herr Neumann (Vertrieb)", "dringlichkeit": "hoch",
           "betreff": "Webshop kaputt", "text": ["Seit heute Morgen …"]}
```

`dringlichkeit`: `niedrig`, `mittel`, `hoch` oder `kritisch`. Ist das Ziel erreicht, schließt man das Ticket
mit F3 und einer kurzen Lösungsnotiz; die Notiz kommt in den Spielstand.

## Dateien (Linux)

```json
"dateien": {
  "/etc/hosts": ["127.0.0.1 localhost", "192.168.10.20 intranet.firma.internal"],
  "/etc/ssh/sshd_config": {"inhalt": ["Port 22"], "rechte": "644", "besitzer": "root:root"},
  "/home/anna/backup.sh": {"inhalt": "#!/bin/bash", "rechte": "rw-r--r--", "besitzer": "anna:anna"},
  "/var/www/html/": {},
  "/etc/neu.conf": null
}
```

* Schlüssel ist der volle Pfad. Ein `/` am Ende heißt: leeres Verzeichnis. Ordner, in denen Dateien
  liegen, gibt es automatisch.
* Wert: Text, Liste von Zeilen oder Objekt mit `inhalt`, `rechte` (`rw-r--r--` oder `644`),
  `besitzer` (`benutzer:gruppe`, Standard `root:root`, im Home-Ordner der Benutzer) und `zeit` (für `ls -l`).
* `null`: Die Datei gibt es am Anfang nicht, sie darf aber entstehen (z. B. mit nano).
* Im Zustand stehen sie als `datei:/pfad` (Inhalt), `rechte:/pfad`, `besitzer:/pfad`. So kann ein
  `ziel` oder `wenn` den Inhalt prüfen, und `setze` kann Dateien ändern (`null` löscht).
* Eingebaut (müssen nicht ins Szenario): `pwd`, `cd`, `ls` (-l -a -h), `cat`, `less`, `head`, `tail`,
  `grep` (-i -n -v -c), `chmod`, `chown`, `nano` (Editor), `sudo` (auch `sudo -i`), Filter hinter Pipes
  (`… | grep`, `head`, `tail`, `sort`, `wc -l`). Ein Befehl im Szenario mit gleichem Muster hat Vorrang.
* Eingebaut sind außerdem `mkdir` (-p), `touch`, `cp` (-r), `mv` und `rm` (-r -f). Neue Dateien bekommen wie
  unter Ubuntu für normale Benutzer die Rechte `rw-rw-r--` (Ordner `rwxrwxr-x`), für root `rw-r--r--`.
* Der Zustand `root` ist `true`, während ein Befehl mit `sudo` läuft – so kann ein Fall
  `{"wenn": {"root": false}, …}` die Fehlermeldung ohne sudo zeigen.

## Dateien (Windows)

```json
"dateien": {
  "C:\\Users\\mberger\\Documents\\": {"modus": "d-r---", "zeit": "11/2/2026 17:41"},
  "C:\\Users\\mberger\\Documents\\notiz.txt": ["Zeile 1", "Zeile 2"],
  "C:\\Users\\mberger\\Documents\\neu.txt": null
}
```

* Pfade beginnen mit dem Laufwerk. Ein `\` am Ende heißt Ordner. Groß-/Kleinschreibung zählt beim Suchen
  nicht; angezeigt wird die Schreibweise aus den Daten.
* Wert: Text, Liste von Zeilen oder Objekt mit `inhalt`, `zeit` (`M/T/JJJJ HH:MM`, wie im Beispiel von
  Get-ChildItem in der Microsoft-Doku) und `modus` (Spalte Mode, z. B. `-a----`, `d-r---`).
* Sobald ein Szenario Windows-Dateien hat, gehen in der PowerShell: `Get-Location` (pwd), `Set-Location`
  (cd, auch `cd..`), `Get-ChildItem` (dir, ls; -Name, -File, -Directory, -Filter, `*.txt`), `Get-Content`
  (type, cat; -TotalCount, -Tail), `New-Item` (-Name, -ItemType File/Directory, -Value), `mkdir`,
  `Copy-Item` (-Recurse), `Move-Item`, `Remove-Item` (-Recurse). In der cmd sind sie nicht nachgebaut.
* Im Zustand: `datei:C:\\…` (Inhalt, `null` = gibt es nicht), `verzeichnis:C:\\…` (`true`/`false`). Einen
  Ordner, der erst entstehen soll, trägt man in den `zustand` ein: `"verzeichnis:C:\\…\\Archiv": false`.

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
| `frage` | Freiwillig, nur mit `bedeutung`. Genaue Aufgabe für das Befehls-Training, wenn die Parameter wichtig sind, z. B. „Zeige den Status des Dienstes Spooler“. Ohne `frage` wird `bedeutung` gefragt. |
| `shell` | Freiwillig. In welcher Shell der Befehl geht: `powershell`, `cmd`, `bash` oder eine Liste. Ohne Angabe: Befehle der Form Verb-Nomen (`Get-Service`) nur in der PowerShell, alle anderen in jeder Shell des Systems. Aliase wie `gsv` bitte mit `"shell": "powershell"` kennzeichnen. |
| `falsch` | Freiwillig. `true`, wenn der Befehl zwar echt ist, aber hier die falsche Wahl (z. B. Neustart als Holzhammer). Dann **muss** `warum` dabei sein. Zählt als falscher Befehl. |
| `warum` | Erklärung, warum der Befehl hier falsch ist. Erscheint rechts im Hinweisbereich. |

### Felder eines Falls

| Feld | Inhalt |
|---|---|
| `wenn` | Bedingung (siehe unten). Ohne Angabe passt der Fall immer. |
| `ausgabe` | Was das System ausgibt. Text oder Liste von Zeilen. Leer lassen, wenn der echte Befehl nichts ausgibt (viele PowerShell-Befehle). |
| `fehler` | `true`, wenn die Ausgabe eine Fehlermeldung ist (wird rot angezeigt). |
| `notiz` | Meldung der Simulation (blau) **nach** einer echten Ausgabe, z. B. „Gekürzt: Im echten System stehen hier über 100 Prozesse.“ |
| `sim` | `true`, wenn die Ausgabe eine Meldung der Simulation ist und kein echter Systemtext (blau, mit `[N3XTBYT3]`). Für Fälle, in denen die echte Ausgabe nicht sicher bekannt ist, ein Fenster aufgehen würde oder eine Rückfrage nicht nachgebaut ist. |
| `setze` | Änderungen am Zustand, z. B. `{"dienst_spooler": "Stopped"}`. Mit `{"+": 1}` oder `{"-": 1}` wird gerechnet. Die Änderung gilt schon für `{…}`-Platzhalter in der Ausgabe dieses Falls. |
| `aktion` | Nur für allgemeine Befehle: `leeren` (Bildschirm), `hilfe`, `exit`, `wechsel:<shell>`. |

### Bedingungen (`wenn` und `ziel`)

Alle genannten Schlüssel müssen passen.

* Gleichheit: `{"dienst_spooler": "Running", "admin": true}`
* Vergleich: `{"frei_gb": {">=": 10}}` – erlaubt sind `<`, `<=`, `>`, `>=` (nur Zahlen),
  `nicht` (`{"status": {"nicht": "Stopped"}}`) und `in` (`{"status": {"in": ["A", "B"]}}`).
* Text: `enthaelt` / `enthaelt_nicht` (Teiltext), `zeile_enthaelt` / `keine_zeile_enthaelt`
  (Teiltext nur in Zeilen, die nicht mit `#` oder `;` beginnen – für Konfigurationsdateien).
  Beispiel: `{"datei:/etc/hosts": {"keine_zeile_enthaelt": "192.168.10.20"}}`.

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
* **Von selbst gleichwertig (seit 07.11.2026):** In der PowerShell die Standard-Aliase der Windows
  PowerShell 5.1 (`gsv`, `sasv`, `spsv`, `gps`, `ps`, `spps`, `kill`, `gcm`, `gci`, `dir`, `ls`, `sl`, `cd`,
  `chdir`, `gc`, `cat`, `type`, `gl`, `pwd`, `ni`, `cpi`, `copy`, `cp`, `mi`, `move`, `mv`, `ri`, `del`, `rm`,
  `erase`, `rd`, `rmdir`, `cls`, `clear`, `help`) – nicht in der cmd. Bei Get-Service, Start-Service,
  Stop-Service, Restart-Service, Get-Process, Get-Command und Get-Help ist `-Name X` dasselbe wie `X`
  (nicht bei Stop-Process). Diese Formen muss ein Szenario nicht als eigenes Muster angeben.
* Andere Schreibweisen (z. B. eine andere Option, die dasselbe bewirkt) als weiteres Muster angeben.

## Was die Simulation bei anderen Eingaben meldet

Alle Meldungen der Simulation beginnen mit `[N3XTBYT3]` und sind keine echten Systemtexte.

* Befehl im Szenario unbekannt: „In dieser Simulation nicht vorhanden“ plus Hinweis; bei einem Tippfehler
  (bis 5 Zeichen 1 Fehler, länger 2; vertauschte Nachbarbuchstaben zählen als 1) „Meintest du …?“.
* Bekannter Befehl, ein bis zwei Wörter mit Tippfehler: „Fast! Schau dir „prcoess“ an – gemeint ist
  vermutlich „Process“.“ (verglichen mit allen Mustern dieses Befehls).
* Befehlsname bekannt, aber andere Parameter: „kennt diese Simulation, aber nicht in dieser Form“.
* Befehl gehört in die andere Shell (z. B. `Get-Service` in cmd): Hinweis zum Wechseln.

## Regeln für den Inhalt

* Jede Ausgabe muss zur offiziellen Doku passen (Microsoft Learn, man-Pages).
  Bei Unsicherheit lieber kürzen als erfinden.
* Nur erfundene Namen, Firmen und Adressen. IP-Adressen aus `192.168.x.x` oder `10.x.x.x`.
  Interne Namen enden auf `.internal` (für interne Netze reserviert), z. B. `intranet.firma.internal`.
* Ausgaben wie im englischen System (so stehen sie in der Microsoft-Doku). Ein deutsches
  Windows zeigt übersetzte Texte – das kann in `begriffe` oder `erklaerung` stehen.
