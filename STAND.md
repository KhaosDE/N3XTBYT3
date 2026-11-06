# STAND — N3XTBYT3

Stand: 06.11.2026.

## Aktuell

**M1 bis M4 sind fertig, dazu der Grundkurs „Konsole von den Babyschuhen an“ (G, aus `IDEEN.md`)**
(bis auf deine Abnahmetests, siehe unten). Alle vier Systeme haben jetzt einen Grundkurs
(10 + 8 + 10 + 7 Lektionen), ein Befehlsbuch (F4) und ein Lexikon (F5).

**Neu: Selbst-Update der `.exe`** (dein Wunsch vom 05.11.2026, Ausnahme zu Regel 1 in `CLAUDE.md`).
Das Repository ist seit 05.11.2026 öffentlich; der feste Download-Link und der echte Update-Ablauf
(Release laden, Prüfsumme, Austausch) sind von außen geprüft.

**Nächster Schritt:** Deine Tests und Rückmeldungen – vor allem: Kommst du ohne Vorwissen durch die
Windows-Lektionen 1–10? Danach laufend: deine echten Fehler als Szenarien aufnehmen und Ausgaben,
die vom echten System abweichen, korrigieren.

## Fertig

- Projektrahmen: `CLAUDE.md`, `PLAN.md`, `STAND.md`, `SITZUNGEN.md`, `IDEEN.md`, `README.md`.
- M1.1 Kern: Szenario-Format (`daten/szenarien/SCHEMA.md`), Lader mit Prüfung,
  Befehlsauswertung, simulierter Zustand, allgemeine Windows-Befehle
  (`daten/allgemein/windows.json`), erstes Szenario `win-dns-cache`, Tests.
- M1.2 Oberfläche (pygame-ce): Hauptmenü mit vier Systemen (leere als „kommt noch“),
  Szenarioliste, Terminal mit Verlauf (Pfeiltasten), Scrollen, Kopfzeile mit System und Shell,
  Seitenbereich mit Aufgabe, Hinweisen (F1, Stufe für Stufe), Begriffen, Erklärung nach dem
  Lösen und deutlich sichtbarem Prüfstatus. Schriftgröße Strg +/−, Vollbild F11.
- M1.3 Spielstand: `spielstand_<system>.json` im Datenordner (lesbares JSON) mit Versuchen,
  gelöst, Hinweisstufen, falschen und unbekannten Befehlen, Zeit und Verlauf.
  Zufallsauswahl bevorzugt ungelöste und schwache Szenarien.
- M1.4 Windows-Inhalte: 13 Szenarien (alle „ungeprüft“, mit Quelle): DNS-Cache, APIPA/DHCP,
  falscher DNS-Server, Netzwerkadapter aus, Druckwarteschlange, Festplatte voll, Dienst deaktiviert,
  Programm hängt, Uhrzeit/Zeitdienst, Konto deaktiviert, Netzlaufwerk, Autostart, sfc mit Adminrechten.
  Vorlage `vorlagen/szenario_vorlage.json`, Anleitung `docs/eigenes_szenario.md`.
  Inhaltstest: nur private IP-Adressen, keine Mailadressen, Vorlage gültig.
- M1.5: GitHub Actions testet bei jedem Push nach `main` unter Windows und Linux, baut die `.exe`
  (PyInstaller), prüft sie mit `--selbsttest` und stellt sie als Artefakt „N3XTBYT3-Windows“ bereit.
  Erster Lauf am 04.11.2026 komplett grün. README in einfachen Worten.

### Abnahme M1 (PLAN.md)

- [x] Hauptmenü mit vier Systemen, nicht gefüllte als „kommt noch“
- [x] Terminal mit Verlauf, Scrollen, Kopf mit Systemname; Seitenbereich mit Aufgabe, Hinweisen,
      Begriffen, Erklärung, Prüfstatus
- [x] Spielstand je System als lesbares JSON im Datenordner
- [x] 13 Windows-Szenarien mit Quelle und „ungeprüft“; Vorlage und Anleitung für eigene Szenarien
- [x] Tests: Laden, Lösbarkeit, Sicherheitstest; `.exe` per GitHub Actions
- [ ] **Tobi:** `.exe` starten, Windows wählen, mindestens drei Szenarien mit Hinweisen lösen,
      beenden, neu starten – Fortschritt ist noch da

### M2

- Lernkartei: Szenarien und Befehle in Fächern 1–5 (Wiederholung nach 0/1/3/7/14 Tagen).
  Falsch oder nicht gelöst → zurück in Fach 1. Die Zufallsauswahl nimmt Fälliges zuerst.
  Die Szenarioliste zeigt Fach und „fällig“.
- Befehls-Training (Eintrag in der Szenarioliste): Fragen „Welcher Befehl …?“ aus den Befehlen der
  Szenarien; richtig / halb (richtiger Befehl, andere Parameter) / falsch. Neues Feld `frage` für
  genaue Aufgaben.
- Auswertung je System: `auswertung_<system>.json` und `.md` im Datenordner, auch als Ansicht im
  Programm. Stärken, Schwächen nach Kategorie und Befehl, häufige Fehler, Empfehlung.
- 16 Windows-Server-Szenarien (alle „ungeprüft“, Quellen geprüft): AD-Konto gesperrt, Passwort
  zurücksetzen, Gruppe fehlt, Konto abgelaufen, GPO greift nicht (falsche OU), DNS-Eintrag fehlt,
  DNS-Weiterleitung, DHCP-Bereich voll, Freigaberechte, NTFS-Rechte (icacls), Feature fehlt,
  Ereignisanzeige (wer hat neu gestartet), alte Logs löschen, RDP-Gruppe, Firewall-Port,
  Vertrauensstellung reparieren.

### M4

- Mehrere Rechner pro Szenario (Feld `rechner`): Wechsel per `ssh` (Linux) oder `Enter-PSSession`
  (Windows), zurück mit `exit`/`Exit-PSSession`. Jeder Rechner hat eigenen Zustand und eigene Dateien;
  Bedingungen können über Rechnergrenzen gehen (`srv-web01:php_aktiv`).
- Ticket-Modus (Kachel 5 im Hauptmenü): Tickets mit Nummer, Absender, Dringlichkeit; Ticket schließen mit F3
  und Lösungsnotiz (kommt in den Spielstand). Zwei Tickets über zwei Rechner:
  „Webshop zeigt 502 Bad Gateway“ (PC → Linux-Webserver) und „Speichern auf Z: geht nicht“
  (PC → Windows-Dateiserver, Schattenkopien).
- MCP-Server `n3xtbyt3_mcp` (ohne Zusatzbibliotheken, nur stdin/stdout): Übersicht, Auswertung, Spielstand,
  Szenarien lesen; Szenario-Entwurf anlegen (immer ungeprüft, prüft Format und Lösungsweg, überschreibt nichts).
  GitHub Actions baut zusätzlich `N3XTBYT3-MCP.exe` und testet sie. Anleitung: `docs/mcp.md`.

### Abnahme M4 (PLAN.md)

- [x] Ein Ticket-Einsatz über zwei Rechner ist spielbar (automatischer Oberflächentest: Ticket öffnen,
      per ssh auf den Server, Dienst starten, zurück, nachprüfen, mit Notiz schließen, Spielstand gespeichert)
- [x] Der MCP-Server liefert die Auswertung eines Systems (automatischer Test und Selbsttest der MCP-.exe im CI)
- [ ] **Tobi:** in Claude Desktop einrichten (`docs/mcp.md`) und fragen: „Wie ist meine Auswertung für Windows?“

### M3

- Simuliertes Dateisystem für Linux: Dateien mit Inhalt, Rechten und Besitzer stehen im Szenario.
  Eingebaut: `pwd`, `cd`, `ls` (-l -a -h), `cat`, `less`, `head`, `tail`, `grep`, `chmod`, `chown`,
  `crontab -l/-e`, `nano` (Editor), `sudo` (auch `sudo -i`), Filter hinter Pipes (grep, head, tail, sort, wc -l).
  Rechte werden geprüft (lesen, schreiben, betreten); ohne sudo kommt „Permission denied“.
- Editor (nano-Ersatz) im Terminalbereich: Strg+O speichern, Strg+X beenden, Strg+K Zeile ausschneiden.
- Ziele können den Inhalt von Konfigurationsdateien prüfen (`zeile_enthaelt`, Kommentare zählen nicht).
- 16 Linux-Szenarien (Ubuntu 24.04 Desktop) und 15 Linux-Server-Szenarien (Ubuntu Server 24.04),
  alle „ungeprüft“ mit Quellen (man7.org, manpages.ubuntu.com, Ubuntu-Doku, nginx/Apache-Doku; Adressen geprüft).

### Abnahme M3 (PLAN.md)

- [x] Alle vier Systeme spielbar (13 + 16 + 16 + 15 Szenarien, alle mit Lösungsweg getestet)
- [x] Auswertung und Lernkartei funktionieren je System (automatischer Test für jedes System)
- [ ] **Tobi:** je System ein, zwei Szenarien spielen; unter Linux einmal eine Datei mit `sudo nano`
      bearbeiten und speichern

### Abnahme M2 (PLAN.md)

- [x] Windows Server spielbar (16 Szenarien, alle mit Lösungsweg getestet)
- [x] Auswertung zeigt nach mehreren Durchläufen plausible Schwächen (automatischer Test)
- [x] Falsch gelöste Szenarien kommen sichtbar öfter wieder (Lernkartei, automatischer Test)
- [ ] **Tobi:** einige Windows-Server-Szenarien spielen, eines absichtlich nicht lösen,
      danach Auswertung ansehen und prüfen, ob die Empfehlung passt

### G — Grundkurs (aus IDEEN.md, freigegeben 05.11.2026)

- Lektionen als Daten: `daten/grundkurs/<system>/<nr>-<id>.json`, Format in `daten/grundkurs/SCHEMA.md`.
  Ablauf: Worum es geht → Mitmachen (rechts steht, was zu tippen ist; nach jedem Schritt eine Erklärung;
  freundliche Tippfehler-Hinweise) → Selbst probieren (Aufgaben mit drei Hinweisstufen, F1) →
  „Das kannst du jetzt“. Fortschritt je Lektion im Spielstand des Systems.
- Windows (10): Konsole, Ordner und Pfade, Hilfe (Get-Help, Get-Command, /?), Infos über den PC,
  Dateien, Prozesse, Dienste, Netzwerk, Adminrechte, Fehlersuche mit Methode (geführt am Druckerproblem).
- Windows Server (8): Server/Domäne/Fernzugriff, AD-Konten, AD-Gruppen, Rollen und Features, DNS, DHCP,
  Ereignisprotokolle, geführte Fehlersuche. Braucht Windows-Lektion 10.
- Linux (10): Terminal, Ordner, Hilfe (man, --help, whatis), Dateien, nano, Rechte und sudo, apt,
  Prozesse mit Pipe und grep, Netzwerk, geführte Fehlersuche (/etc/hosts).
- Linux Server (7): ssh, systemctl, Protokolle (journalctl, /var/log), df/du, ufw, Benutzer und Gruppen,
  geführte Fehlersuche (nginx). Braucht Linux-Lektion 10.
- Neu im Kern: Dateibefehle für die Windows-PowerShell (Get-Location, Set-Location, Get-ChildItem,
  Get-Content, New-Item/mkdir, Copy-Item, Move-Item, Remove-Item); unter Linux zusätzlich mkdir, touch,
  cp, mv, rm. Feld `notiz` (blaue Meldung nach einer echten Ausgabe, z. B. „gekürzt“).
- Oberfläche: Willkommensbild beim ersten Start („Grundkurs starten“ vorgewählt), Grundkurs als erster
  Eintrag jeder Szenarioliste („Lektion 3 von 10 ist dran · Empfohlen: zuerst den Grundkurs“),
  Lektionsliste je System, Lektionsansicht. Szenarien zeigen „braucht: Lektion n“ (Feld `voraussetzung`,
  in allen 62 Szenarien nachgetragen) – nur ein Hinweis, keine Sperre.
- Befehlsbuch (F4, überall): je System Befehl, was er tut, Beispiel, Parameter, „Wann brauche ich das?“,
  Quelle; Sicht „Was tippe ich, wenn …?“ (Windows 14, Windows Server 12, Linux 12, Linux Server 11
  Situationen). Daten in `daten/befehlsbuch/<system>.json`.
- Lexikon (F5, überall): alle Begriffe aus Lektionen und Szenarien, alphabetisch, mit Suche und Fundstellen.
- Befehle geschaffter Lektionen kommen ins Befehls-Training; die Auswertung zeigt den Kursstand und
  empfiehlt die nächste Lektion. Der Selbsttest der `.exe` spielt auch alle Lektionen durch.

- 06.11.2026, Fehler von Tobi behoben: Im Wiederholungsschritt von Lektion 1 („Pfeil hoch“) blieb man nach
  einmal ↑ bei `whoami` hängen, ohne zu erfahren, warum. Jetzt: klarere Anleitung („jeder Druck geht einen
  Befehl weiter zurück“) und ein eigener Hinweis („Das war „whoami“ … Drück ↑ noch einmal“). Außerdem
  gibt es beim Selbst-Probieren immer eine Rückmeldung, wenn ein Befehl die Aufgabe nicht löst („Das löst
  Aufgabe n noch nicht … F1“; bei einem richtigen ersten Teilschritt „Guter erster Schritt …“), ohne die
  Lösung zu verraten. `help` sagt in Lektionen, dass die nächste Aufgabe rechts steht. Neues freies Feld
  `tipp` für Lektionsschritte. Alle Lektionen habe ich zusätzlich mit einem Prüfskript durchsucht (jede
  erlaubte Schreibweise, jede Zielbedingung, jeder letzte Hinweis) – keine weiteren Fehler gefunden.

### Abnahme G (IDEEN.md / PLAN.md)

- [x] Erster Start zeigt das Willkommensbild, „Grundkurs starten“ führt in Windows-Lektion 1
      (automatischer Oberflächentest bis Lektion 2)
- [x] Befehlsbuch und Lexikon sind von überall erreichbar (F4/F5, automatischer Test)
- [x] „Was tippe ich, wenn …?“ hat mindestens 10 Situationen je System (automatischer Test)
- [x] Grundkurse für alle vier Systeme vorhanden; jede Lektion lässt sich vollständig durchspielen
      und jedes Befehlsbuch-Beispiel funktioniert in seiner Lektion (automatische Tests)
- [x] Jede `voraussetzung` zeigt auf eine vorhandene Lektion (automatischer Test)
- [ ] **Tobi:** ohne Vorwissen durch die Windows-Lektionen 1–10 kommen, ohne woanders nachzusehen

### Selbst-Update der .exe (Wunsch Tobi, 05.11.2026)

- Paket `n3xtbyt3_update`: Beim Start der `.exe` fragt es GitHub nach dem neuesten Release dieses
  Repositorys (`build-<n>`). Ist es neuer als die eigene Version, lädt es `N3XTBYT3.exe` und
  `N3XTBYT3.exe.sha256` mit Fortschrittsfenster, prüft die Prüfsumme, benennt die laufende Datei in
  `N3XTBYT3.exe.alt` um, legt die neue an ihren Platz und startet sie. Die neue Version löscht beim Start
  die alte Datei. Jeder Fehler landet in `update.log`; dann startet die alte Version ganz normal.
- GitHub Actions trägt die Laufnummer als Version ein, veröffentlicht bei jedem Push nach `main` ein
  Release `build-<n>` (mit der `.exe`, der Prüfsumme und der MCP-.exe) und behält die neuesten 10.
- Versionsnummer unten im Hauptmenü. Abschalten mit `"auto_update": false` oder `--kein-update`.
- Tests: Update-Ablauf mit nachgebautem GitHub (Austausch, Prüfsumme falsch, nichts zu tun), nur die
  erlaubten Adressen im Update-Paket, das Lernprogramm kennt das Update-Paket nicht.
- 05.11.2026: Repository öffentlich (Tobi). Geprüft ohne Anmeldung: Repository-Seite erreichbar, fester
  Download-Link liefert die `.exe`, der echte Ablauf gegen Release `build-22` lädt, prüft die Prüfsumme,
  tauscht und startet (unter Linux mit Platzhalter-Datei).
- 05.11.2026: **Unter Windows von Tobi bestätigt:** Build 22 hat sich beim Start selbst auf Build 23
  aktualisiert und läuft.

## Offene Punkte

- Szenario-Ausgaben sind „ungeprüft“. Bitte beim Spielen auf Abweichungen zum echten Windows achten.
  Besonders unsicher (bewusst so markiert oder gekürzt):
  - `Get-Volume`: Spaltenformat von Windows 10/11; das Beispiel in der Microsoft-Doku ist älter.
  - `ping` ohne Netzwerkadapter („PING: transmit failed. General failure.“).
  - `net user jschulz`: Ausgabe gekürzt (Passwort- und Anmeldezeilen weggelassen).
  - Wo die echte Ausgabe nicht sicher bekannt ist oder ein Fenster aufgehen würde, zeigt die
    Simulation eine blaue `[N3XTBYT3]`-Meldung statt eines erfundenen Textes.
- Grundkurs: Lektionen, Befehlsbuch und Lexikon sind „ungeprüft“. Besonders unsicher:
  - `Get-ChildItem`: Spalten und Datumsformat nach dem Beispiel der Microsoft-Doku (Uhrzeit 24 Stunden,
    z. B. `08:29`). Ein echtes englisches Windows zeigt die Uhrzeit vermutlich als `8:29 AM`.
  - `Get-Command`: Spalten Version/Source nach der Beschreibung in der Doku; Spaltenbreiten wie im Beispiel.
  - `Resolve-DnsName` und `Get-Service … | Select-Object …`: Spaltenformat nicht aus einem Doku-Beispiel.
  - `whatis` (Spaltenbreite) und Ubuntus Meldung „Command 'Whoami' not found, did you mean:“ (gekürzt).
  - Neue Dateien unter Linux: `rw-rw-r--` (Ubuntu-Standard für normale Benutzer, umask 002).
  - `Get-Help`, `man`, `systeminfo`, Prozess- und Dienstlisten sind gekürzt (blaue Notiz darunter).

## Entscheidungen

- 04.11.2026 (Tobi): Eigenes Programm, nicht Teil von Shellbreaker; Aussehen angelehnt.
- 04.11.2026 (Tobi): Nachgebautes Terminal, reine Simulation, ändert nichts am echten System.
- 04.11.2026 (Tobi): Reihenfolge Windows → Windows Server → Linux und Linux Server; alle vier Pflicht.
- 04.11.2026 (Tobi): Claude Code arbeitet selbstständig ohne große Unterbrechungen, direkt auf `main`.
- 04.11.2026: Szenarien sind Datendateien; selbst geschriebene gelten als „ungeprüft“, nur Tobi bestätigt.
- 04.11.2026: **Systemausgaben auf Englisch**, so wie in den Beispielen der Microsoft-Doku und der
  man-Pages. Grund: nur so lassen sie sich gegen die offizielle Doku prüfen. Erklärungen,
  Hinweise und Meldungen der Simulation sind deutsch.
- 04.11.2026: **Eigene Szenarien auch im Datenordner** (`%APPDATA%\N3XTBYT3\szenarien\<system>\`).
  Grund: Tobi kann echte Fehler als Szenario ergänzen, ohne dass eine neue `.exe` gebaut werden muss.
- 04.11.2026: **Befehlsvergleich:** Optionen samt Wert dürfen in beliebiger Reihenfolge kommen;
  andere Schreibweisen stehen als weitere Muster im Szenario. Grund: einfach und vorhersagbar,
  ohne für jeden Befehl die echte Parameterlogik nachzubauen.
- 04.11.2026: **Windows hat zwei Shells** (PowerShell und cmd), Wechsel mit `powershell`, `cmd`,
  `exit`. Befehle der Form Verb-Nomen gehen nur in der PowerShell. Grund: Den Unterschied
  muss man im Alltag kennen (z. B. `sc` ist in der PowerShell ein Alias für Set-Content).
- 04.11.2026: `help` zeigt die Hilfe der Simulation (Tasten und Grundbefehle), nicht die echte
  Hilfe und keine Lösungsbefehle. Alle Meldungen der Simulation beginnen mit `[N3XTBYT3]`.
- 04.11.2026: Erfundene interne Namen enden auf `.internal` (für private Netze reserviert).
- 04.11.2026: Schriften DejaVu Sans und DejaVu Sans Mono liegen bei (freie Lizenz, Text in
  `n3xtbyt3/oberflaeche/schriften/`). Grund: gleiches Aussehen auf jedem PC, Umlaute sicher.
- 04.11.2026: Ein Versuch ohne einen einzigen Befehl und ohne Hinweis wird nicht gespeichert
  (nur reingeschaut). Nach dem Lösen wird sofort gespeichert.
- 04.11.2026: Auswahlgewichte (M1): neu 5, ungelöst 6, gelöst 1 + Hinweisstufen + 0,5 je falschem
  Befehl. Das gerade gespielte Szenario kommt nicht direkt wieder. M2 ersetzt das durch die Lernkartei.
- 04.11.2026: Neues Feld `"sim": true` in einem Fall: Die Ausgabe ist eine Meldung der Simulation
  statt eines Systemtextes. Grund: Regel „lieber kürzen als erfinden“ – z. B. bei Rückfragen (Ja/Nein),
  Fenstern (cleanmgr) oder Ausgaben, die ich nicht sicher kenne.
- 04.11.2026: Neustart/Herunterfahren (`Restart-Computer`, `shutdown /r` …) ist in allen Windows-Szenarien
  ein „falscher Befehl“ mit Erklärung. Grund: Tobi soll die Ursache finden statt neu zu starten.
- 04.11.2026: Netzlaufwerk-Szenario läuft bewusst ohne Adminrechte: Laufwerke aus einer
  Administrator-Konsole sieht der Benutzer im Explorer nicht (Microsoft-Doku zu New-PSDrive).
- 04.11.2026: Lernkartei-Regeln: ohne Hinweis und mit höchstens 2 falschen Befehlen gelöst → Fach +1;
  mit 1 Hinweis → Fach bleibt; mit 2–3 Hinweisen → Fach −1; nicht gelöst → Fach 1.
  Grund: Wer Hilfe brauchte, soll es bald wieder üben, aber nicht ganz von vorn anfangen.
- 04.11.2026: Befehls-Training bewertet „halb“, wenn der Befehlsname stimmt, aber die Parameter
  abweichen (Fach bleibt). Grund: Den Befehl zu kennen ist schon viel wert; die Musterlösung wird gezeigt.
- 04.11.2026: Auswertung als `auswertung_<system>.json/.md` im Datenordner (statt eines Unterordners),
  passend zu `spielstand_<system>.json`. Neu geschrieben nach jedem Versuch und nach dem Training.
- 04.11.2026: Windows-Server-Szenarien spielen in einer erfundenen Domäne `firma.internal` (NetBIOS FIRMA)
  mit DC01 (192.168.10.5), SRV-DATEI01, SRV-APP01, SRV-TS01. Anmeldenamen wie kwagner@firma.internal
  sind erfunden; der Inhaltstest lässt `.internal`-Adressen zu.
- 04.11.2026: Linux-Szenarien bilden Ubuntu 24.04 LTS nach (Desktop: Benutzer anna auf pc-lager02;
  Server: Benutzer admin auf srv-web01). Grund: verbreitet, gut dokumentiert, nutzt apt, systemd, ufw, Netplan.
- 04.11.2026: Dateien liegen als flache Zustandsschlüssel vor (`datei:/pfad`, `rechte:/pfad`, `besitzer:/pfad`).
  Grund: Bedingungen und Änderungen funktionieren damit genauso wie bei allen anderen Werten.
- 04.11.2026: `sudo` fragt nicht wirklich nach einem Passwort; die Zeile „[sudo] password for …“ erscheint einmal
  pro Szenario mit Hinweis. Bei `sudo befehl ~/x` gilt wie im echten System das Home des Benutzers.
- 04.11.2026: Der Editor ist ein eigener, einfacher nano-Ersatz mit deutschen Meldungen (kein Nachbau von nano).
  Die nano-Tasten Strg+O, Strg+X, Strg+K funktionieren wie im Original.
- 04.11.2026: Lösungswege dürfen unter Linux Speicherschritte enthalten (`{"speichern": pfad, "inhalt": …}`),
  damit der automatische Test auch Szenarien mit Editor durchspielen kann.
- 04.11.2026: Erklärungen als Liste von Zeilen werden zu Fließtext verbunden (leere Zeile = neuer Absatz).
- 04.11.2026: Der MCP-Server ist ohne das offizielle MCP-Python-Paket gebaut (eigenes, kleines JSON-RPC über
  stdin/stdout). Grund: keine zusätzliche Abhängigkeit, leicht zu prüfen, keine Netzwerkbibliotheken.
  Er liegt als eigenes Paket `n3xtbyt3_mcp` neben `n3xtbyt3`; der Sicherheitstest prüft beide.
- 04.11.2026: Szenario-Entwürfe über MCP landen direkt im Datenordner (`szenarien/<system>/`), damit Tobi sie
  sofort sieht – immer „ungeprüft“, nur nach erfolgreicher Prüfung, nie überschreibend.
- 04.11.2026: Tickets sind normale Szenarien mit Feld `ticket` (im Ordner ihres Startsystems). Grund: kein
  zweites Format; dieselben Tests, Lernkartei und Auswertung gelten auch für Tickets.
- 04.11.2026: Bei Tickets wird der Versuch erst beim Schließen (oder Verlassen) gespeichert, damit die
  Lösungsnotiz dabei ist.
- 04.11.2026: Zweig: Die Sitzung gibt den Arbeitszweig `claude/busy-turing-1n3hmy` vor. Ich pushe
  dorthin **und** nach `main` (laut `CLAUDE.md`), beide Stände bleiben gleich.
- 05.11.2026: **Grundkurs auf derselben Befehlsauswertung:** Aus jeder Lektion wird intern ein Szenario
  gebaut und in einer normalen Sitzung gespielt. Die geführten Lektionen nutzen vorhandene Szenarien als
  Grundlage (Feld `szenario`). Grund: geprüfte Ausgaben wiederverwenden, kein zweites System.
- 05.11.2026: Lektions-ids haben die Vorsilbe `gk-win-`, `gk-srv-`, `gk-lin-`, `gk-ls-` und sind über alle
  Kurse eindeutig; `voraussetzung` darf auf eine Lektion eines anderen Systems zeigen (Server-Kurse bauen
  auf Windows bzw. Linux auf).
- 05.11.2026: **Windows-Dateibefehle nur in der PowerShell** und nur, wenn ein Szenario oder eine Lektion
  Windows-Dateien hat. Die cmd-Varianten (dir, type, copy …) sind nicht nachgebaut und melden das klar.
  Grund: Die Idee sagt „keine neuen Systemfunktionen über das hinaus, was die Lektionen brauchen“, und der
  Grundkurs lehrt PowerShell zuerst.
- 05.11.2026: Ausgabe von `Get-ChildItem` nach dem Beispiel der Microsoft-Doku (Seite für PowerShell 5.1).
  Die beiden Szenarien mit eigener Get-ChildItem-Tabelle (Druckwarteschlange, Festplatte voll) habe ich
  angeglichen, damit es überall gleich aussieht.
- 05.11.2026: Fehlermeldungen der PowerShell-Dateibefehle zeigen nur die erste Zeile (mit dem getippten
  Befehlsnamen vorn, wie Windows PowerShell). Rückfragen (Ordner nicht leer ohne -Recurse) und unbekannte
  Parameter beantwortet die Simulation blau – nie mit einer erfundenen Fehlermeldung.
- 05.11.2026: Neues Feld `notiz` in einem Fall: echte Ausgabe plus blaue Meldung danach (z. B. „Gekürzt …“).
  Grund: Regel „lieber kürzen als erfinden“, und Tobi soll sehen, dass gekürzt wurde.
- 05.11.2026: Ein Mitmachen-Schritt zählt nur, wenn der Befehl wirklich lief (nicht in der falschen Shell).
  Eine Ziel-Bedingung lässt andere Schreibweisen zu (z. B. `cd .\documents`).
- 05.11.2026: Das Willkommensbild erscheint, solange es noch keinen Spielstand gibt (keine
  `spielstand_*.json`) – also bis zum ersten getippten Befehl in einer Lektion oder einem Szenario.
- 05.11.2026: F2 springt auch ohne Abschluss zur nächsten Lektion („Überspringen“). Grund: Die Idee will
  Hinweise statt Sperren.
- 05.11.2026: Das Befehlsbuch zeigt immer alle Befehle; noch nicht gelernte stehen als „Kommt in Lektion n“
  da. Ins Befehls-Training kommen sie erst, wenn die Lektion geschafft ist (Aliase zählen als richtig).
  Grund: Nachschlagen soll immer gehen, das Training nur Gelerntes abfragen.
- 05.11.2026: Befehlsbuch und Lexikon sind Einblendungen über der aktuellen Ansicht (Esc, F4 bzw. F5 schließt),
  kein Ansichtswechsel. Grund: Ein laufendes Szenario wird dadurch nicht beendet oder gespeichert.
- 05.11.2026: Das Lexikon zeigt die Begriffe des aktuellen Systems (Lektionen zuerst, dann Szenarien);
  gleiche Begriffe werden zusammengefasst.
- 05.11.2026: In den Lektionen gelten dieselben erfundenen Namen wie in den Szenarien (mberger, anna, admin;
  PC-BUERO-07, pc-lager02, srv-web01) und nur private IP-Adressen (z. B. `ping 192.168.10.1` statt einer
  öffentlichen Adresse). Grund: Regel 4.
- 05.11.2026: Tab-Ergänzung wird in Windows-Lektion 2 nur erklärt, nicht nachgebaut (die Idee sagt „erklären“).
- 05.11.2026: Neue Dateien unter Linux (mkdir, touch, cp) bekommen die Ubuntu-Standardrechte: normale
  Benutzer `rw-rw-r--`/`rwxrwxr-x` (umask 002), root `rw-r--r--`/`rwxr-xr-x`.
- 05.11.2026 (Tobi): **Selbst-Update** der `.exe` als einzige Ausnahme von Regel 1; Repository wird dafür
  öffentlich (macht Tobi). Umgesetzt als eigenes Paket `n3xtbyt3_update` in derselben `.exe` statt eines
  zweiten Startprogramms. Grund: Tobi behält eine einzige Datei; die Trennung vom Lernprogramm sichern
  eigene Pakete und Tests.
- 05.11.2026: Version = Laufnummer von GitHub Actions (Release `build-<n>`), Vergleich als Zahl. Die frisch
  gestartete neue Version prüft nicht gleich noch einmal (kein Endlos-Neustart). Ein Update lädt ohne
  Rückfrage (Wunsch: „sollte sich selbst aktualisieren“); Esc im Fortschrittsfenster bricht ab.
- 06.11.2026: Beim Selbst-Probieren kommt bei einem falschen Befehl eine allgemeine Rückmeldung, aber nie die
  Lösung. Grund: Tobi soll merken, dass die Aufgabe noch offen ist, die Hinweise holt er sich selbst mit F1.

## Für Tobi zum Testen

**Neu: Grundkurs**

1. Neueste `.exe` holen (wie unten). Das Willkommensbild kommt nur, solange es noch keinen Spielstand gibt.
   Hast du schon gespielt, startest du den Grundkurs über Windows → erster Eintrag „Grundkurs“.
   (Nur wenn du das Willkommensbild sehen willst: Ordner `%APPDATA%\N3XTBYT3` vorher umbenennen, z. B. in
   `N3XTBYT3-alt`. Was du dann spielst, landet im neuen Ordner.)
2. Im Willkommensbild Enter (bzw. „Grundkurs“): Windows-Lektion 1 startet. Arbeite die Lektionen 1–10 der
   Reihe nach durch.
   Wichtigste Frage: Kommst du durch, ohne woanders nachzusehen? Wo hast du gestockt?
3. Absichtlich vertippen (z. B. `hostnme`): Ist der Hinweis rechts hilfreich?
4. F4 (Befehlsbuch) und F5 (Lexikon) an verschiedenen Stellen drücken, etwas suchen, Tab im Befehlsbuch.
5. In der Szenarioliste: Steht der Grundkurs oben, und zeigen Szenarien „braucht: Lektion n“?
6. Wenn Zeit ist: je eine Lektion in Windows Server, Linux und Linux Server.

**Bisherige Tests (M1–M4)**

1. `.exe` holen: GitHub → Actions → neuester grüner Lauf → unten „N3XTBYT3-Windows“ → entpacken.
   Windows warnt beim ersten Start (nicht signiert): „Weitere Informationen“ → „Trotzdem ausführen“.
2. Windows wählen, „Zufälliges Szenario“, mindestens drei Szenarien lösen. Dabei auch mal F1 drücken.
3. Programm schließen, wieder öffnen: In der Liste müssen die gelösten Szenarien grün sein.
4. Schrift mit Strg + / Strg − anpassen, F11 für Vollbild. Ist alles gut lesbar?
5. Windows Server: ein paar Szenarien spielen, eines mit Esc abbrechen. Dann „Auswertung ansehen“:
   Steht das abgebrochene Szenario bei den Schwächen und in der Empfehlung? Kommt es bei
   „Zufälliges Szenario“ öfter dran?
6. Linux und Linux Server: z. B. „Webserver startet nicht nach Änderung“ – Fehler mit `sudo nginx -t`
   finden, mit `sudo nano …` beheben (Strg+O, Strg+X), `sudo systemctl restart nginx`. Ist der Editor
   gut bedienbar? Stimmen die Ausgaben mit deinem Ubuntu überein?
7. Tickets: Kachel 5 im Hauptmenü, „Webshop zeigt 502 Bad Gateway“ spielen (vom PC per
   `ssh admin@srv-web01` auf den Server, zurück mit `exit`), am Ende F3 und eine kurze Notiz.
8. Claude Desktop: MCP-Server nach `docs/mcp.md` einrichten und nach deiner Auswertung fragen.
9. Befehls-Training ausprobieren: Sind die Fragen verständlich? Ist die Bewertung fair?
10. Auf Abweichungen zum echten System achten (Ausgaben, Fehlermeldungen) und mir sagen,
   welches Szenario. Wenn alles stimmt: in der Datei `"pruefstatus": "bestaetigt"` setzen.
