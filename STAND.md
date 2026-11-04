# STAND — N3XTBYT3

Stand: 04.11.2026.

## Aktuell

M1 läuft. M1.1 bis M1.4 sind fertig.

**Nächster Schritt:** M1.5 — Tests unter Windows, `.exe` per GitHub Actions, README.

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
- 04.11.2026: Zweig: Die Sitzung gibt den Arbeitszweig `claude/busy-turing-1n3hmy` vor. Ich pushe
  dorthin **und** nach `main` (laut `CLAUDE.md`), beide Stände bleiben gleich.

## Für Tobi zum Testen

- noch nichts (erst ab M1.2 gibt es etwas zu sehen)
