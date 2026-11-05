# CLAUDE.md — Regeln für Sitzungen an N3XTBYT3

## Was N3XTBYT3 ist

Ein Lern-Simulator für Systemwartung. Tobi lernt darin über ein **nachgebautes Terminal**,
Fehler an Systemen zu erkennen und zu beheben — Befehle, Fachbegriffe und Vorgehen.
Im Hauptmenü wählt er eines von vier Systemen: **Windows, Windows Server, Linux,
Linux Server**. Die Simulation wählt Szenarien aus, gibt gestufte Hinweise und speichert
den Fortschritt je System.

- **Nutzer:** nur Tobi, reines Lernwerkzeug. Keine Veröffentlichung, kein Shop, keine Konten.
- **Kern:** Probleme und Fehler erkennen, die Lösung lernen und kennen. Tickets und
  andere Abläufe sind nur Abwechslung, nie der Kern.
- **Zweck:** Vorbereitung auf eine IT-Weiterbildung (Netzwerkadministration, Windows
  Server) und bessere Wartungskenntnisse für den Alltag.
- **Szenarien aus der Wirklichkeit:** Echte Fehler, die Tobi löst, kommen laufend als
  neue Szenarien dazu. Das Programm muss das ohne Codeänderung erlauben.

## Unverhandelbar

1. **Reine Simulation.** Das Programm führt nie echte Systembefehle aus: kein
   `subprocess`, kein `os.system`, kein Schreiben außerhalb des eigenen Datenordners,
   kein Netzwerkzugriff. Jede Ausgabe kommt aus den Szenario-Daten. Ein Test prüft das
   (siehe PLAN.md, M1).
   **Einzige Ausnahme (Entscheidung Tobi, 05.11.2026): Selbst-Update der `.exe`.** Das Paket
   `n3xtbyt3_update` darf beim Start der `.exe` bei GitHub nach einem neueren Release *dieses*
   Repositorys fragen, die neue `.exe` samt Prüfsumme laden, sie nach Prüfung gegen die laufende
   Datei tauschen und starten. Sonst nichts – keine anderen Adressen, keine anderen Befehle. Das
   Lernprogramm (`n3xtbyt3`) und der MCP-Server bleiben ohne Netz und ohne Systemaufrufe; Tests
   prüfen beides. Das Repository muss dafür öffentlich sein, die `.exe` enthält keinen Schlüssel.
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

## Arbeitsweise: selbstständig durchlaufen

Tobi will, dass du **ohne Unterbrechungen** arbeitest.

- **Zu Beginn jeder Sitzung liest du als Erstes `IDEEN.md`**, danach `STAND.md` und `PLAN.md`.
  Einträge mit `Status: freigegeben` haben Vorrang vor allem anderen (Regel unten:
  „Ideen aus den Chats“).
- Arbeite `PLAN.md` der Reihe nach ab: Meilenstein für Meilenstein, Schritt für Schritt.
- Musst du etwas entscheiden, das der Plan offenlässt: entscheide selbst, nimm die
  einfachere Lösung, und schreib die Entscheidung mit Begründung in `STAND.md`,
  Abschnitt „Entscheidungen“. Nicht anhalten, nicht nachfragen.
- Anhalten und fragen nur, wenn eine Regel aus „Unverhandelbar“ verletzt würde oder du
  etwas Unumkehrbares tun müsstest (Repository-Einstellungen, Löschen von Tobis
  Szenarien mit `"bestaetigt"`).
- Arbeite in kleinen, lauffähigen Schritten. Nach jedem Schritt: Tests laufen lassen
  (`python -m unittest`), committen, `STAND.md` aktualisieren.
- **Zweig:** Direkt auf `main` committen und pushen, sobald die Tests grün sind
  (Entscheidung Tobi, 04.11.2026). Ist `main` geschützt oder lehnt ab: Arbeitszweig,
  Pull Request, selbst zusammenführen, wenn die Tests grün sind.
- Am Ende eines Meilensteins: Abnahmekriterien aus `PLAN.md` abhaken, in `STAND.md`
  festhalten, was Tobi testen soll (kurze Liste, in einfachen Worten).

## Stand-Dateien (Brücke zu den Chats)

Die Chats auf claude.ai lesen den Stand über GitHub. Deshalb führt das Repository ihn selbst:

| Datei | Art | Inhalt |
|---|---|---|
| `STAND.md` | wird **überarbeitet** | aktueller Meilenstein, was fertig ist, offene Punkte, Entscheidungen, Testliste für Tobi |
| `SITZUNGEN.md` | wird **angehängt** | ein Einzeiler pro Sitzung: Datum — was erledigt wurde |
| `IDEEN.md` | wird überarbeitet | Ideen für das Programm, jede mit Status (siehe unten) |
| `PLAN.md` | wird nur bei Planänderung überarbeitet | Meilensteine und Abnahmekriterien |

Jede Sitzung endet mit aktualisiertem `STAND.md` und einer neuen Zeile in `SITZUNGEN.md`.

### Ideen aus den Chats

Tobi bespricht neue Ideen zuerst im Chat und lässt sie dort ausarbeiten. Die fertige
Fassung landet in `IDEEN.md` mit einem Status:

- `Status: offen` — nur notiert, **nicht bauen**.
- `Status: freigegeben` — ausgearbeitet und von Tobi freigegeben. Bau sie als Nächstes
  (läuft gerade ein Meilenstein-Schritt, erst diesen Schritt abschließen). Trag sie in
  `PLAN.md` ein, hak die Abnahme in `STAND.md` ab und setz sie danach auf
  `Status: erledigt (<Datum>)`. Mehrere freigegebene Ideen: von oben nach unten.
- `IDEEN.md` ist der einzige Weg, auf dem Aufträge aus den Chats zu dir kommen. Was dort
  steht, ist ausgearbeitet; lass dir Lücken nicht bestätigen, sondern entscheide nach den
  Regeln oben und notiere es in `STAND.md`.
- Widerspricht eine freigegebene Idee einer Regel aus „Unverhandelbar“, baust du sie
  nicht und schreibst den Grund in `STAND.md`, Abschnitt „Offene Punkte“.

## Technik

- Python 3.12, Oberfläche mit **Pygame** (`pygame-ce`), Tests mit `unittest`.
- **Kern ohne Pygame:** Szenario-Lader, Zustand, Befehlsauswertung, Spielstand,
  Lernkartei liegen in `n3xtbyt3/kern/` und sind ohne Oberfläche testbar.
  Die Oberfläche (`n3xtbyt3/oberflaeche/`) ruft nur den Kern auf.
- **Szenarien sind Daten:** `daten/szenarien/<system>/<id>.json`, Format in
  `daten/szenarien/SCHEMA.md`. Ein Test lädt und prüft jede Datei.
- **Spielstand:** lesbares JSON. Windows: `%APPDATA%\N3XTBYT3\`, sonst
  `~/.local/share/n3xtbyt3/`. Je System eine Datei.
- **Windows-Programmdatei:** GitHub Actions baut bei jedem Push nach `main` eine `.exe`
  (PyInstaller), testet unter Windows und veröffentlicht sie als Release `build-<Laufnummer>`.
  Aus dem neuesten Release aktualisiert sich die `.exe` beim Start selbst (Ausnahme zu Regel 1).

## Aussehen

Angelehnt an Tobis Spiel Shellbreaker: dunkler Hintergrund, Terminalschrift in Grün,
Neon-/Matrix-Stil. Aufteilung: links das Terminal, rechts ein Bereich für Hinweise,
Erklärungen und Begriffe. Gut lesbar bei 1920 × 1080, Schriftgröße einstellbar.

## Sprache

Alle Texte für Tobi auf Deutsch, einfach und ohne unnötige Fachsprache. Fachbegriffe
werden beim ersten Auftreten kurz erklärt. Befehle bleiben im Original.
Commit-Nachrichten auf Deutsch.
