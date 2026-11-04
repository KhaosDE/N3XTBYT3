"""Inhaltsregeln für alle mitgelieferten Szenarien (CLAUDE.md, „Unverhandelbar“)."""

import ipaddress
import json
import re
import unittest
from pathlib import Path

from n3xtbyt3.kern.szenario import pruefe_daten

WURZEL = Path(__file__).resolve().parents[1]
SZENARIEN = sorted((WURZEL / "daten" / "szenarien").glob("*/*.json"))
IP = re.compile(r"(?<![\d.])(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?![\d.])")

ERLAUBT = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # APIPA
]


def _ist_maske_oder_sonder(adresse: ipaddress.IPv4Address) -> bool:
    text = str(adresse)
    if text == "0.0.0.0" or text.startswith("255."):
        return True
    return False


class InhaltTest(unittest.TestCase):
    def test_es_gibt_genug_windows_szenarien(self):
        anzahl = len(list((WURZEL / "daten" / "szenarien" / "windows").glob("*.json")))
        self.assertGreaterEqual(anzahl, 10)

    def test_nur_private_ip_adressen(self):
        funde = []
        for datei in SZENARIEN:
            for treffer in IP.findall(datei.read_text(encoding="utf-8")):
                try:
                    adresse = ipaddress.ip_address(treffer)
                except ValueError:
                    continue  # z. B. Versionsnummern
                if _ist_maske_oder_sonder(adresse) or any(adresse in n for n in ERLAUBT):
                    continue
                funde.append(f"{datei.name}: {treffer}")
        self.assertEqual(funde, [], "Nicht-private IP-Adressen gefunden:\n" + "\n".join(funde))

    def test_keine_echten_mailadressen(self):
        mail = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
        funde = [f"{d.name}: {m}" for d in SZENARIEN for m in mail.findall(d.read_text(encoding="utf-8"))
                 if not m.endswith(".internal")]  # erfundene Domäne firma.internal ist erlaubt
        self.assertEqual(funde, [])

    def test_vorlage_ist_gueltig(self):
        daten = json.loads((WURZEL / "vorlagen" / "szenario_vorlage.json").read_text(encoding="utf-8"))
        szenario, fehler = pruefe_daten(daten)
        self.assertEqual(fehler, [])
        self.assertEqual(szenario.id, "win-mein-fehler")

    def test_claude_szenarien_sind_ungeprueft_oder_bestaetigt(self):
        for datei in SZENARIEN:
            daten = json.loads(datei.read_text(encoding="utf-8"))
            self.assertIn(daten["pruefstatus"], ("ungeprueft", "bestaetigt"), datei.name)


if __name__ == "__main__":
    unittest.main()
