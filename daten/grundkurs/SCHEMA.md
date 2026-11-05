# Format einer Grundkurs-Lektion

Eine Lektion ist eine JSON-Datei in `daten/grundkurs/<system>/<nr>-<id>.json`, z. B.
`daten/grundkurs/windows/01-gk-win-konsole.json`. Die Nummer (zweistellig) legt die Reihenfolge fest,
die `id` muss zum Dateinamen passen und in allen Kursen eindeutig sein (Vorsilbe `gk-win-`, `gk-srv-`,
`gk-lin-`, `gk-ls-`).

Eine Lektion läuft auf derselben Befehlsauswertung wie die Szenarien. Ablauf:

1. **Erklären** – ein kurzer Absatz (`erklaeren`), Begriffe gehen ins Lexikon (`begriffe`).
2. **Mitmachen** – rechts steht genau, was zu tippen ist (`mitmachen`). Nach jedem Schritt erscheint
   die Erklärung (`danach`). Bei Tippfehlern gibt es einen freundlichen Hinweis.
3. **Selbst probieren** – Aufgaben ohne vorgegebenen Befehl, mit drei Hinweisstufen (F1).
4. **Das kannst du jetzt** – Zusammenfassung (`fertig`).

## Felder

| Feld | Pflicht | Inhalt |
|---|---|---|
| `id` | ja | z. B. `gk-win-konsole` |
| `system` | ja | `windows`, `windows_server`, `linux`, `linux_server` |
| `titel` | ja | Titel der Lektion |
| `pruefstatus` | ja | `ungeprueft` (von Claude geschrieben) oder `bestaetigt` (nur Tobi) |
| `quelle` | ja | Adresse(n) der offiziellen Doku, auf die sich die Ausgaben stützen |
| `datum` | ja | `JJJJ-MM-TT` |
| `erklaeren` | ja | Ein Absatz (Text oder Liste von Zeilen; leere Zeile = neuer Absatz) |
| `begriffe` | ja | `{"Begriff": "kurze Erklärung"}` – darf `{}` sein |
| `mitmachen` | ja | Liste von Schritten (siehe unten) |
| `aufgaben` | ja | Liste von Aufgaben (siehe unten) |
| `fertig` | ja | Liste „Das kannst du jetzt“ |
| `szenario` | nein | id eines Szenarios desselben Systems. Dessen `zustand`, `dateien`, `befehle`, `rechner` und `shell` sind die Grundlage (für die geführte Fehlersuche). Ziel und Lösung des Szenarios gelten nicht. |
| `zustand`, `dateien`, `befehle`, `rechner`, `shell` | nein | wie bei Szenarien (`daten/szenarien/SCHEMA.md`); ergänzen bzw. überschreiben das Grundszenario. Eigene `befehle` haben Vorrang. |
| `voraussetzung` | nein | id einer Lektion (auch aus einem anderen Kurs), die vorher dran sein sollte – nur ein Hinweis, keine Sperre. |

## Mitmachen

```json
{"text": "Wechsle in den Ordner Documents: Set-Location Documents",
 "eingabe": ["Set-Location Documents", "cd Documents"],
 "ziel": {"pfad": "C:\\Users\\mberger\\Documents"},
 "danach": "Sieh auf den Prompt: Jetzt bist du in Documents."}
```

* `eingabe`: Befehl oder Liste von Befehlen, die den Schritt erfüllen. Der **erste** wird als Vorgabe
  angezeigt. Verglichen wird wie bei Szenarien (Windows ohne Groß-/Kleinschreibung, Optionen in beliebiger
  Reihenfolge). Der Befehl muss auch wirklich laufen – in der falschen Shell zählt er nicht.
* `ziel` (frei): Bedingung auf den Zustand; ist sie nach irgendeinem Befehl erfüllt, ist der Schritt
  auch geschafft (z. B. `cd .\documents` statt `cd Documents`).
* `wenn` (frei): Bedingung, die **zusätzlich** zur Eingabe gelten muss (z. B. im richtigen Ordner).

## Aufgaben

```json
{"aufgabe": "Wechsle in den Ordner Downloads und zeig dort an, was darin liegt.",
 "eingabe": ["Get-ChildItem", "dir", "ls", "gci"],
 "wenn": {"pfad": "C:\\Users\\mberger\\Downloads"},
 "hinweise": ["Richtung", "Werkzeug", "Fast die Lösung"],
 "loesung": ["cd Downloads", "dir"],
 "danach": "Richtig."}
```

* Wie Mitmachen, nur ohne Vorgabe: `eingabe` und/oder `ziel` (mindestens eins), `wenn` frei.
* `hinweise`: genau drei (F1, Stufe für Stufe).
* `loesung`: Befehle, mit denen der Test die Aufgabe automatisch löst (Standard: erste `eingabe`).

## Regeln

* Gleiche Regeln wie bei Szenarien: Ausgaben passend zur offiziellen Doku, sonst kürzen (`notiz`) oder
  als Meldung der Simulation (`"sim": true`). Namen, Rechner und IP-Adressen sind erfunden
  (192.168.x.x / 10.x.x.x).
* Texte für Tobi: einfach, Fachbegriffe beim ersten Auftreten erklären, Befehle im Original.
* Ein Test spielt jede Lektion vollständig durch (`tests/test_grundkurs.py`).
