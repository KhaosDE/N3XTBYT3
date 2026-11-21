# Technik — N3XTBYT3

Wortgleich aus `CLAUDE.md` (Abschnitt „Technik“) hierher verschoben (21.11.2026). Vor technischen Änderungen lesen.

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

## Selbst-Update

Wortgleich aus `CLAUDE.md`, „Unverhandelbar“, Regel 1 (verschoben 21.11.2026); die Regel selbst steht dort weiter:

**Einzige Ausnahme (Entscheidung Tobi, 05.11.2026): Selbst-Update der `.exe`.** Das Paket
`n3xtbyt3_update` darf beim Start der `.exe` bei GitHub nach einem neueren Release *dieses*
Repositorys fragen, die neue `.exe` samt Prüfsumme laden, sie nach Prüfung gegen die laufende
Datei tauschen und starten. Sonst nichts – keine anderen Adressen, keine anderen Befehle. Das
Lernprogramm (`n3xtbyt3`) und der MCP-Server bleiben ohne Netz und ohne Systemaufrufe; Tests
prüfen beides. Das Repository muss dafür öffentlich sein, die `.exe` enthält keinen Schlüssel.
