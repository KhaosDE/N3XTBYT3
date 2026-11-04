# N3XTBYT3 mit Claude Desktop verbinden (MCP-Server)

Mit dem MCP-Server kann Claude Desktop deinen Lernstand lesen. Dann kannst du im Chat z. B. fragen:
„Wo stehe ich bei Windows Server, und was soll ich als Nächstes üben?“ – Claude liest dafür die
Auswertung. Claude schaut nur nach, wenn du im Chat fragst; der Server tut nichts von sich aus.

## Was der Server darf

| Werkzeug | Wirkung |
|---|---|
| `systeme_uebersicht` | Überblick über alle vier Systeme (Anzahl Szenarien, gelöst, Versuche) |
| `auswertung_lesen` | Auswertung eines Systems: Stärken, Schwächen, häufige Fehler, Empfehlung |
| `spielstand_lesen` | Spielstand eines Systems (alle Versuche) |
| `szenarien_auflisten` | Szenarien eines Systems mit Prüfstatus und Lernstand |
| `szenario_lesen` | Eine Szenario-Datei vollständig |
| `szenario_format` | Szenario-Format und Vorlage |
| `szenario_entwurf_anlegen` | **Einziges schreibendes Werkzeug:** legt einen neuen Szenario-Entwurf in deinem Datenordner an |

Sicherheit:

- Der Server spricht nur über die Ein- und Ausgabe mit Claude Desktop – kein Netzwerk, keine Systembefehle.
- Er ändert nie deinen Spielstand.
- Entwürfe sind immer `"pruefstatus": "ungeprueft"` und überschreiben nie eine vorhandene Datei. Vor dem
  Speichern prüft der Server das Format und spielt den Lösungsweg durch. Der Entwurf erscheint danach im
  Programm mit den Markierungen „eigen“ und „ungeprüft“.

## Einrichten (Windows)

### 1. Programmdatei holen

Im selben GitHub-Lauf wie die `N3XTBYT3.exe` gibt es das Artefakt **N3XTBYT3-MCP-Windows** mit der Datei
`N3XTBYT3-MCP.exe` (GitHub → Actions → neuester grüner Lauf → unten bei Artifacts).
Leg sie in einen festen Ordner, z. B. `C:\Programme\N3XTBYT3\N3XTBYT3-MCP.exe`.

Die Datei öffnet kein Fenster. Ein Doppelklick bringt nichts – sie wird von Claude Desktop gestartet.

### 2. Claude Desktop einstellen

So steht es in der Anleitung zu lokalen MCP-Servern
(<https://modelcontextprotocol.io/docs/develop/connect-local-servers>):

1. In Claude Desktop die Einstellungen öffnen, links den Bereich **Developer** wählen und auf
   **Edit Config** klicken. Das öffnet die Datei `%APPDATA%\Claude\claude_desktop_config.json`.
2. Den Eintrag für N3XTBYT3 hinzufügen (Pfad an deinen Ordner anpassen, Backslashes doppelt schreiben):

```json
{
  "mcpServers": {
    "n3xtbyt3": {
      "command": "C:\\Programme\\N3XTBYT3\\N3XTBYT3-MCP.exe"
    }
  }
}
```

   Stehen in der Datei schon andere Server unter `"mcpServers"`, kommt `"n3xtbyt3": { … }` mit einem
   Komma dazu.
3. Speichern, Claude Desktop **ganz beenden** (auch im Infobereich der Taskleiste) und neu starten.

### Ohne .exe (mit Python 3.12)

Statt der `.exe` geht auch Python. Dann im Eintrag:

```json
"n3xtbyt3": {
  "command": "python",
  "args": ["C:\\Pfad\\zu\\N3XTBYT3\\start_mcp.py"]
}
```

## Ausprobieren

Im Chat in Claude Desktop zum Beispiel fragen:

- „Wie ist meine Auswertung für Windows Server?“
- „Welche Linux-Szenarien habe ich noch nicht gelöst?“
- „Ich hatte heute diesen Fehler: … Leg dafür bitte einen Szenario-Entwurf für Windows an.“

Claude fragt vor dem ersten Benutzen eines Werkzeugs um Erlaubnis.

## Wenn es nicht klappt

- Den Pfad in der Konfiguration prüfen (doppelte Backslashes, Datei vorhanden?).
- Selbsttest in PowerShell im Ordner der `.exe` (die Antwort ist eine Zeile JSON mit der Werkzeugliste):

```powershell
'{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | .\N3XTBYT3-MCP.exe
```

- Claude Desktop schreibt Protokolle für MCP-Server; wo sie liegen, steht in der oben genannten Anleitung.
