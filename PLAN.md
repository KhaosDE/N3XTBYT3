# PLAN — N3XTBYT3

Stand: 04.11.2026. Ziel: M1 und M2 vor Juni 2027 fertig und von Tobi getestet.
Regeln für die Arbeit: `CLAUDE.md`. Fortschritt: `STAND.md`.

Jeder Meilenstein gilt erst als fertig, wenn **alle** Abnahmekriterien erfüllt sind und
die Tests grün laufen.

---

## M1 — Grundgerüst und Windows

### M1.1 Kern ohne Oberfläche
- Szenario-Format festlegen und in `daten/szenarien/SCHEMA.md` beschreiben. Mindestens:
  `id`, `system`, `titel`, `kategorie`, `schwierigkeit` (1–3), `pruefstatus`
  (`ungeprueft`/`bestaetigt`), `quelle`, `datum`, `ausgangslage` (was der Nutzer sieht,
  z. B. die Fehlermeldung), `zustand` (Startwerte, z. B. Dienst gestoppt),
  `befehle` (Befehlsbündel: welche Befehle es kennt, welche Ausgabe je nach Zustand,
  welche Zustandsänderung), `ziel` (Bedingung für „gelöst“), `hinweise` (3 Stufen:
  Richtung → Werkzeug → fast die Lösung), `erklaerung` (warum das die Lösung ist),
  `begriffe` (Fachbegriffe mit kurzer Erklärung).
- Szenario-Lader mit Prüfung (fehlende Felder, unbekannte Systeme → klare Fehlermeldung).
- Befehlsauswertung: Eingabe zerlegen, Groß-/Kleinschreibung wie im echten System
  (Windows tolerant, Linux streng), Parameter-Varianten, unbekannter Befehl → Meldung
  „In dieser Simulation nicht vorhanden“ plus Hinweis.
- Simulierter Zustand je Szenario (Dienste, Dateien, Netzwerk-Werte, Speicherplatz …).
- Allgemeine Befehle, die in jedem Szenario eines Systems gehen (z. B. `help`, `cls`/`clear`,
  `hostname`), getrennt von den Szenario-Befehlen.

### M1.2 Oberfläche
- Hauptmenü: vier Systeme; noch nicht gefüllte Systeme sichtbar, aber als
  „kommt noch“ gekennzeichnet.
- Terminal mit Eingabezeile, Verlauf (Pfeiltasten), Scrollen, Kopf mit Systemname.
- Seitenbereich: Aufgabe, Hinweis-Knopf/Taste (Stufe für Stufe), Begriffe, Erklärung nach
  dem Lösen, Prüfstatus des Szenarios („ungeprüft“ deutlich sichtbar).
- Aussehen nach `CLAUDE.md`, Abschnitt „Aussehen“.

### M1.3 Spielstand je System
- Je Szenario: Versuche, gelöst ja/nein, benutzte Hinweisstufen, falsche und unbekannte
  Befehle, Zeit.
- Lesbares JSON, Speicherort nach `CLAUDE.md`.
- Szenarioauswahl: zufällig, ungelöste und schwache Szenarien bevorzugt.

### M1.4 Windows-Inhalte
- 10–15 Szenarien aus dem Alltag am Windows-PC, mit `cmd` und PowerShell. Beispiele:
  kein Internet (IP-Konfiguration, DNS-Cache, Ping), Druckauftrag hängt
  (Druckwarteschlange, Dienst neu starten), Festplatte voll, Dienst startet nicht,
  Programm reagiert nicht (Prozess finden und beenden), falsche Uhrzeit, Benutzer
  gesperrt, Netzlaufwerk fehlt, langsamer Start (Autostart).
- Jedes Szenario mit `quelle` (offizielle Doku) und `"pruefstatus": "ungeprueft"`.
- `vorlagen/szenario_vorlage.json` und Anleitung `docs/eigenes_szenario.md`: wie Tobi
  einen echten Fehler als Szenario anlegt (auch: „gib Claude diese Vorlage und deine
  Fehlerbeschreibung“).

### M1.5 Tests und Programmdatei
- Tests: jedes Szenario lädt fehlerfrei; jedes Szenario ist mit seinen eigenen Befehlen
  lösbar (automatischer Durchlauf über einen hinterlegten Lösungsweg); **Sicherheitstest:**
  im Paket `n3xtbyt3` kommen `subprocess`, `os.system`, `socket` und `urllib` nicht vor.
- GitHub Actions: Tests unter Windows, Bau einer `.exe` mit PyInstaller, als Artefakt
  herunterladbar.
- `README.md`: Starten, Spielen, Szenario hinzufügen — in einfachen Worten.

**Abnahme M1:** Tobi startet die `.exe`, wählt Windows, löst mindestens drei Szenarien
mit Hinweisen, beendet, startet neu — der Fortschritt ist noch da.

---

## M2 — Windows Server, Lernkartei, Auswertung

- Windows-Server-Szenarien (PowerShell), mindestens 15: Benutzer und Gruppen im
  Active Directory, Passwort zurücksetzen, Konto entsperren, DNS-Eintrag fehlt,
  DHCP-Bereich erschöpft, Freigabe und NTFS-Rechte, Gruppenrichtlinie greift nicht,
  Dienst/Rolle prüfen, Ereignisanzeige lesen, Speicherplatz auf dem Server.
- **Lernkartei:** Szenarien und einzelne Befehle wandern durch Fächer (Wiederholung in
  wachsenden Abständen). Falsch → zurück nach vorn. Die Szenarioauswahl richtet sich danach.
- **Befehls-Training** als zweiter Modus: kurze Abfragen „Welcher Befehl zeigt …?“ aus
  den Befehlen der Szenarien.
- **Auswertungsdatei** je System (`auswertung.json` und lesbare `auswertung.md`):
  Stärken, Schwächen nach Kategorie und Befehl, häufige Fehler, Empfehlung, was als
  Nächstes geübt werden sollte. Gedacht dafür, dass Claude sie lesen kann.

**Abnahme M2:** Windows Server spielbar; nach einigen Durchläufen zeigt die Auswertung
plausible Schwächen; falsch gelöste Szenarien kommen sichtbar öfter wieder.

---

## M3 — Linux und Linux Server

- Linux-Szenarien (Bash), mindestens 15: Dateirechte, Besitzer, Pakete installieren und
  aktualisieren, Speicherplatz (`df`, `du`), Prozesse, Netzwerk (`ip`, `ping`, DNS),
  Protokolle lesen.
- Linux-Server-Szenarien, mindestens 15: Dienste mit `systemctl`, Protokolle mit
  `journalctl`, Firewall (`ufw`), SSH-Zugang, Cron-Aufgaben, Webserver startet nicht
  (Konfigurationsfehler), voller Datenträger durch Protokolle, Benutzer und `sudo`.
- Simuliertes Dateisystem mit `cd`, `ls`, `cat`, `nano`-Ersatz (einfacher Editor im
  Terminal) für Konfigurationsdateien.

**Abnahme M3:** alle vier Systeme spielbar, Auswertung und Lernkartei funktionieren je System.

---

## M4 — Abwechslung, Netzwerk, Claude

- **Tickets:** ein Modus, in dem Szenarien als Ticket mit Bearbeitungsanfrage und
  Dringlichkeit kommen; Ablauf über mehrere Schritte (z. B. Fehlermeldung am Windows-PC
  → per `ssh` auf einen simulierten Server → Problem dort lösen → Ticket schließen).
- **Mehrere simulierte Rechner** in einem Szenario, Wechsel per `ssh`/`Enter-PSSession`;
  Fehler, die über Rechnergrenzen gehen (DNS, Firewall, Freigaben).
- **MCP-Server** (Python, lokal, nur lesend + Szenario-Entwürfe): Werkzeuge zum Lesen
  von Spielstand und Auswertung je System, zum Auflisten der Szenarien und zum Anlegen
  eines neuen Szenario-Entwurfs (immer `ungeprueft`). Anleitung zum Einbinden in Claude
  Desktop in `docs/mcp.md`. Claude wertet nur aus, wenn Tobi im Chat fragt.

**Abnahme M4:** Ein Ticket-Einsatz über zwei Rechner ist spielbar; in Claude Desktop
liefert der MCP-Server die Auswertung eines Systems.

---

## G — Grundkurs „Konsole von den Babyschuhen an“ (aus IDEEN.md, freigegeben 05.11.2026)

Ein geführter Grundkurs je System, der bei null anfängt, dazu Befehlsbuch und Lexikon.
Ausführliche Beschreibung: `IDEEN.md`, Eintrag „Grundkurs“.

- G1 Kern: Lektionen als Daten (`daten/grundkurs/<system>/<nr>-<id>.json`, Format in
  `daten/grundkurs/SCHEMA.md`), Lektionsablauf (Erklären → Mitmachen → Selbst probieren →
  „Das kannst du jetzt“), Fortschritt im Spielstand, Feld `voraussetzung` für Szenarien.
- G2 Simuliertes Dateisystem auch für Windows (PowerShell und cmd), weil die Lektionen
  Ordner und Dateien brauchen; unter Linux zusätzlich `cp`, `mv`, `rm`, `mkdir`.
- G3 Windows-Lektionen 1–10 (PowerShell zuerst), Lektion 10 mit geführtem Szenario.
- G4 Oberfläche: Willkommensbild beim ersten Start, „Grundkurs“ als erster Eintrag je System mit
  Fortschritt, Lektionsansicht, „braucht: Lektion n“ in der Szenarioliste.
- G5 Befehlsbuch (F4) mit „Was tippe ich, wenn …?“ (mind. 10 Situationen je System) und
  Lexikon (F5) mit Suche, beide überall erreichbar, aus den Daten erzeugt.
- G6 Grundkurs in Auswertung und Befehls-Training; `voraussetzung` in allen Szenarien nachgetragen.
- G7 Grundkurse für Windows Server, Linux und Linux Server.

**Abnahme G:** Erster Start zeigt das Willkommensbild, „Grundkurs starten“ führt in Windows-Lektion 1;
Tobi kommt ohne Vorwissen durch die Windows-Lektionen 1–10; Befehlsbuch und Lexikon sind von überall
erreichbar, „Was tippe ich, wenn …?“ hat mindestens 10 Situationen je System; Grundkurse für alle vier
Systeme vorhanden.

---

## Laufend (nach M1)

Tobis echte Fehler mit funktionierender Lösung als Szenario aufnehmen (`bestaetigt`).
