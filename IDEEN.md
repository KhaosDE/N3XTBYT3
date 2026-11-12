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

## Grundkurs: Jede Aufgabe nur mit vorher Gezeigtem lösbar
Status: freigegeben
Datum: 12.11.2026
Was: Im Grundkurs verlangen 17 Aufgaben einen Befehl, der vorher in keinem Mitmachen-Teil
vorgeführt wurde. Das wird behoben, und eine feste Regel samt Test verhindert es künftig.
Warum: Tobi meldet aus Windows-Lektion 6: Er soll Excel beenden, aber `taskkill` und
`Stop-Process` wurden nie gezeigt oder erklärt. Der Aufbau „Erklären → Mitmachen → Selbst
probieren“ verspricht, dass man beim Selbst-Probieren nur anwendet, was man gesehen hat.
Gefunden mit `werkzeuge/didaktikpruefung.py` (Stand 12.11.2026).

### Regel (gilt ab sofort für alle Lektionen)
Jede Aufgabe muss mit Befehlen lösbar sein, die im Mitmachen-Teil dieser oder einer früheren
Lektion vorgeführt wurden (oder im vorausgesetzten Kurs: Windows vor Windows Server, Linux vor
Linux Server). Ausnahme nur als **ausdrückliche Suchaufgabe**: Der Aufgabentext sagt dann
selbst, dass der Befehl neu ist und womit man ihn findet, z. B. „Den Befehl kennst du noch
nicht. Finde ihn mit Get-Command *Restart*“ bzw. „… mit apropos“. Solche Aufgaben sind im
Lektionsformat gekennzeichnet (neues Feld `"suchaufgabe": true`), erst ab der Hilfe-Lektion
(Lektion 3) erlaubt und höchstens eine pro Lektion.

### Gruppe 1 – Kernhandlung der Lektion fehlt (zwingend im Mitmachen vorführen)
Das ist genau Tobis Fall: Die Lektion handelt davon, wird aber nie gezeigt.
- `gk-win-prozesse` Aufgabe 1+2 (`taskkill /IM …`, `/F`): Im Mitmachen an einem **anderen**
  hängenden Programm vorführen (z. B. Editor `notepad.exe`), damit für die Aufgaben mit Excel
  noch etwas zu tun bleibt: `taskkill /IM notepad.exe`, dann erzwungen mit `/F`, dazu
  `Stop-Process -Name notepad` als PowerShell-Weg. Erklärung „höflich gegen erzwungen“
  (was `/F` macht, warum Ungespeichertes verloren geht).
- `gk-lin-prozesse` Aufgabe 1+2 (`kill`, `kill -9`): genauso an einem anderen Prozess
  vorführen; Signal TERM gegen KILL einfach erklären.
- `gk-lin-rechte` Aufgabe 2 (`chown`): Die Lektion zu Rechten zeigt `chown` nie. Im Mitmachen
  an einer anderen Datei vorführen (`sudo chown …`), Benutzer:Gruppe erklären.
- `gk-ls-logs` Aufgabe 1 (`chown -R`): wird durch `gk-lin-rechte` mit abgedeckt, wenn dort
  `chown` gezeigt wird; zusätzlich `-R` (ganzer Ordner) im Mitmachen dieser Lektion zeigen.

### Gruppe 2 – Neuer Befehl nach dem Verb-Nomen-Prinzip (vorführen oder Suchaufgabe)
`gk-win-dienste` A2 `Restart-Service`, `gk-win-netzwerk` A1 `Test-Connection`, `gk-srv-server`
A2 `Exit-PSSession`, `gk-srv-ad-benutzer` A1 `Unlock-ADAccount`, `gk-srv-ad-gruppen` A1
`Add-ADGroupMember`, `gk-srv-features` A1 `Install-WindowsFeature`.
Je Lektion entscheiden (einfachere Lösung, in `STAND.md` festhalten): entweder im Mitmachen
vorführen, oder zur gekennzeichneten Suchaufgabe machen, deren Text auf `Get-Command`
verweist. Höchstens eine Suchaufgabe pro Lektion – der Rest wird vorgeführt.

### Gruppe 3 – Lange Spezialbefehle (immer vorführen, nicht erraten lassen)
`gk-srv-dns` A1 `Add-DnsServerResourceRecordA`, `gk-srv-dhcp` A1 `Set-DhcpServerv4Scope`,
`gk-srv-fehlersuche` A1 `Set-ADAccountExpiration`. Diese Namen samt Parametern kann ein
Einsteiger nicht ableiten. Im Mitmachen an einem anderen Beispiel vorführen (anderer Name,
andere Adresse, anderes Datum), die Aufgabe bleibt die Übertragung.

### Gruppe 4 – Hilfe-Mechanismus auf neuen Befehl übertragen (vermutlich in Ordnung)
`gk-win-hilfe` A3 `ping /?`, `gk-lin-hilfe` A2 `cp --help`: Hier ist der Befehl neu, gelernt
werden soll aber die Hilfe-Art (`/?`, `--help`). Prüfen, ob `/?` bzw. `--help` im Mitmachen
an einem anderen Befehl gezeigt wurde. Falls ja: unverändert lassen. Falls nein: vorführen.

### Weitere Punkte
- Der Erklären-Text darf nichts versprechen, was die Lektion nicht vorführt (Lektion 6:
  „erst höflich, dann erzwungen“).
- Neue Mitmachen-Schritte bekommen wie alle Inhalte `quelle` (Microsoft Learn / man-Page).
- Die Befehle wandern wie gewohnt ins Befehlsbuch und ins Befehls-Training.

### Test und Abnahme
- `werkzeuge/didaktikpruefung.py` wird zum Test `tests/test_didaktik.py`: Jede Aufgabe ist
  mit vorher Gezeigtem lösbar oder als `suchaufgabe` gekennzeichnet; Suchaufgaben nennen im
  Text `Get-Command`, `Get-Help`, `apropos`, `man` oder `--help`, stehen ab Lektion 3 und
  kommen höchstens einmal pro Lektion vor.
- Der Bericht des Werkzeugs zeigt danach 0 Lücken (außer gekennzeichneten Suchaufgaben).
- Tobi spielt Windows-Lektion 6 erneut und weiß bei Aufgabe 1 ohne Hinweis, was zu tippen ist.

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
