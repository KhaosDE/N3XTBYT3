"""Tests für Fehler aus der Bugsuche vom 07.11.2026 (jeder Test stellt einen gefundenen Fehler nach)."""

import unittest
from pathlib import Path
from unittest import mock

from n3xtbyt3.kern import auswertung, einstellungen, training
from n3xtbyt3.kern.spielstand import Spielstand
from n3xtbyt3.kern.szenario import lade_system, pruefe_daten

from tests.hilfen import Datenordner, mini


class SpielstandSchutzTest(unittest.TestCase):
    def test_gesperrte_datei_wird_nicht_ueberschrieben(self):
        with Datenordner() as ordner:
            stand = Spielstand("windows")
            stand.versuch_eintragen("win-dns-cache", {"geloest": True, "befehle": 3, "hinweise": 0})
            stand.speichere()
            datei = Path(ordner, "spielstand_windows.json")
            vorher = datei.read_text(encoding="utf-8")
            with mock.patch.object(Path, "read_text", side_effect=PermissionError("gesperrt")):
                gesperrt = Spielstand.lade("windows")
            self.assertTrue(gesperrt.nicht_speichern)
            self.assertIn("nicht lesen", gesperrt.warnung)
            gesperrt.versuch_eintragen("win-apipa", {"geloest": True, "befehle": 2, "hinweise": 0})
            with self.assertRaises(OSError):
                gesperrt.speichere()
            self.assertEqual(datei.read_text(encoding="utf-8"), vorher)  # nichts verloren
            self.assertEqual([p.name for p in Path(ordner).glob("*.defekt-*")], [])

    def test_falsche_zeichenkodierung_wird_gesichert(self):
        with Datenordner() as ordner:
            Path(ordner, "einstellungen.json").write_bytes(b'{"schriftgroesse": 24, "x": "\xe4"}')  # ANSI statt UTF-8
            werte = einstellungen.lade()  # stürzte vorher mit UnicodeDecodeError ab
            self.assertEqual(werte["schriftgroesse"], einstellungen.STANDARD["schriftgroesse"])
            self.assertEqual(len(list(Path(ordner).glob("einstellungen.defekt-*.json"))), 1)


class AuswertungTest(unittest.TestCase):
    def test_pipe_im_befehl_verschiebt_keine_spalten(self):
        with Datenordner():
            szenarien = lade_system("windows").szenarien
            stand = Spielstand("windows")
            karten = [k for k in training.sammle_karten(szenarien) if "|" in k.beispiel]
            self.assertTrue(karten)
            stand.kartei.befehl_ergebnis(karten[0].schluessel, "falsch")
            md = auswertung.als_markdown(auswertung.erstelle("windows", szenarien, stand))
            zeile = next(z for z in md.split("\n") if karten[0].beispiel.split("|")[0].strip() in z and z.startswith("|"))
            self.assertEqual(zeile.replace("\\|", "").count("|"), 6)

    def test_beispiele_fuer_falsch_und_unbekannt_getrennt(self):
        with Datenordner():
            szenarien = lade_system("windows").szenarien
            stand = Spielstand("windows")
            stand.versuch_eintragen(szenarien[0].id, {"befehle": 1, "falsch": ["shutdown /r /t 0"], "unbekannt": []})
            stand.versuch_eintragen(szenarien[1].id, {"befehle": 1, "falsch": [], "unbekannt": ["shutdown /a"]})
            a = auswertung.erstelle("windows", szenarien, stand)
            self.assertEqual(a["haeufige_fehler"]["falsch"][0]["beispiel"], "shutdown /r /t 0")
            self.assertEqual(a["haeufige_fehler"]["unbekannt"][0]["beispiel"], "shutdown /a")


class IdTest(unittest.TestCase):
    def test_zeilenumbruch_in_der_id(self):
        _, fehler = pruefe_daten(mini(id="test-mini\n"))
        self.assertTrue(any("„id“" in f for f in fehler))
        _, fehler = pruefe_daten(mini(voraussetzung="gk-win-konsole\n"))
        self.assertTrue(any("voraussetzung" in f for f in fehler))


class McpTest(unittest.TestCase):
    def test_szenario_lesen_nur_mit_id(self):
        from n3xtbyt3_mcp import server
        with Datenordner() as ordner:
            geheim = Path(ordner, "geheim.json")
            geheim.write_text('{"geheim": 1}', encoding="utf-8")
            for sid in (str(geheim)[:-5], "../../../../../../" + str(geheim)[1:-5]):
                antwort = server.bearbeite({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                            "params": {"name": "szenario_lesen", "arguments": {"id": sid}}})
                self.assertTrue(antwort["result"]["isError"], sid)
                self.assertNotIn("geheim", antwort["result"]["content"][0]["text"].split("„")[0])

    def test_params_kein_objekt(self):
        from n3xtbyt3_mcp import server
        for params in ([1], "x", 5):
            antwort = server.bearbeite({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": params})
            self.assertEqual(antwort["error"]["code"], -32602)
        antwort = server.bearbeite({"jsonrpc": "2.0", "id": 8, "method": "tools/call",
                                    "params": {"name": "systeme_uebersicht", "arguments": [1]}})
        self.assertEqual(antwort["error"]["code"], -32602)


if __name__ == "__main__":
    unittest.main()
