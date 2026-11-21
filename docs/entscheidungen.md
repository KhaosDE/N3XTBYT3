# Entscheidungen

Geltende Entscheidungen, auch verworfene Ideen mit Grund. Wird überarbeitet, nicht angehängt.

## Entscheidungen bis 20.11.2026

Wortgleich aus `docs/verlauf.md` (dorthin aus `STAND.md`, Abschnitt „Entscheidungen“, verschoben); sie gelten weiter.

- 20.11.2026: Windows-Lektion 6 übt an drei hängenden Editor-Fenstern statt an einem; die Reihenfolge ist
  „/IM höflich → /PID /F → Stop-Process -Id → /IM /F“. Grund: Mit nur einem Fenster wäre es nach dem ersten
  erzwungenen Beenden weg, und /PID und Stop-Process hätten nichts mehr zum Üben.
- 20.11.2026: Die Grundkurse wurden von vier Helfern parallel überarbeitet (je ein Kurs), die Szenarien von einem
  fünften; ich habe die Ergebnisse gelesen, Stichproben gegen die Doku geprüft und fachliche Fehler korrigiert.
- 20.11.2026: Keine Suchaufgaben eingebaut – alles wird vorher erklärt (Vorgabe: lieber erklären als suchen lassen).

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
- 06.11.2026: Lektionen schreiben ein Protokoll (`grundkurs_protokoll.txt`, die letzten 400 Eingaben) in den
  Datenordner. Grund: Fehler, die Tobi meldet, lassen sich sonst nicht nachvollziehen. Nur im Datenordner (Regel 1).

- 07.11.2026: Tippfehler gelten nur bis zu einem Abstand von 1 (bis 5 Zeichen) bzw. 2 (länger); höchstens zwei
  Wörter dürfen abweichen. Grund: Vorgabe der Idee; mehr Abweichung ist eher ein anderer Befehl als ein Tippfehler.
- 07.11.2026: Aliase werden erst geprüft, wenn die Eingabe genau so nicht passt; die Hilfe der Simulation
  (`help`) ist davon ausgenommen. Grund: `help` soll weiter die Hilfe der Simulation zeigen, `Get-Help` nicht.
- 07.11.2026: `chown` kennt nur Konten, die im Szenario vorkommen oder auf Ubuntu Standard sind. Grund: ein echter
  Rechner hat eine feste Benutzerliste; ein Tippfehler im Namen soll wie dort `invalid user/group` melden.
- 07.11.2026: Klassische Programme (`taskkill`, `net`, `netsh` …) gelten in beiden Shells, auch wenn im selben
  Eintrag ein Cmdlet steht; PowerShell-Kurznamen daneben (`tnc`, `gci`, `help` …) nur in der PowerShell. Grund:
  so ist es in Windows, und Tobi sollte nicht lernen, dass `taskkill` in der cmd fehlt.
- 07.11.2026: Bash-Platzhalter (`*`, `?`, `~`) werden nur bei den eingebauten Dateibefehlen aufgelöst, nicht in
  Mustern der Szenarien. Wörter in Anführungszeichen bleiben stehen. Grund: Szenario-Muster sollen so bleiben,
  wie sie geschrieben sind.
- 07.11.2026: Home-Ordner unter Linux sind ohne Angabe 750 (`drwxr-x---`), `/root` 700. Grund: Standard von
  Ubuntu ab 21.04 (HOME_MODE 0750). Szenarien können das mit `rechte` überschreiben.
- 07.11.2026: Nicht nachgebaute Optionen (z. B. `ls -t`, `ls -R`, seltene grep-Optionen) bekommen eine blaue
  `[N3XTBYT3]`-Meldung statt einer erfundenen Fehlermeldung (Regel 3).
- 07.11.2026: `rm` auf eine schreibgeschützte Datei: Die echte Rückfrage wird gezeigt, die Simulation antwortet
  mit „y“ (blaue Meldung). `rm` des Ordners, in dem man steht, setzt den Prompt eine Ebene höher (die echte Bash
  bliebe im gelöschten Ordner) – bewusst vereinfacht.
- 07.11.2026: F2 und die Knöpfe „Nächstes“/„Liste“ wirken nicht, solange der Editor offen ist; der Editor
  zeigt „Erst den Editor schließen: Strg+X“. Grund: sonst gingen ungespeicherte Änderungen still verloren.
- 07.11.2026: Befehle nach dem Lösen zählen bei Tickets weiter (bis F3), auch falsche. Grund: Nachprüfen gehört
  zum Ticket; die normalen Szenarien speichern ohnehin sofort beim Lösen.
- 07.11.2026: Zu lange Knopftexte werden bis 70 % verkleinert, sonst mit „…“ gekürzt; Tastenleisten brechen an
  den „·“ um; Titel in Listen werden vor den Etiketten gekürzt.
