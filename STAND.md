# STAND — N3XTBYT3

Stand: 04.11.2026.

## Aktuell

M1 läuft. M1.1 (Kern ohne Oberfläche) ist fertig.

**Nächster Schritt:** M1.2 — Oberfläche (siehe `PLAN.md`).

## Fertig

- Projektrahmen: `CLAUDE.md`, `PLAN.md`, `STAND.md`, `SITZUNGEN.md`, `IDEEN.md`, `README.md`.
- M1.1 Kern: Szenario-Format (`daten/szenarien/SCHEMA.md`), Lader mit Prüfung,
  Befehlsauswertung, simulierter Zustand, allgemeine Windows-Befehle
  (`daten/allgemein/windows.json`), erstes Szenario `win-dns-cache`, Tests.

## Offene Punkte

- keine

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
- 04.11.2026: Zweig: Die Sitzung gibt den Arbeitszweig `claude/busy-turing-1n3hmy` vor. Ich pushe
  dorthin **und** nach `main` (laut `CLAUDE.md`), beide Stände bleiben gleich.

## Für Tobi zum Testen

- noch nichts (erst ab M1.2 gibt es etwas zu sehen)
