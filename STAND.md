# STAND — N3XTBYT3

Stand: 04.11.2026.

## Aktuell

**M1 und M2 sind fertig** (bis auf deine Abnahmetests, siehe unten).

**Nächster Schritt:** M3 — Linux und Linux Server (simuliertes Dateisystem, Editor, Szenarien).

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

### Abnahme M2 (PLAN.md)

- [x] Windows Server spielbar (16 Szenarien, alle mit Lösungsweg getestet)
- [x] Auswertung zeigt nach mehreren Durchläufen plausible Schwächen (automatischer Test)
- [x] Falsch gelöste Szenarien kommen sichtbar öfter wieder (Lernkartei, automatischer Test)
- [ ] **Tobi:** einige Windows-Server-Szenarien spielen, eines absichtlich nicht lösen,
      danach Auswertung ansehen und prüfen, ob die Empfehlung passt

## Offene Punkte

- Szenario-Ausgaben sind „ungeprüft“. Bitte beim Spielen auf Abweichungen zum echten Windows achten.
  Besonders unsicher (bewusst so markiert oder gekürzt):
  - `Get-Volume`: Spaltenformat von Windows 10/11; das Beispiel in der Microsoft-Doku ist älter.
  - `ping` ohne Netzwerkadapter („PING: transmit failed. General failure.“).
  - `net user jschulz`: Ausgabe gekürzt (Passwort- und Anmeldezeilen weggelassen).
  - Wo die echte Ausgabe nicht sicher bekannt ist oder ein Fenster aufgehen würde, zeigt die
    Simulation eine blaue `[N3XTBYT3]`-Meldung statt eines erfundenen Textes.

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
- 04.11.2026: Zweig: Die Sitzung gibt den Arbeitszweig `claude/busy-turing-1n3hmy` vor. Ich pushe
  dorthin **und** nach `main` (laut `CLAUDE.md`), beide Stände bleiben gleich.

## Für Tobi zum Testen

1. `.exe` holen: GitHub → Actions → neuester grüner Lauf → unten „N3XTBYT3-Windows“ → entpacken.
   Windows warnt beim ersten Start (nicht signiert): „Weitere Informationen“ → „Trotzdem ausführen“.
2. Windows wählen, „Zufälliges Szenario“, mindestens drei Szenarien lösen. Dabei auch mal F1 drücken.
3. Programm schließen, wieder öffnen: In der Liste müssen die gelösten Szenarien grün sein.
4. Schrift mit Strg + / Strg − anpassen, F11 für Vollbild. Ist alles gut lesbar?
5. Windows Server: ein paar Szenarien spielen, eines mit Esc abbrechen. Dann „Auswertung ansehen“:
   Steht das abgebrochene Szenario bei den Schwächen und in der Empfehlung? Kommt es bei
   „Zufälliges Szenario“ öfter dran?
6. Befehls-Training ausprobieren: Sind die Fragen verständlich? Ist die Bewertung fair?
7. Auf Abweichungen zum echten Windows achten (Ausgaben, Fehlermeldungen) und mir sagen,
   welches Szenario. Wenn alles stimmt: in der Datei `"pruefstatus": "bestaetigt"` setzen.
