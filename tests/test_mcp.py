"""Tests für den MCP-Server (Abnahme M4: liefert die Auswertung eines Systems)."""

import io
import json
import unittest
from pathlib import Path

from n3xtbyt3.kern.spielstand import Spielstand
from n3xtbyt3_mcp import server

from .hilfen import Datenordner, mini


def rufe(name, **argumente):
    antwort = server.bearbeite({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                                "params": {"name": name, "arguments": argumente}})
    ergebnis = antwort["result"]
    return ergebnis["content"][0]["text"], ergebnis["isError"]


class ProtokollTest(unittest.TestCase):
    def test_initialize_und_liste(self):
        a = server.bearbeite({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                              "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                                         "clientInfo": {"name": "t", "version": "1"}}})
        self.assertEqual(a["result"]["protocolVersion"], "2024-11-05")
        self.assertIn("tools", a["result"]["capabilities"])
        self.assertIsNone(server.bearbeite({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        liste = server.bearbeite({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        namen = {t["name"] for t in liste}
        self.assertIn("auswertung_lesen", namen)
        self.assertIn("szenario_entwurf_anlegen", namen)
        for t in liste:
            self.assertEqual(t["inputSchema"]["type"], "object")

    def test_unbekannte_methode_und_kaputtes_json(self):
        a = server.bearbeite({"jsonrpc": "2.0", "id": 3, "method": "gibtsnicht"})
        self.assertEqual(a["error"]["code"], -32601)
        aus = io.StringIO()
        server.lauf(io.StringIO("{kaputt\n"), aus)
        self.assertEqual(json.loads(aus.getvalue())["error"]["code"], -32700)

    def test_zeilenweise_ueber_stdio(self):
        eingabe = io.StringIO('{"jsonrpc":"2.0","id":1,"method":"ping"}\n\n'
                              '{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        aus = io.StringIO()
        server.lauf(eingabe, aus)
        zeilen = aus.getvalue().strip().split("\n")
        self.assertEqual(len(zeilen), 1)
        self.assertEqual(json.loads(zeilen[0]), {"jsonrpc": "2.0", "id": 1, "result": {}})


class WerkzeugTest(unittest.TestCase):
    def test_auswertung_lesen(self):
        with Datenordner():
            stand = Spielstand.lade("windows_server")
            stand.versuch_eintragen("srv-ad-konto-gesperrt", {
                "datum": "2026-11-04T10:00:00", "geloest": False, "hinweise": 2, "falsche_befehle": 1,
                "unbekannte_befehle": 0, "befehle": 4, "sekunden": 200, "falsch": [], "unbekannt": []})
            stand.speichere()
            text, fehler = rufe("auswertung_lesen", system="windows_server")
            self.assertFalse(fehler)
            self.assertIn("# Auswertung Windows Server", text)
            self.assertIn("Konto nach Urlaub gesperrt", text)
            roh, _ = rufe("auswertung_lesen", system="windows_server", format="json")
            self.assertEqual(json.loads(roh)["system"], "windows_server")
            _, fehler = rufe("auswertung_lesen", system="macos")
            self.assertTrue(fehler)

    def test_lesende_werkzeuge(self):
        with Datenordner():
            text, _ = rufe("systeme_uebersicht")
            self.assertIn("Linux Server", text)
            liste = json.loads(rufe("szenarien_auflisten", system="linux")[0])
            self.assertGreaterEqual(len(liste["szenarien"]), 15)
            self.assertIn("\"id\": \"win-dns-cache\"", rufe("szenario_lesen", id="win-dns-cache")[0])
            self.assertTrue(rufe("szenario_lesen", id="gibt-es-nicht")[1])
            self.assertIn("Pflichtfelder", rufe("szenario_format")[0])
            self.assertEqual(json.loads(rufe("spielstand_lesen", system="linux")[0])["system"], "linux")

    def test_entwurf_anlegen(self):
        with Datenordner() as ordner:
            entwurf = mini(id="mcp-entwurf", pruefstatus="bestaetigt")
            text, fehler = rufe("szenario_entwurf_anlegen", szenario=entwurf)
            self.assertFalse(fehler, text)
            datei = Path(ordner) / "szenarien" / "windows" / "mcp-entwurf.json"
            self.assertTrue(datei.exists())
            self.assertEqual(json.loads(datei.read_text(encoding="utf-8"))["pruefstatus"], "ungeprueft")
            text, fehler = rufe("szenario_entwurf_anlegen", szenario=entwurf)
            self.assertTrue(fehler)
            self.assertIn("schon", text)
            text, fehler = rufe("szenario_entwurf_anlegen", szenario=mini(id="win-dns-cache"))
            self.assertTrue(fehler)  # mitgeliefertes Szenario wird nicht überschrieben
            text, fehler = rufe("szenario_entwurf_anlegen", szenario=mini(id="mcp-kaputt", hinweise=["nur einer"]))
            self.assertTrue(fehler)
            self.assertIn("hinweise", text)
            text, fehler = rufe("szenario_entwurf_anlegen", szenario=mini(id="mcp-unloesbar", loesung=["Get-Service Testdienst"]))
            self.assertTrue(fehler)
            self.assertIn("Lösungsweg", text)


if __name__ == "__main__":
    unittest.main()
