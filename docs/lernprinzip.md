# Lernprinzip — N3XTBYT3

Wortgleich aus `CLAUDE.md` (Abschnitt „Lernprinzip“) und aus den erledigten Einträgen „Grundkurs“ und
„Lernprinzip“ in `IDEEN.md` hierher verschoben (21.11.2026). Gilt für Grundkurs, Szenarien und jeden
neuen Bereich. Der übrige Text der erledigten Einträge steht im Git-Verlauf (`git show 6781491:IDEEN.md`).

## Ziel

Ziel ist eine funktionierende Lernsoftware, die **erklärt, erläutert, das Wissen abfragt und
erprobt** (Tobi, 20.11.2026). Daraus folgt für Grundkurs, Szenarien und jeden neuen Bereich:

1. **Erklären** – jeder Befehl und jeder Zusatz wird erklärt (was, wozu, wie liest man die Ausgabe),
   bevor eine Aufgabe ihn verlangt. Hinweise (F1) ersetzen keine Erklärung.
2. **Erläutern/Vorführen** – im Mitmachen an einem Beispiel gezeigt; die Erklärung danach sagt,
   warum es so funktioniert.
3. **Abfragen** – die Aufgabe überträgt das Gelernte auf ein anderes Beispiel und verlangt nichts Neues
   (Ausnahme: gekennzeichnete Suchaufgabe).
4. **Erproben** – Szenarien wenden es in echten Fehlersituationen an; ihre Erklärung geht die Lösung
   Schritt für Schritt durch.

`tests/test_didaktik.py` prüft das (Regeln unten). Eine Lektion oder ein Szenario,
das den Test nicht besteht, ist nicht fertig.

## Aus „Lernprinzip“ (IDEEN.md, freigegeben 20.11.2026)

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

### Suchaufgaben (Ausnahme von Regel 3)
Erlaubt ab der Hilfe-Lektion (Lektion 3), höchstens eine pro Lektion, gekennzeichnet mit
`"suchaufgabe": true`. Der Aufgabentext sagt selbst, dass der Befehl neu ist und womit man ihn
findet (`Get-Command`, `Get-Help`, `apropos`, `man`, `--help`). Die Erklärung danach erklärt den
gefundenen Befehl vollständig nach Regel 1 und 2.

### Ausnahmen
Gewollt unbekannte Befehle (Vorführung einer Fehlermeldung, z. B. `Get-Kaffee`) bekommen am Schritt
`"absichtlich_unbekannt": true`; die Prüfung überspringt sie.

## Aus „Grundkurs“ (IDEEN.md, freigegeben 05.11.2026)

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

### Technik
- Lektionen sind **Daten wie Szenarien**: `daten/grundkurs/<system>/<nr>-<id>.json`, Format
  in `daten/grundkurs/SCHEMA.md`, mit `quelle` und `pruefstatus` (selbst geschrieben =
  `ungeprueft`). Die Befehle nutzen dieselbe Befehlsauswertung wie die Szenarien.
- Fortschritt je Lektion im Spielstand des Systems; die Auswertung zeigt den Grundkurs-Stand.
- Befehlsbuch und Lexikon werden aus den Daten erzeugt, nicht von Hand gepflegt.
- Tests: jede Lektion lädt und ist mit den vorgegebenen Eingaben durchspielbar; jeder
  Befehlsbuch-Eintrag funktioniert in der Simulation; jedes Szenario mit `voraussetzung`
  verweist auf eine existierende Lektion.
