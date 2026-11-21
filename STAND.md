# STAND — N3XTBYT3

Stand: 20.11.2026.

## Aktuell

**M1 bis M4 sind fertig, dazu der Grundkurs „Konsole von den Babyschuhen an“ (G, aus `IDEEN.md`)**
(bis auf deine Abnahmetests, siehe unten). Alle vier Systeme haben jetzt einen Grundkurs
(10 + 8 + 10 + 7 Lektionen), ein Befehlsbuch (F4) und ein Lexikon (F5).

**Neu: Selbst-Update der `.exe`** (dein Wunsch vom 05.11.2026, Ausnahme zu Regel 1 in `CLAUDE.md`).
Das Repository ist seit 05.11.2026 öffentlich; der feste Download-Link und der echte Update-Ablauf
(Release laden, Prüfsumme, Austausch) sind von außen geprüft.

**Neu (07.11.2026): Große Bugsuche.** Vier Prüfer haben Befehlsauswertung, Linux- und Windows-Dateisystem,
Editor und Oberfläche durchgesehen, dazu Fuzzing (Zufallseingaben) von Kern und Oberfläche. Rund 60 echte Fehler
sind behoben, jeder mit Test (`tests/test_bugfixes.py`, `tests/test_oberflaeche.py`). Einzelheiten in `docs/verlauf.md` unter
„Bugsuche 07.11.2026“.

**Neu (07.11.2026): Logikprüfung (L, aus `IDEEN.md`).** Tippfehler werden jetzt beim Namen genannt –
im Grundkurs und in allen Szenarien, auf allen vier Systemen. Echte PowerShell-Aliase (`gsv`, `dir`, `ri` …)
und `-Name` werden angenommen. Einzelheiten in `docs/verlauf.md` unter „Logikprüfung 07.11.2026“.

**Neu (20.11.2026): Lernprinzip (D, aus `IDEEN.md`).** Grundkurs und Szenarien erklären jetzt jeden Befehl und
jeden Zusatz, bevor eine Aufgabe ihn verlangt; jede Erklärung erklärt wirklich etwas. Einzelheiten in `docs/verlauf.md` unter
„Lernprinzip 20.11.2026“.

**Nächster Schritt:** Deine Tests und Rückmeldungen – vor allem: Kommst du ohne Vorwissen durch die
Windows-Lektionen 1–10? Danach laufend: deine echten Fehler als Szenarien aufnehmen und Ausgaben,
die vom echten System abweichen, korrigieren.

## Fertig

Alles Erledigte (Meilensteine M1–M4, Grundkurs G, Selbst-Update, Lernprinzip, Logikprüfung, Bugsuche)
samt abgehakter Abnahmen steht wortgleich in `docs/verlauf.md`, Abschnitt „Fertig“.

## Offene Punkte

- Szenario-Ausgaben sind „ungeprüft“. Bitte beim Spielen auf Abweichungen zum echten Windows achten.
  Besonders unsicher (bewusst so markiert oder gekürzt):
  - `Get-Volume`: Spaltenformat von Windows 10/11; das Beispiel in der Microsoft-Doku ist älter.
  - `ping` ohne Netzwerkadapter („PING: transmit failed. General failure.“).
  - `net user jschulz`: Ausgabe gekürzt (Passwort- und Anmeldezeilen weggelassen).
  - Wo die echte Ausgabe nicht sicher bekannt ist oder ein Fenster aufgehen würde, zeigt die
    Simulation eine blaue `[N3XTBYT3]`-Meldung statt eines erfundenen Textes.
- Tobis Meldung „whoami bei Aufgabe 2 nicht erkannt“ (06.11.2026) ließ sich nicht nachstellen. Kommt es wieder
  vor: `grundkurs_protokoll.txt` aus `%APPDATA%\N3XTBYT3` schicken – darin steht die Eingabe genau, wie sie ankam.
- Grundkurs: Lektionen, Befehlsbuch und Lexikon sind „ungeprüft“. Besonders unsicher:
  - `Get-ChildItem`: Spalten und Datumsformat nach dem Beispiel der Microsoft-Doku (Uhrzeit 24 Stunden,
    z. B. `08:29`). Ein echtes englisches Windows zeigt die Uhrzeit vermutlich als `8:29 AM`.
  - `Get-Command`: Spalten Version/Source nach der Beschreibung in der Doku; Spaltenbreiten wie im Beispiel.
  - `Resolve-DnsName` und `Get-Service … | Select-Object …`: Spaltenformat nicht aus einem Doku-Beispiel.
  - `whatis` (Spaltenbreite) und Ubuntus Meldung „Command 'Whoami' not found, did you mean:“ (gekürzt).
  - Neue Dateien unter Linux: `rw-rw-r--` (Ubuntu-Standard für normale Benutzer, umask 002).
  - `Get-Help`, `man`, `systeminfo`, Prozess- und Dienstlisten sind gekürzt (blaue Notiz darunter).

## Entscheidungen

Neue Entscheidungen hier eintragen. Die bisherigen (04.11.–20.11.2026) stehen wortgleich in
`docs/verlauf.md`, Abschnitt „Entscheidungen“.

## Für Tobi zum Testen

**Neu: Lernprinzip (20.11.2026)**

1. Windows-Lektion 6 von vorn spielen: Weißt du bei jeder Excel-Aufgabe ohne F1, was zu tippen ist und warum?
2. Eine Lektion je Kurs lesen wie ein Einsteiger: Ist jede Erklärung nach einem Schritt verständlich und hilfreich?
3. Ein Szenario lösen und danach die Erklärung lesen („So gehst du vor …“): Passt sie zu dem, was du getan hast?
4. Wo du stockst oder etwas nicht erklärt findest: Lektion und Schritt notieren und mir sagen.


**Neu: Logikprüfung (07.11.2026)**

1. Grundkurs Windows, Lektion 3, Aufgabe 2: absichtlich `get-command *-prcoess` tippen. Steht im Terminal
   „Fast! Schau dir „prcoess“ an …“? Dann `gcm *-Process` – löst es die Aufgabe?
2. In beliebigen Windows-Szenarien Aliase probieren: `gsv`, `dir`, `del`, `ps` … und `Get-Service -Name Spooler`.
3. Absichtlich vertippen: `pnig …`, `sduo …`, ein falscher Ordnername bei `cd`. Ist der Vorschlag hilfreich?
4. Linux Server, „Hintergrunddienst stürzt immer wieder ab“: `sudo chown -R shop:hsop /var/lib/shop` → `invalid group`?
5. Optional: `Get-Command *xyz*` in deinem echten Windows – kommt nichts oder eine Fehlermeldung?

**Nach der Bugsuche (07.11.2026)** – die `.exe` aktualisiert sich beim nächsten Start selbst.

1. Linux-Kurs, Lektion mit nano: Datei ändern, Strg+X, mit J antworten. Kommt danach im Terminal kein
   „j“ mehr an?
2. Tickets (Kachel 5): F4 und F5 drücken – kein Absturz mehr. Im Ticket halb einen Befehl tippen, F3,
   Esc: Ist der halbe Befehl wieder da?
3. Schrift groß stellen (Strg + mehrmals): Passt das Hauptmenü, kann man in der Lektionsliste bis
   Lektion 10 blättern, passen die Knöpfe rechts?
4. Windows-Szenario „Excel reagiert nicht mehr“: in der cmd `taskkill /IM EXCEL.EXE /F` – geht jetzt.
5. Linux: `ls -l /home`, `cat /root/...`, `cp` auf eine Datei in `/etc` ohne sudo – stimmen die
   Meldungen mit deinem Ubuntu überein?


**Neu: Grundkurs**

1. Neueste `.exe` holen (wie unten). Das Willkommensbild kommt nur, solange es noch keinen Spielstand gibt.
   Hast du schon gespielt, startest du den Grundkurs über Windows → erster Eintrag „Grundkurs“.
   (Nur wenn du das Willkommensbild sehen willst: Ordner `%APPDATA%\N3XTBYT3` vorher umbenennen, z. B. in
   `N3XTBYT3-alt`. Was du dann spielst, landet im neuen Ordner.)
2. Im Willkommensbild Enter (bzw. „Grundkurs“): Windows-Lektion 1 startet. Arbeite die Lektionen 1–10 der
   Reihe nach durch.
   Wichtigste Frage: Kommst du durch, ohne woanders nachzusehen? Wo hast du gestockt?
3. Absichtlich vertippen (z. B. `hostnme`): Ist der Hinweis rechts hilfreich?
4. F4 (Befehlsbuch) und F5 (Lexikon) an verschiedenen Stellen drücken, etwas suchen, Tab im Befehlsbuch.
5. In der Szenarioliste: Steht der Grundkurs oben, und zeigen Szenarien „braucht: Lektion n“?
6. Wenn Zeit ist: je eine Lektion in Windows Server, Linux und Linux Server.

**Bisherige Tests (M1–M4)**

1. `.exe` holen: GitHub → Actions → neuester grüner Lauf → unten „N3XTBYT3-Windows“ → entpacken.
   Windows warnt beim ersten Start (nicht signiert): „Weitere Informationen“ → „Trotzdem ausführen“.
2. Windows wählen, „Zufälliges Szenario“, mindestens drei Szenarien lösen. Dabei auch mal F1 drücken.
3. Programm schließen, wieder öffnen: In der Liste müssen die gelösten Szenarien grün sein.
4. Schrift mit Strg + / Strg − anpassen, F11 für Vollbild. Ist alles gut lesbar?
5. Windows Server: ein paar Szenarien spielen, eines mit Esc abbrechen. Dann „Auswertung ansehen“:
   Steht das abgebrochene Szenario bei den Schwächen und in der Empfehlung? Kommt es bei
   „Zufälliges Szenario“ öfter dran?
6. Linux und Linux Server: z. B. „Webserver startet nicht nach Änderung“ – Fehler mit `sudo nginx -t`
   finden, mit `sudo nano …` beheben (Strg+O, Strg+X), `sudo systemctl restart nginx`. Ist der Editor
   gut bedienbar? Stimmen die Ausgaben mit deinem Ubuntu überein?
7. Tickets: Kachel 5 im Hauptmenü, „Webshop zeigt 502 Bad Gateway“ spielen (vom PC per
   `ssh admin@srv-web01` auf den Server, zurück mit `exit`), am Ende F3 und eine kurze Notiz.
8. Claude Desktop: MCP-Server nach `docs/mcp.md` einrichten und nach deiner Auswertung fragen.
9. Befehls-Training ausprobieren: Sind die Fragen verständlich? Ist die Bewertung fair?
10. Auf Abweichungen zum echten System achten (Ausgaben, Fehlermeldungen) und mir sagen,
   welches Szenario. Wenn alles stimmt: in der Datei `"pruefstatus": "bestaetigt"` setzen.
