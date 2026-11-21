# CLAUDE.md — Regeln für Sitzungen an N3XTBYT3

## Was N3XTBYT3 ist (Kurzfassung)
Tobis Lernplattform für IT-Themen; erster Baustein ist der Wartungs-Simulator (nachgebautes Terminal,
vier Systeme). Nur für Tobi, reines Lernwerkzeug. Ausführlich – Zweck, Kern, Szenarien aus der
Wirklichkeit, Aussehen – in `docs/projekt.md`. Lies sie vor neuen Bereichen oder Änderungen am Aussehen.

## Arbeitsweise (Standard KhaosDE, Fassung 21.11.2026 – in allen Repositorys gleich)

Dateien:
- `IDEEN.md` – die Aufträge. Nur offene Ideen: je Idee eine Überschrift `## …` und genau eine
  Zeile `Status: in Klärung` oder `Status: bereit`. Erledigtes und Verworfenes wird gelöscht.
- `STAND.md` – nur der aktuelle Zustand: was läuft, offene Punkte, nächste Schritte (höchstens
  150 Zeilen). Wird überschrieben, Veraltetes gelöscht.
- `SITZUNGEN.md` – je erledigter Aufgabe eine Zeile `- TT.MM.JJJJ — was erledigt`, nur
  anhängen, neueste unten. Die einzige Chronik; Gelöschtes bleibt im Git-Verlauf.
- `docs/` – dauerhaftes Wissen, geltende Entscheidungen in `docs/entscheidungen.md`. Nur gezielt lesen.

Ablauf:
1. Sitzungsbeginn: `STAND.md` und `IDEEN.md` lesen.
2. Umgesetzt wird nur eine Idee mit `Status: bereit` – eine pro Sitzung. Geplant wird im Chat,
   die Idee ist der Plan. Lässt sie eine Kleinigkeit offen: die einfachere Lösung nehmen und mit
   Grund in `docs/entscheidungen.md` festhalten. Ist der Kern unklar oder passt die Idee nicht
   zum Code: anhalten und fragen, nicht raten.
3. Fertig erst, wenn die Prüfung (Abschnitt „Prüfen“) grün ist; letzte Zeile der Ausgabe im
   Bericht zeigen. Nicht Prüfbares ausdrücklich „ungeprüft“ nennen. Tests nie abschwächen.
4. Vor dem Übernehmen nach `main`: ein Prüf-Subagent in frischem Kontext prüft den Diff gegen
   die Idee (nur Fehler zu Richtigkeit oder Auftrag, keine Stilwünsche).
5. Im selben Commit wie die Arbeit: Idee aus `IDEEN.md` löschen, `STAND.md` überschreiben,
   Zeile in `SITZUNGEN.md` anhängen.
6. Einfälle nebenbei: als neue Idee mit `Status: in Klärung` in `IDEEN.md`, nicht umsetzen.
   `bereit` setzt nur Tobi (auch über den Chat).
7. Keine Passwörter, Tokens, Zugangsdaten oder echten Personennamen im Repository.

`.claude/hooks/notizen_pruefen.py` prüft am Ende jeder Antwort Punkt 5, die Länge von `STAND.md`
und die Status in `IDEEN.md`; meldet es etwas, beheben. Diesen Abschnitt und das Skript nicht
einzeln ändern – sie sind in allen Repositorys gleich.

## Prüfen – Pflicht, bevor du „fertig“ sagst

- Alle Tests: `python -m unittest` (Windows und Linux, Python 3.12, `pip install -r requirements.txt`).
  In der Cloud-Sitzung: `python3.12 -m pip install --break-system-packages -r requirements.txt`, dann
  `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3.12 -m unittest` (Stand 21.11.2026:
  „Ran 236 tests … OK“, etwa 10 Sekunden).
- Fertig ist eine Aufgabe erst, wenn die Prüfung grün ist. Zeige die letzte Zeile der Ausgabe im Bericht.
  In der Cloud nicht prüfbar, deshalb ausdrücklich „ungeprüft“ nennen: Aussehen und Bedienung am echten
  Bildschirm, die `.exe` und ihr Selbst-Update unter Windows, der MCP-Server in Claude Desktop, und ob
  Ausgaben zum echten System passen (das bestätigt nur Tobi, Regel 2).
- Ursachen beheben, keine Tests abschwächen oder überspringen, damit sie grün werden.

## Projektregeln

### Unverhandelbar
1. **Reine Simulation.** Das Programm führt nie echte Systembefehle aus: kein
   `subprocess`, kein `os.system`, kein Schreiben außerhalb des eigenen Datenordners,
   kein Netzwerkzugriff. Jede Ausgabe kommt aus den Szenario-Daten. Ein Test prüft das
   (siehe PLAN.md, M1).
   **Einzige Ausnahme (Entscheidung Tobi, 05.11.2026): Selbst-Update der `.exe`** durch das Paket
   `n3xtbyt3_update` – sonst nichts; genaue Grenzen in `docs/technik.md`, „Selbst-Update“ (vorher lesen).
2. **Nichts Falsches lehren.** Jede Befehlsausgabe und jede Lösung muss zur offiziellen
   Dokumentation passen (Microsoft Learn, man-Pages, Doku der Distribution).
   Szenarien, die du selbst schreibst, bekommen `"pruefstatus": "ungeprueft"` und eine
   `quelle` (URL). Nur Tobi setzt `"bestaetigt"`. Die Oberfläche zeigt den Status an.
   Weißt du eine Ausgabe nicht sicher, kürze sie lieber, statt sie zu erfinden.
3. **Unbekannte Befehle** beantwortet die Simulation mit einer klaren Meldung
   („In dieser Simulation nicht vorhanden“) plus Hinweis — nie mit einer erfundenen
   Fehlermeldung, die wie eine echte aussieht.
4. **Keine Geheimnisse, keine personenbezogenen Daten** im Repository — auch nicht in
   Beispielszenarien (Namen, IPs, Firmen sind erfunden; IPs aus 192.168.x.x/10.x.x.x).
5. **Nur Betrieb, Wartung, Diagnose und Abwehr.** N3XTBYT3 lehrt, Systeme zu betreiben, zu
   warten, abzusichern und Angriffe zu erkennen. Es lehrt **nicht**, anzugreifen: keine
   Anleitungen zu Exploits, Schadsoftware, dem Einschleusen von Code in fremde Prozesse oder
   dem Umgehen von Schutzmaßnahmen — auch nicht als „Simulation“, Spiel oder Übungsmodul. Im
   Zweifel die Abwehr-Seite bauen (Lücke erkennen und schließen), nie die Angriffs-Seite. Das
   gilt auch für neue IT-Bereiche der Lernplattform. Entscheidung Tobi, 12.11.2026.

### Selbstständig durchlaufen – Tobi will, dass du **ohne Unterbrechungen** arbeitest
- Lässt eine Idee etwas offen: entscheide selbst (Ablauf Punkt 2). Anhalten und fragen nur, wenn eine
  Regel aus „Unverhandelbar“ verletzt würde, du etwas Unumkehrbares tun müsstest (Repository-Einstellungen,
  Löschen von Tobis Szenarien mit `"bestaetigt"`) oder der Kern einer Idee unklar ist.
- Widerspricht eine Idee mit `Status: bereit` einer Regel aus „Unverhandelbar“, baust du sie nicht und
  schreibst den Grund in `STAND.md`, Abschnitt „Offene Punkte“.
- **Zweig:** Direkt auf `main` committen und pushen, sobald die Tests grün sind
  (Entscheidung Tobi, 04.11.2026). Ist `main` geschützt oder lehnt ab: Arbeitszweig,
  Pull Request, selbst zusammenführen, wenn die Tests grün sind. Vorher prüft der Prüf-Subagent
  (Ablauf Punkt 4). Jeder Push nach `main` veröffentlicht ein Release, aus dem sich Tobis `.exe`
  beim Start selbst aktualisiert.
- `PLAN.md`: Meilensteine und Abnahmekriterien, wird nur bei Planänderung überarbeitet. Am Ende eines
  Meilensteins: Abnahmekriterien abhaken, in `STAND.md` festhalten, was Tobi testen soll.
- Grundkurs, Szenarien und jeder neue Bereich **erklären, erläutern, fragen ab und erproben**
  (`docs/lernprinzip.md`, vor jeder Lektion oder jedem Szenario lesen). `tests/test_didaktik.py`
  prüft das; eine Lektion oder ein Szenario, das den Test nicht besteht, ist nicht fertig.
- Alle Texte für Tobi auf Deutsch, einfach und ohne unnötige Fachsprache. Fachbegriffe
  werden beim ersten Auftreten kurz erklärt. Befehle bleiben im Original.
  Commit-Nachrichten auf Deutsch.

## Wo was steht

`docs/projekt.md` (Zweck, Kern, Aussehen) · `docs/technik.md` (Technik, Selbst-Update, Release) ·
`docs/lernprinzip.md` · `docs/mcp.md` · `docs/eigenes_szenario.md` · `docs/entscheidungen.md`.
