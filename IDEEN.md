# IDEEN — N3XTBYT3

Ideen für das Programm, nur offene. Werden im Chat ausgearbeitet und hier eingetragen.
Gebaut wird nur, was `Status: bereit` hat; neue Einfälle bekommen `Status: in Klärung`. Erledigtes wird
gelöscht (Zeile in `SITZUNGEN.md`), Verworfenes steht mit Grund in `docs/entscheidungen.md`.

Aufbau eines Eintrags:

```
## <Titel>
Status: in Klärung | bereit
Datum: <Datum>
Was: <ein bis drei Sätze, was es tun soll>
Warum: <wofür Tobi es braucht>
Umfang: <was dazu gehört, was ausdrücklich nicht>
```

## Szenarien aus gelösten Problemen in Tobis Notizen
Status: in Klärung
Datum: 04.11.2026
Was: Gelöste Probleme aus Tobis Notizen (Einträge mit `#lehre`) als Szenarien übernehmen.
Warum: echte Fehler als Lernstoff.
Umfang: Tobi liefert die Texte; nichts selbst zusammensuchen.

## Prüfungsmodus
Status: in Klärung
Datum: 04.11.2026
Was: Szenarien ohne Hinweise und mit Zeitlimit, passend zur Weiterbildung.
Warum: Prüfungssituation üben.
Umfang: noch nicht ausgearbeitet.

## Weiterbildung A: Szenarien zum ILS-Lehrplan (Windows Server)
Status: in Klärung
Datum: 12.11.2026
Was: Neue Fehlerszenarien, die die Themen des ILS-Lehrgangs „Netzwerkadministrator für MS
Windows Server" abdecken, soweit sie sich im Terminal nachbauen lassen.
Warum: Prüfungsstoff der Weiterbildung; bisher fehlt vor allem die PowerShell-Vertiefung.

### ILS-Lehrplan (recherchiert 12.11.2026, Quellen unten)
Themen laut ILS: Netzwerk-Grundlagen (Topologien, Hardware, LAN-WAN, TCP/IP, IPv4/IPv6),
Windows Server 2019/2022, Domäne und Active Directory, zentrale Benutzer-/Ressourcen-
verwaltung, Gruppenrichtlinien, Bereitstellungsdienste, Routing, DNS und DHCP, Fernzugriff
(Remotedesktop, VPN/IPSec), Webserver IIS, Druckdienste, heterogene Netze mit Linux
(Debian/openSUSE), Sicherheitsaspekte, Windows PowerShell, Hyper-V, Server Core,
Virtualisierung (VMware). 21 Monate, ca. 7 h/Woche.
**Nicht ausdrücklich genannt:** Subnetting und Datensicherung (Subnetting steckt sachlich im
TCP/IP-Teil). Backup wird daher in A nur optional geführt.

### Was A abdeckt (Terminal) – nach Priorität
1. **PowerShell vertiefen** (ILS „Windows PowerShell"; fehlt ganz, höchste Priorität):
   Pipeline `|`, `Where-Object` (filtern), `Sort-Object`, `Select-Object`, `Measure-Object`
   (zählen/summieren), `Format-Table`/`Format-List`, Variablen, eine einfache `foreach`-Schleife.
2. **Routing und Netzwerk-Diagnose** (ILS „Routing", „LAN-WAN"): `route print`, Routing-
   Tabelle lesen, `tracert`, `pathping`, `netstat -ano`, `Test-NetConnection` genauer.
3. **DNS/DHCP vertiefen** (ILS „DNS und DHCP"; Grundlagen schon da): Zonentypen, Weiter-
   leitung, Reverse-Lookup, DHCP-Reservierung, Lease anzeigen.
4. **Active Directory vertiefen** (ILS „zentrale Benutzerverwaltung", „Gruppenrichtlinien";
   Grundlagen da): Benutzer mit CSV anlegen (`Import-Csv | foreach`), OU verschieben,
   Gruppenmitgliedschaften prüfen, GPO einer OU zuordnen.
5. **IIS Webserver** (ILS „Webserver IIS"): Dienst `W3SVC` prüfen/neu starten, Website mit
   `Get-Website` ansehen, Standardseite erreichbar machen.
6. **Druckdienste auf dem Server** (ILS „Druckdienste"; PC-Spooler schon da): Druckerwarte-
   schlange auf dem Server, hängenden Druckauftrag entfernen.
7. **Sicherheit/Fernzugriff** (ILS „Sicherheitsaspekte", „Remotedesktop"; Abwehr-konform,
   Regel 5): Firewall-Regel setzen/prüfen (`Get-NetFirewallRule`, `New-NetFirewallRule`),
   RDP-Zugang prüfen. Kein VPN/IPSec (Theorie, nicht im Terminal) – gehört zu B.
8. **Optional, eingeschränkt:** Backup (`wbadmin`), Hyper-V/Server Core als reine
   Befehlsübung (keine Oberfläche).

### Nicht in A (gehört zu B oder entfällt)
TCP/IP, IPv4/IPv6, Subnetting, Topologien, Netzwerkhardware, OSI → Rechnen/Quiz in B.
VMware/Hyper-V-Oberfläche, physische Hardware, VPN-Einrichtung → nicht im Simulator
(Regel C aus dem Konzept), höchstens als Quiz-Begriffe.

### Vorgehen
Themen 1–7 nacheinander, Thema 1 (PowerShell) zuerst und als eigener kleiner Grundkurs-
Zweig (Mitmachen → Selbst probieren), die übrigen als Fehlerszenarien in den bestehenden
Systemen. Jedes mit `quelle` (Microsoft Learn) und `pruefstatus: ungeprueft`. Reiht sich in
die vier Systeme ein, kein neues Format. Der Didaktik-Test (oben) gilt auch hier.

### Vor der Freigabe (hier im Chat)
Thema 1 (PowerShell-Pipeline) wird als Erstes ausgearbeitet: Liste der 6–8 Aufgaben mit
geprüften Ausgaben. Dann freigeben. Die übrigen Themen folgen einzeln.

Quellen ILS-Lehrplan:
- https://www.fernstudi.net/weiterbildung/informatik/netzwerktechnik/11535
- https://www.studieren-studium.com/studieren/Gepruefte_r_Netzwerkadministrator_in_fuer_MS_Windows_Server_ILS_Lehrgang_ILS_Institut_fuer_Lernsysteme_122847

## Weiterbildung B: Übungsarten ohne Terminal (Subnetting, Theorie-Quiz)
Status: in Klärung
Datum: 12.11.2026
Was: Zwei neue Übungsarten, die kein Terminal brauchen und als eigener Modus laufen:
- Subnetting rechnen: Netz, Broadcast, Hostzahl, CIDR — Aufgaben mit Zufallswerten und
  Korrektur, Rechenweg als Erklärung.
- Theorie-Quiz: OSI-Modell, Netzwerk-Topologien, Netzwerkhardware, wichtige Ports und
  Protokolle, RAID-Level, Fachbegriffe.
Warum: Prüfungsstoff, der im reinen Befehls-Trainer nicht abbildbar ist. Deckt die
ILS-Themen ab, die A nicht fasst (TCP/IP, IPv4/IPv6, Topologien, Hardware).
Hinweis: Der ILS-Lehrplan nennt „Subnetting" nicht ausdrücklich, sondern „TCP/IP, IPv4 und
IPv6"; Subnetting gehört sachlich dazu und ist typischer Prüfungsstoff.
Umfang: noch nicht ausgearbeitet. Eigener Menüpunkt neben den Systemen; Fortschritt und
Lernkartei wie bei den Szenarien. Aufgaben und Quizfragen als Daten (nicht im Code), mit
Quelle. Vor dem Bauen: Aufgabentypen und Fragenkatalog hier im Chat festlegen.
