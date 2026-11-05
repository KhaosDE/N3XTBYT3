"""Selbst-Update der Windows-Programmdatei (Ausnahme von Regel 1, Entscheidung Tobi, 05.11.2026).

Nur dieses Paket darf ins Netz – und nur zu den Releases dieses Repositorys auf GitHub:

1. Beim Start der .exe fragt es https://api.github.com/repos/KhaosDE/N3XTBYT3/releases/latest,
   ob es einen neueren Build gibt (Zeitlimit wenige Sekunden; ohne Netz geht es einfach weiter).
2. Wenn ja: lädt es ``N3XTBYT3.exe`` und die Prüfsumme ``N3XTBYT3.exe.sha256`` und vergleicht beide.
3. Es benennt die laufende .exe in ``N3XTBYT3.exe.alt`` um, legt die neue an ihren Platz, startet sie
   und beendet sich. Die neue Version löscht beim Start die alte Datei.

Jeder Fehler (kein Netz, Repository nicht öffentlich, kein Schreibrecht im Ordner …) wird in
``update.log`` im Datenordner notiert – das Programm startet dann ganz normal in der alten Version.
Abschalten: ``"auto_update": false`` in ``einstellungen.json`` oder Startparameter ``--kein-update``.

Das Lernprogramm (Paket ``n3xtbyt3``) und der MCP-Server bleiben ohne Netz; ein Test prüft das.
"""

from .aktualisierung import beim_start

__all__ = ["beim_start"]
