# IDEEN — N3XTBYT3

Ideen für das Programm. Werden im Chat ausgearbeitet und hier eingetragen.
Gebaut wird nur, was `Status: freigegeben` hat (Regel: `CLAUDE.md`, „Ideen aus den Chats“).

Aufbau eines Eintrags:

```
## <Titel>
Status: offen | freigegeben | erledigt (<Datum>)
Datum: <Datum>
Was: <ein bis drei Sätze, was es tun soll>
Warum: <wofür Tobi es braucht>
Umfang: <was dazu gehört, was ausdrücklich nicht>
```

## Grundkurs: Konsole von den Babyschuhen an
Status: erledigt (05.11.2026)
Datum: 05.11.2026
Was: Ein geführter Grundkurs je System, der bei null anfängt: was eine Konsole ist, wie man
einen Befehl eingibt, und Schritt für Schritt, welche Befehle man in welcher Situation
eintippt. Dazu ein Befehlsbuch und ein Lexikon zum Nachschlagen.
Warum: Tobi hat das Programm zum ersten Mal gestartet und wusste nicht, was er tun soll.
Die Szenarien setzen Wissen voraus, das er erst lernen muss. Ohne Grundkurs ist der Einstieg
zu steil.
Umfang: siehe Unterpunkte. Ausdrücklich **nicht**: Szenarien sperren, bis der Kurs fertig ist
(sie bleiben frei wählbar); neue Systemfunktionen über das hinaus, was die Lektionen brauchen.

### Einstieg
- Erster Start (noch kein Spielstand): Willkommensbild statt direkt Hauptmenü. Kurz erklären,
  was N3XTBYT3 ist (Simulation, nichts geht kaputt, Fehler sind erlaubt) und mit
  „Grundkurs starten“ als vorausgewählter Schaltfläche.
- In jedem System steht **„Grundkurs“ als erster Eintrag** in der Liste, über den Szenarien,
  mit Fortschritt (z. B. „Lektion 3 von 9“). Solange der Grundkurs eines Systems nicht fertig
  ist, steht dort ein Hinweis „Empfohlen: zuerst den Grundkurs“.
- Szenarien zeigen in der Liste, welche Lektion sie voraussetzen („braucht: Lektion 6“) —
  als Hinweis, nicht als Sperre. Dafür bekommt das Szenario-Format ein freiwilliges Feld
  `voraussetzung` (Lektions-ID); bestehende Szenarien bekommen es nachgetragen.

### Aufbau einer Lektion
Jede Lektion hat drei Teile, im Seitenbereich angezeigt, im Terminal geübt:
1. **Erklären** — Was ist das, wozu braucht man es im Alltag. Höchstens ein kurzer Absatz,
   Fachbegriffe beim ersten Auftreten erklärt (und ins Lexikon).
2. **Mitmachen** — Schritte, bei denen der Seitenbereich **genau zeigt, was einzutippen ist**.
   Nach jedem Schritt erklärt der Seitenbereich, was die Ausgabe bedeutet („Die Zeile
   IPv4-Adresse ist die Adresse deines PCs im Netz …“). Tippfehler: freundlicher Hinweis,
   was anders war (z. B. Leerzeichen fehlt), und nochmal versuchen.
3. **Selbst probieren** — 2–3 kleine Aufgaben **ohne** vorgegebenen Befehl, nur mit der
   Situation („Finde heraus, wie dein PC heißt“). Mit den bekannten drei Hinweisstufen (F1).
Am Ende: kurze Zusammenfassung „Das kannst du jetzt“ und die neuen Befehle wandern ins
Befehlsbuch und ins Befehls-Training (Lernkartei).

### Lektionen Windows (zuerst bauen)
PowerShell zuerst; cmd nur dort, wo man es im Alltag noch braucht.
1. Was ist eine Konsole? Eingabezeile, Prompt lesen (`PS C:\Users\tobi>`), Befehl tippen,
   Enter, Ausgabe lesen. Pfeiltaste hoch für den letzten Befehl, `cls`. Die Tasten der
   Simulation (F1 Hinweis, Esc zurück).
2. Wo bin ich? Ordner und Pfade: `Get-Location`, `Get-ChildItem` (und `dir`/`ls` als
   Kurzform), `Set-Location`/`cd`, `cd ..`, absolute und relative Pfade, Tab-Ergänzung erklären.
3. Hilfe holen: `Get-Help <Befehl>`, `Get-Help <Befehl> -Examples`, `Get-Command *service*`,
   bei cmd-Befehlen `/?`. Verb-Nomen-Prinzip der PowerShell (Get-, Set-, Start-, Stop-).
4. Infos über den PC: `hostname`, `whoami`, `Get-Date`, `Get-ComputerInfo` (gekürzt),
   `systeminfo`.
5. Dateien ansehen und anlegen: `Get-Content`, `New-Item`, `Copy-Item`, `Move-Item`,
   `Remove-Item` (mit Warnung, was das im echten Leben bedeutet).
6. Programme und Prozesse: `Get-Process`, `Stop-Process -Name …`, `tasklist`, `taskkill`.
   Was ist ein Prozess, was ein „hängendes Programm“.
7. Dienste: `Get-Service`, `Get-Service -Name …`, `Start-Service`, `Stop-Service`,
   `Restart-Service`, Starttyp. Was ist ein Dienst (Beispiel Druckerwarteschlange).
8. Netzwerk-Grundlagen: `ipconfig`, `ipconfig /all`, `ping`, `Test-Connection`,
   `nslookup`, `Resolve-DnsName`, `ipconfig /flushdns`. Begriffe IP-Adresse, Gateway, DNS,
   DHCP — einfach erklärt.
9. Adminrechte: was ist ein Administrator, „Als Administrator ausführen“, woran man eine
   Admin-Konsole erkennt, typische Meldung „Zugriff verweigert“.
10. **So gehst du bei Fehlern vor** (Methode, die in allen Systemen gleich bleibt):
    1 Was genau ist das Problem? 2 Nachsehen (Status, Meldungen) 3 Vermutung 4 Eine Sache
    ändern 5 Prüfen, ob es jetzt geht. Danach ein **geführtes erstes Szenario** (z. B.
    `win-druckwarteschlange`) mit Kommentaren zu jedem dieser fünf Schritte.

### Lektionen der anderen Systeme (danach, gleicher Aufbau)
- **Windows Server** (setzt den Windows-Grundkurs voraus): Was ist ein Server, was eine
  Domäne; Active Directory einfach erklärt (Benutzer, Gruppe, OU, Domänencontroller);
  `Get-ADUser`, `Get-ADGroupMember`, `Search-ADAccount`; Remote-Arbeit mit `Enter-PSSession`;
  Rollen und Features (`Get-WindowsFeature`); DNS und DHCP auf dem Server; Ereignisanzeige
  (`Get-WinEvent`). Abschluss: geführtes Szenario.
- **Linux**: Terminal und Prompt (`anna@pc-lager02:~$`), `pwd`, `ls`, `cd`, Pfade mit `/`,
  `~`; Groß-/Kleinschreibung zählt; Hilfe mit `man` und `--help`; Dateien mit `cat`, `less`,
  `cp`, `mv`, `rm`, `mkdir`; Editor `nano`; Rechte (`ls -l` lesen, `chmod`, `chown`) und
  `sudo`; Pakete mit `apt`; Prozesse (`ps`, `top`, `kill`); Netzwerk (`ip a`, `ping`);
  Pipes `|` und `grep`. Abschluss: Fehlersuche-Methode + geführtes Szenario.
- **Linux Server** (setzt den Linux-Grundkurs voraus): per `ssh` auf einen Server, Dienste
  mit `systemctl status/start/restart/enable`, Protokolle mit `journalctl -u … `, Logs unter
  `/var/log`, Firewall `ufw`, Speicherplatz `df -h`/`du -sh`, Benutzer und Gruppen.
  Abschluss: geführtes Szenario.

### Befehlsbuch (Nachschlagen, eigene Taste z. B. F4, überall erreichbar)
- Je System alle Befehle, die in Lektionen vorkamen: Befehl, was er tut, Beispiel,
  wichtigste Parameter, und **„Wann brauche ich das?“** in einem Satz.
- Zweite Ansicht **„Was tippe ich, wenn …?“**: Alltagssituationen mit den ersten Befehlen,
  z. B. „Kein Internet“ → `ipconfig`, `ping 8.8.8.8`, `ping www.example.com`;
  „Drucker druckt nicht“ → `Get-Service Spooler`; „PC ist langsam“ → `Get-Process`
  sortiert nach CPU; „Programm reagiert nicht“; „Festplatte voll“; „Kann mich nicht anmelden“.
  Genau dieses Wissen ist das Ziel des Kurses.
- Nur Befehle, die in der Simulation auch funktionieren; jeder Eintrag mit Quelle.

### Lexikon (Begriffe, Taste z. B. F5)
- Alle Begriffe aus Lektionen **und** aus den bestehenden Szenarien (`begriffe`) gesammelt,
  alphabetisch, mit Suche. Bei jedem Begriff: in welchen Lektionen/Szenarien er vorkommt.

### Technik
- Lektionen sind **Daten wie Szenarien**: `daten/grundkurs/<system>/<nr>-<id>.json`, Format
  in `daten/grundkurs/SCHEMA.md`, mit `quelle` und `pruefstatus` (selbst geschrieben =
  `ungeprueft`). Die Befehle nutzen dieselbe Befehlsauswertung wie die Szenarien.
- Fortschritt je Lektion im Spielstand des Systems; die Auswertung zeigt den Grundkurs-Stand.
- Befehlsbuch und Lexikon werden aus den Daten erzeugt, nicht von Hand gepflegt.
- Tests: jede Lektion lädt und ist mit den vorgegebenen Eingaben durchspielbar; jeder
  Befehlsbuch-Eintrag funktioniert in der Simulation; jedes Szenario mit `voraussetzung`
  verweist auf eine existierende Lektion.

### Abnahme
- Erster Start zeigt das Willkommensbild, „Grundkurs starten“ führt in Windows-Lektion 1.
- Tobi kommt ohne Vorwissen durch die Windows-Lektionen 1–10, ohne außerhalb des Programms
  nachschlagen zu müssen.
- Befehlsbuch und Lexikon sind von überall erreichbar; „Was tippe ich, wenn …?“ enthält
  mindestens 10 Situationen je System.
- Grundkurse für alle vier Systeme vorhanden.

## Logikprüfung: Tippfehler erkennen, gleichwertige Eingaben annehmen
Status: erledigt (07.11.2026)
Datum: 07.11.2026
Was: Die Simulation weist bei jedem Tippfehler auf das falsch geschriebene Wort hin – im
Grundkurs und in allen Szenarien, auf allen vier Systemen. Eingaben, die im echten System
dasselbe bewirken (Aliase, mit/ohne `-Name`), werden angenommen. Dazu einige Logikfehler.
Warum: Tobi hat in Grundkurs Windows, Lektion 3, Aufgabe 2 `get-command *-prcoess` getippt
(c und o vertauscht). Die Simulation meldete „kennt diese Simulation, aber nicht in dieser Form“
und „Der Befehl passt – aber nicht mit diesen Zusätzen“. Für einen Einsteiger heißt das:
`Get-Command` ist falsch. Der Fehler war nur das Wort „prcoess“.

### Befund (Prüfung am 07.11.2026 mit `werkzeuge/logikpruefung.py`)
Jede Aufgabe wurde bis zum Lösungsschritt gespielt, dann ein Tippfehler eingegeben.
| | Tippfehler erkannt | nur allgemeine Meldung | nicht erkannt |
|---|---|---|---|
| Grundkurs (452 Tippfehler) | 331 | 86 | 35 |
| Szenarien (575 Tippfehler) | 176 | 286 | 91 |
Beispiele:
- Tippfehler im Befehlsnamen (`pnig`, `sduo`, `tial`, `culr.exe`, `Remoev-Item`, `eixt`):
  „In dieser Simulation nicht vorhanden“ ohne Vorschlag (79 Fälle in Szenarien).
- Tippfehler in Argument oder Option (`Get-Help Get-Porcess`, `Get-Volume -DrivLeetter D`,
  `Test-NetConnection … -Prot 80`, `taskkill /IM EXCLE.EXE`): nur „nicht in dieser Form“.
- Tippfehler in Pfad oder Dateiname im Grundkurs (`mkdir Arhciv`, `cd …\Doucments\…`,
  `chmod 600 ~/Dokumente/ebricht.txt`): nur „Das löst Aufgabe 3 noch nicht“.
- Echte Aliase abgelehnt (69 Fälle), auch beim Selbst-Probieren und in Szenarien:
  `gsv Spooler`, `sasv`, `spsv`, `gci`/`dir`/`ls`, `ri`/`del`/`rm`/`erase`, `gps`/`ps`, `gcm`.
- Mit/ohne `-Name` abgelehnt (6 Fälle, Mitmachen): z. B. `Get-Service -Name Spooler` statt
  `Get-Service Spooler`, `Stop-Service W32Time` statt `Stop-Service -Name W32Time`.

### Umfang
1. **Tippfehler im Befehlsnamen** (`sitzung.py`, `_unbekannt_text`): Vor „nicht vorhanden“ mit
   allen bekannten Namen vergleichen (Szenario-Befehle, allgemeine Befehle, eingebaute
   Datei-Befehle, Aliase, `sudo`). Abstand: vertauschte Nachbarbuchstaben zählen als 1 Fehler
   (Damerau-Levenshtein); bis 5 Zeichen höchstens 1 Fehler, länger höchstens 2. Treffer:
   „Meintest du „ping“?“. Nach `sudo` gilt das für den folgenden Befehl.
2. **Tippfehler in Argument oder Option** (`sitzung.py`, Meldung „nicht in dieser Form“):
   Wortweise mit allen Mustern dieses Befehls vergleichen. Weicht nur ein Wort (oder wenige) um
   1–2 Fehler ab: „Fast! Schau dir „prcoess“ an – gemeint ist vermutlich „process“.“ Nur das
   abweichende Wort nennen, nicht den ganzen Befehl. Platzhalter im Muster (`*`) zählen nicht
   als Abweichung.
3. **Tippfehler in Pfaden** (Datei-Befehle Windows und Linux): Die echte Fehlermeldung des
   Systems bleibt. Gibt es im selben Ordner einen Namen mit 1–2 Fehlern Abstand, folgt die
   blaue Meldung „Meintest du „Dokumente“?“.
4. **Grundkurs** (`grundkurs.py`, `_tipp`): Die Tippfehler-Prüfung kommt **vor** „Der Befehl
   passt – aber nicht mit diesen Zusätzen“ und vor „Das löst Aufgabe … noch nicht“. Verglichen
   wird mit `eingabe` **und** `loesung` des Schritts. Gleiche Wortweise wie in Punkt 2.
5. **Echte Aliase der Windows PowerShell 5.1 annehmen** (nur in der PowerShell, nicht in cmd):
   gsv, sasv, spsv, gps, ps, spps, kill, gcm, gci, dir, ls, sl, cd, chdir, gc, cat, type, gl, pwd,
   ni, cpi, copy, cp, mi, move, mv, ri, del, rm, erase, rd, rmdir, cls, clear, help. Vor dem Einbau
   jeden Alias gegen die Microsoft-Doku prüfen (about_Aliases / Liste der Standard-Aliase
   5.1) – nicht belegte weglassen. `curl` und `wget` **nicht** (in 5.1 Alias für
   Invoke-WebRequest, anderes Verhalten als curl.exe). Umsetzung zentral im `Vergleicher`
   (Alias → Befehlsname), damit alle Szenarien ohne Datenänderung profitieren.
6. **Mit/ohne `-Name` gleichwertig** bei Get-Service, Start-Service, Stop-Service,
   Restart-Service, Get-Process, Get-Command, Get-Help (Name ist dort der erste
   Positionsparameter – vorher in der Microsoft-Doku je Befehl prüfen). **Nicht** bei
   Stop-Process: dort ist der erste Positionsparameter `-Id`.
7. **Lektion 3, Aufgabe 2:** `Get-Command *process*` erfüllt die Aufgabe, wie sie dasteht
   („mit einem Platzhalter alle Befehle, die mit Prozessen zu tun haben“), wird aber nicht
   gewertet. Annehmen und den vorhandenen Hinweis („wird im echten System sehr lang …
   genauer ist *-Process“) als Erklärung dazu zeigen. Dasselbe für `*service*` in Aufgabe 1,
   falls dort gleich.
8. **`chown` mit falsch geschriebenem Benutzer oder Gruppe** läuft still durch
   (`sudo chown -R www-data:www-adta …` in ls-upload-rechte, `shop:hsop` in ls-worker-rechte).
   Im echten System: Fehlermeldung „chown: invalid user“ bzw. „invalid group“ (Wortlaut vor dem
   Einbau in der man-Page/coreutils prüfen). Unbekannte Benutzer/Gruppen → diese Meldung,
   Zustand unverändert, plus Vorschlag nach Punkt 3.
9. **Keine doppelten Meldungen:** Im Terminal steht eine Meldung höchstens einmal; der
   Seitenbereich darf ergänzen.
10. **`Get-Command` mit Platzhalter ohne Treffer** gibt im echten System keine Ausgabe und
    keinen Fehler (vor dem Einbau in der Microsoft-Doku prüfen, sonst weglassen). Dann leere
    Ausgabe plus Meldung nach Punkt 2.

### Test und Abnahme
- `werkzeuge/logikpruefung.py` wird zu einem Test (`tests/test_logik.py`): Jeder erzeugte
  Tippfehler bekommt eine Meldung, die das falsche Wort nennt („Meintest du“ / „Fast!“) –
  Ausnahme: Tippfehler, die im echten System einen gültigen anderen Befehl ergeben; die zeigen
  die echte Ausgabe. Jeder Alias aus Punkt 5 und jede Schreibweise aus Punkt 6 löst den Schritt.
- Tobis Fall: `get-command *-prcoess` in Lektion 3, Aufgabe 2 nennt „prcoess“;
  `Get-Command *-Process` und `gcm *-Process` lösen die Aufgabe.
- Der Bericht des Werkzeugs zeigt danach 0 Fälle „nur allgemeine Meldung“ und 0 Fälle „nicht
  erkannt“; Zahlen in `STAND.md` festhalten.

## Lernprinzip: Alles wird erklärt, bevor es verlangt wird (Grundkurs und Szenarien)
Status: freigegeben
Datum: 20.11.2026 (ersetzt den Eintrag „Jede Aufgabe nur mit vorher Gezeigtem lösbar" vom 12.11.)
Was: Grundkurs und Szenarien werden so überarbeitet, dass jeder Befehl und jeder Zusatz (Option,
Schalter wie `/IM`, `/F`, `-Identity`, `--vacuum-size`) **erklärt** wird, bevor eine Aufgabe ihn
verlangt – nicht nur gezeigt. Jede Erklärung nach einem Schritt erklärt wirklich etwas.
Warum: Tobi, 20.11.2026: In Windows-Lektion 6 soll er Excel beenden, `taskkill` wird aber nirgends
vorher erklärt – nur in den Hinweisen und erst nach dem Lösen. „Alle Aufgaben müssen eine Erklärung
haben … Ziel ist eine funktionierende Lernsoftware, die erklärt, erläutert, das Wissen abfragt und
erprobt." Das Lernprinzip steht jetzt auch in `CLAUDE.md` (Abschnitt „Lernprinzip").

### Befund (`werkzeuge/didaktikpruefung.py`, 20.11.2026; volle Liste: `docs/didaktik-befund-2026-11-20.txt`)
- Grundkurs: 31 Mitmach-Schritte benutzen einen Befehl/Zusatz, der nirgends erklärt wird
  (z. B. `whoami`, `Set-Location`, `Start-Service`, `-StartupType`, `ipconfig /all`, `-ComputerName`,
  `Get-ADGroupMember`, `-ZoneName`, `--disk-usage`).
- Grundkurs: 25 Aufgaben verlangen etwas, das vorher nicht erklärt wurde (z. B. `taskkill /IM` in
  Lektion 6, `Restart-Service`, `Test-Connection`, `Unlock-ADAccount -Identity`,
  `Set-DhcpServerv4Scope -ScopeId -EndRange`, `journalctl --vacuum-size`, `curl -I`).
- Grundkurs: 47 Erklärungen nach einem Schritt sind nur Bestätigungen („Genau: pwd.", „Angelegt.",
  „Gut!").
- Szenarien: 22 Szenarien nutzen Befehle/Zusätze, die weder im Grundkurs noch im Szenario erklärt
  sind (z. B. `Get-Volume -DriveLetter`, `icacls`, `Get-SmbShareAccess`, `-Identity`, `uptime`, `ls -la`).
- Ein paar Treffer sind gewollt und kein Fehler (z. B. `Get-Kaffee` in Lektion 1 als Beispiel für
  einen unbekannten Befehl) – siehe „Ausnahmen".

### Regeln für jede Erklärung
1. **Neuer Befehl** (beim ersten Auftreten, im Erklären-Absatz oder im Text/`danach` des
   Mitmach-Schritts): Was macht er? Wozu brauchst du ihn im Alltag? Woher kommt der Name
   (z. B. taskkill = „Task töten“)? Wie liest du die Ausgabe?
2. **Neuer Zusatz** (Option/Schalter): Was bewirkt er, was passiert ohne ihn? Beispiel: `/IM` =
   Image-Name, also der Name der Programmdatei (`EXCEL.EXE`); `/F` = force, erzwingen.
3. **Mitmachen zeigt es vor, die Aufgabe überträgt es.** Die Aufgabe nutzt das Gelernte an einem
   anderen Beispiel (anderes Programm, anderer Name, andere Adresse) – sie verlangt nie etwas Neues.
   Ausnahme nur als gekennzeichnete Suchaufgabe (siehe unten).
4. **`danach` erklärt, nicht nur bestätigen:** Warum hat das funktioniert, was zeigt die Ausgabe,
   wann brauchst du das in echt? Mindestens zwei Sätze. „Richtig." allein reicht nie.
5. **Szenarien:** Jeder Befehl und Zusatz der Lösung ist entweder in einer Lektion erklärt, die das
   Szenario als `voraussetzung` nennt, oder in der `erklaerung`/den `begriffe` des Szenarios selbst.
   Die Erklärung nach dem Lösen geht die Lösung Schritt für Schritt durch (was, warum).
6. Alle neuen Texte mit Quelle (Microsoft Learn / man-Page); Inhalte bleiben `ungeprueft`.

### Lektion 6 (Windows, Prozesse) – genau so umbauen
- Erklären-Absatz: kündigt an, dass du zwei Wege lernst: `taskkill` (älteres Programm, geht in
  PowerShell und cmd) und `Stop-Process` (PowerShell).
- Neue Mitmach-Schritte **an einem anderen hängenden Programm** (z. B. Editor, `notepad.exe`), damit für
  Excel in den Aufgaben noch etwas zu tun bleibt:
  1. `taskkill /IM notepad.exe` – erklärt: taskkill = „Task töten“, `/IM` = Image-Name (Name der
     Programmdatei, steht in der Spalte „Image Name“ von tasklist); ohne `/F` schickt taskkill nur die
     Bitte „schließ dich“ (wie ein Klick aufs X) – ein hängendes Programm reagiert darauf nicht.
     Die echte Rückmeldung zeigen (laut Doku).
  2. `taskkill /IM notepad.exe /F` – erklärt: `/F` = force, Windows beendet das Programm sofort;
     Ungespeichertes ist verloren.
  3. Alternative mit der PID: `taskkill /PID <Nummer> /F` – erklärt, warum die PID eindeutig ist, wenn
     mehrere Prozesse gleich heißen.
  4. `Stop-Process -Name notepad` (bzw. `-Id`) – erklärt: der PowerShell-Weg, beendet sofort (wie `/F`);
     `-Name` ohne `.exe`.
- Danach die Aufgaben mit Excel (höflich, erzwungen, nachprüfen) – jetzt reine Übertragung.

### Suchaufgaben (Ausnahme von Regel 3)
Erlaubt ab der Hilfe-Lektion (Lektion 3), höchstens eine pro Lektion, gekennzeichnet mit
`"suchaufgabe": true`. Der Aufgabentext sagt selbst, dass der Befehl neu ist und womit man ihn
findet (`Get-Command`, `Get-Help`, `apropos`, `man`, `--help`). Die Erklärung danach erklärt den
gefundenen Befehl vollständig nach Regel 1 und 2.

### Ausnahmen
Gewollt unbekannte Befehle (Vorführung einer Fehlermeldung, z. B. `Get-Kaffee`) bekommen am Schritt
`"absichtlich_unbekannt": true`; die Prüfung überspringt sie.

### Vorgehen
Lektion für Lektion durchgehen, alle vier Kurse, danach alle Szenarien. Nicht nur die Befunde des
Werkzeugs abarbeiten: Das Werkzeug prüft nur, ob ein Wort in einem Erklärtext vorkommt, nicht ob die
Erklärung gut ist. Jede Lektion zusätzlich von Hand lesen, als wäre man Einsteiger: Weiß ich bei
jeder Aufgabe ohne Hinweis, was zu tippen ist und warum?

### Test und Abnahme
- `werkzeuge/didaktikpruefung.py` wird zum Test `tests/test_didaktik.py` und zeigt **0 Befunde**
  (Ausnahmen nur über `suchaufgabe` / `absichtlich_unbekannt`). Der Test prüft außerdem: höchstens eine
  Suchaufgabe pro Lektion, erst ab Lektion 3, Text nennt das Suchwerkzeug.
- In `STAND.md`: Zahl der Befunde vorher/nachher, je Kurs.
- Tobi spielt Windows-Lektion 6 und weiß bei jeder Aufgabe ohne Hinweis, was zu tippen ist.

## Szenarien aus gelösten Problemen in Tobis Notizen
Status: offen
Datum: 04.11.2026
Was: Gelöste Probleme aus Tobis Notizen (Einträge mit `#lehre`) als Szenarien übernehmen.
Warum: echte Fehler als Lernstoff.
Umfang: Tobi liefert die Texte; nichts selbst zusammensuchen.

## Prüfungsmodus
Status: offen
Datum: 04.11.2026
Was: Szenarien ohne Hinweise und mit Zeitlimit, passend zur Weiterbildung.
Warum: Prüfungssituation üben.
Umfang: noch nicht ausgearbeitet.

## Weiterbildung A: Szenarien zum ILS-Lehrplan (Windows Server)
Status: offen
Datum: 12.11.2026
Was: Neue Fehlerszenarien, die die Themen des ILS-Lehrgangs „Netzwerkadministrator für MS
Windows Server" abdecken, soweit sie sich im Terminal nachbauen lassen.
Warum: Prüfungsstoff der Weiterbildung; bisher fehlt vor allem die PowerShell-Vertiefung.

### ILS-Lehrplan (recherchiert 12.11.2026, Quellen unten)
Themen laut ILS: Netzwerk-Grundlagen (Topologien, Hardware, LAN-WAN, TCP/IP, IPv4/IPv6),
Windows Server 2019/2022, Domäne und Active Directory, zentrale Benutzer-/Ressourcen-
verwaltung, Gruppenrichtlinien, Bereitstellungsdienste, Routing, DNS und DHCP, Fernzugriff
(Remotedesktop, VPN/IPSec), Webserver IIS, Druckdienste, heterogene Netze mit Linux
(Debian/openSUSE), Sicherheitsaspekte, Windows PowerShell, Hyper-V, Server Core,
Virtualisierung (VMware). 21 Monate, ca. 7 h/Woche.
**Nicht ausdrücklich genannt:** Subnetting und Datensicherung (Subnetting steckt sachlich im
TCP/IP-Teil). Backup wird daher in A nur optional geführt.

### Was A abdeckt (Terminal) – nach Priorität
1. **PowerShell vertiefen** (ILS „Windows PowerShell"; fehlt ganz, höchste Priorität):
   Pipeline `|`, `Where-Object` (filtern), `Sort-Object`, `Select-Object`, `Measure-Object`
   (zählen/summieren), `Format-Table`/`Format-List`, Variablen, eine einfache `foreach`-Schleife.
2. **Routing und Netzwerk-Diagnose** (ILS „Routing", „LAN-WAN"): `route print`, Routing-
   Tabelle lesen, `tracert`, `pathping`, `netstat -ano`, `Test-NetConnection` genauer.
3. **DNS/DHCP vertiefen** (ILS „DNS und DHCP"; Grundlagen schon da): Zonentypen, Weiter-
   leitung, Reverse-Lookup, DHCP-Reservierung, Lease anzeigen.
4. **Active Directory vertiefen** (ILS „zentrale Benutzerverwaltung", „Gruppenrichtlinien";
   Grundlagen da): Benutzer mit CSV anlegen (`Import-Csv | foreach`), OU verschieben,
   Gruppenmitgliedschaften prüfen, GPO einer OU zuordnen.
5. **IIS Webserver** (ILS „Webserver IIS"): Dienst `W3SVC` prüfen/neu starten, Website mit
   `Get-Website` ansehen, Standardseite erreichbar machen.
6. **Druckdienste auf dem Server** (ILS „Druckdienste"; PC-Spooler schon da): Druckerwarte-
   schlange auf dem Server, hängenden Druckauftrag entfernen.
7. **Sicherheit/Fernzugriff** (ILS „Sicherheitsaspekte", „Remotedesktop"; Abwehr-konform,
   Regel 5): Firewall-Regel setzen/prüfen (`Get-NetFirewallRule`, `New-NetFirewallRule`),
   RDP-Zugang prüfen. Kein VPN/IPSec (Theorie, nicht im Terminal) – gehört zu B.
8. **Optional, eingeschränkt:** Backup (`wbadmin`), Hyper-V/Server Core als reine
   Befehlsübung (keine Oberfläche).

### Nicht in A (gehört zu B oder entfällt)
TCP/IP, IPv4/IPv6, Subnetting, Topologien, Netzwerkhardware, OSI → Rechnen/Quiz in B.
VMware/Hyper-V-Oberfläche, physische Hardware, VPN-Einrichtung → nicht im Simulator
(Regel C aus dem Konzept), höchstens als Quiz-Begriffe.

### Vorgehen
Themen 1–7 nacheinander, Thema 1 (PowerShell) zuerst und als eigener kleiner Grundkurs-
Zweig (Mitmachen → Selbst probieren), die übrigen als Fehlerszenarien in den bestehenden
Systemen. Jedes mit `quelle` (Microsoft Learn) und `pruefstatus: ungeprueft`. Reiht sich in
die vier Systeme ein, kein neues Format. Der Didaktik-Test (oben) gilt auch hier.

### Vor der Freigabe (hier im Chat)
Thema 1 (PowerShell-Pipeline) wird als Erstes ausgearbeitet: Liste der 6–8 Aufgaben mit
geprüften Ausgaben. Dann freigeben. Die übrigen Themen folgen einzeln.

Quellen ILS-Lehrplan:
- https://www.fernstudi.net/weiterbildung/informatik/netzwerktechnik/11535
- https://www.studieren-studium.com/studieren/Gepruefte_r_Netzwerkadministrator_in_fuer_MS_Windows_Server_ILS_Lehrgang_ILS_Institut_fuer_Lernsysteme_122847

## Weiterbildung B: Übungsarten ohne Terminal (Subnetting, Theorie-Quiz)
Status: offen
Datum: 12.11.2026
Was: Zwei neue Übungsarten, die kein Terminal brauchen und als eigener Modus laufen:
- Subnetting rechnen: Netz, Broadcast, Hostzahl, CIDR — Aufgaben mit Zufallswerten und
  Korrektur, Rechenweg als Erklärung.
- Theorie-Quiz: OSI-Modell, Netzwerk-Topologien, Netzwerkhardware, wichtige Ports und
  Protokolle, RAID-Level, Fachbegriffe.
Warum: Prüfungsstoff, der im reinen Befehls-Trainer nicht abbildbar ist. Deckt die
ILS-Themen ab, die A nicht fasst (TCP/IP, IPv4/IPv6, Topologien, Hardware).
Hinweis: Der ILS-Lehrplan nennt „Subnetting" nicht ausdrücklich, sondern „TCP/IP, IPv4 und
IPv6"; Subnetting gehört sachlich dazu und ist typischer Prüfungsstoff.
Umfang: noch nicht ausgearbeitet. Eigener Menüpunkt neben den Systemen; Fortschritt und
Lernkartei wie bei den Szenarien. Aufgaben und Quizfragen als Daten (nicht im Code), mit
Quelle. Vor dem Bauen: Aufgabentypen und Fragenkatalog hier im Chat festlegen.
