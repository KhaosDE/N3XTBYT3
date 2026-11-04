"""Gemeinsame Hilfen für die Tests."""

import copy
import os
import tempfile

MINI = {
    "id": "test-mini",
    "system": "windows",
    "titel": "Testszenario",
    "kategorie": "Test",
    "schwierigkeit": 1,
    "pruefstatus": "ungeprueft",
    "quelle": "https://learn.microsoft.com/windows-server/administration/windows-commands/net-start",
    "datum": "2026-11-04",
    "ausgangslage": "Ein Dienst läuft nicht.",
    "zustand": {"dienst": "Stopped"},
    "befehle": [
        {
            "muster": ["Get-Service Testdienst"],
            "faelle": [
                {"wenn": {"dienst": "Stopped"}, "ausgabe": "Stopped  Testdienst"},
                {"ausgabe": "Running  Testdienst"},
            ],
        },
        {
            "muster": ["Start-Service Testdienst", "Start-Service -Name Testdienst"],
            "faelle": [{"setze": {"dienst": "Running"}}],
        },
        {
            "muster": ["shutdown /r /t 0"],
            "falsch": True,
            "warum": "Ein Neustart ist hier der Holzhammer.",
            "faelle": [{"ausgabe": ""}],
        },
        {
            "muster": ["sc.exe query Testdienst", "sc query Testdienst"],
            "shell": "cmd",
            "faelle": [{"ausgabe": "SERVICE_NAME: Testdienst"}],
        },
    ],
    "ziel": {"dienst": "Running"},
    "hinweise": ["Richtung", "Werkzeug", "Fast die Lösung"],
    "erklaerung": "Der Dienst musste gestartet werden.",
    "begriffe": {"Dienst": "Ein Programm, das im Hintergrund läuft."},
    "loesung": ["Get-Service Testdienst", "Start-Service Testdienst"],
}


def mini(**aenderungen):
    daten = copy.deepcopy(MINI)
    for k, v in aenderungen.items():
        if v is None:
            daten.pop(k, None)
        else:
            daten[k] = v
    return daten


class Datenordner:
    """Lenkt den Datenordner für die Dauer eines Tests in einen leeren Ordner um."""

    def __enter__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._alt = os.environ.get("N3XTBYT3_DATEN")
        os.environ["N3XTBYT3_DATEN"] = self._tmp.name
        return self._tmp.name

    def __exit__(self, *exc):
        if self._alt is None:
            os.environ.pop("N3XTBYT3_DATEN", None)
        else:
            os.environ["N3XTBYT3_DATEN"] = self._alt
        self._tmp.cleanup()
