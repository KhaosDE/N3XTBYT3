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

## Fehler: Tippfehler im Parameter wird als „falsche Form“ gemeldet
Status: freigegeben
Datum: 07.11.2026
Was: Hat ein Befehl einen Tippfehler in einem Parameter, soll die Simulation den Tippfehler
zeigen, statt zu behaupten, der Befehl passe „nicht in dieser Form“.
Warum: Tobi hat in Grundkurs Windows, Lektion 3, Aufgabe 2 `get-command *-prcoess` getippt
(c und o vertauscht). Die Simulation meldete zweimal „kennt diese Simulation, aber nicht in
dieser Form“ und „Der Befehl passt – aber nicht mit diesen Zusätzen“. Für einen Einsteiger
klingt das, als sei `Get-Command` falsch – der Fehler ist aber nur das Wort „prcoess“.
Umfang:
- `n3xtbyt3/kern/grundkurs.py`, `_tipp()`: Die Prüfung auf Tippfehler („Fast! …“) kommt
  **vor** der Meldung „Der Befehl passt – aber nicht mit diesen Zusätzen“. Verglichen wird
  nicht nur mit `schritt.eingabe` (beim Selbst-Probieren leer oder unpassend), sondern auch
  mit den Mustern aus `schritt.loesung`/den Befehlsmustern der Aufgabe.
- Der Tipp nennt die Stelle: „Fast! Schau dir das Wort ‚prcoess‘ an – gemeint ist
  ‚process‘.“ (Wortweise vergleichen; nur das abweichende Wort nennen, nicht die ganze Lösung.)
- `n3xtbyt3/kern/sitzung.py`, Meldung „kennt diese Simulation, aber nicht in dieser Form“:
  dieselbe Wortprüfung gegen die bekannten Muster dieses Befehls; bei einem ähnlichen Muster
  „Meintest du …?“ mit dem abweichenden Wort. Gilt für Grundkurs und Szenarien in allen
  Systemen.
- Echtes Verhalten nachbilden, wo es sicher belegt ist: `Get-Command` mit Platzhalter, auf den
  nichts passt, gibt in der echten PowerShell keine Ausgabe und keinen Fehler (vor dem Einbau
  in der Microsoft-Doku zu Get-Command prüfen; ist das nicht belegt, weglassen). Dann zeigt
  das Terminal eine leere Ausgabe und darunter die blaue Meldung „Kein Befehl passt zu diesem
  Muster – prüf die Schreibweise.“
- Dieselbe Meldung nicht doppelt ausgeben (Terminal und Seitenbereich dürfen sich ergänzen,
  im Terminal steht sie nur einmal).
- Test: `get-command *-prcoess` in Lektion 3, Aufgabe 2 ergibt einen Tipp, der „prcoess“
  nennt; `Get-Command *-Process` löst die Aufgabe weiterhin.

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
