"""Inhaltsregeln für alle mitgelieferten Szenarien (CLAUDE.md, „Unverhandelbar“)."""

import ipaddress
import json
import re
import unittest
from pathlib import Path

from n3xtbyt3.kern.szenario import pruefe_daten

WURZEL = Path(__file__).resolve().parents[1]
SZENARIEN = sorted((WURZEL / "daten" / "szenarien").glob("*/*.json"))
# Für die Regeln zu IP-Adressen und Mailadressen zählen auch Lektionen und Befehlsbücher.
ALLE_DATEN = SZENARIEN + sorted((WURZEL / "daten" / "grundkurs").glob("*/*.json")) \
    + sorted((WURZEL / "daten" / "befehlsbuch").glob("*.json"))
IP = re.compile(r"(?<![\d.])(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?![\d.])")

ERLAUBT = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # APIPA
]


# Versionsnummern, die wie IP-Adressen aussehen (Modulversion in der Ausgabe von Get-Command)
VERSIONEN = {"3.1.0.0"}


def _ist_maske_oder_sonder(adresse: ipaddress.IPv4Address) -> bool:
    text = str(adresse)
    if text == "0.0.0.0" or text.startswith("255.") or text in VERSIONEN:
        return True
    return False


class InhaltTest(unittest.TestCase):
    def test_es_gibt_genug_windows_szenarien(self):
        anzahl = len(list((WURZEL / "daten" / "szenarien" / "windows").glob("*.json")))
        self.assertGreaterEqual(anzahl, 10)

    def test_nur_private_ip_adressen(self):
        funde = []
        for datei in ALLE_DATEN:
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
        funde = [f"{d.name}: {m}" for d in ALLE_DATEN for m in mail.findall(d.read_text(encoding="utf-8"))
                 if not m.endswith(".internal")]  # erfundene Domäne firma.internal ist erlaubt
        self.assertEqual(funde, [])

    def test_vorlage_ist_gueltig(self):
        daten = json.loads((WURZEL / "vorlagen" / "szenario_vorlage.json").read_text(encoding="utf-8"))
        szenario, fehler = pruefe_daten(daten)
        self.assertEqual(fehler, [])
        self.assertEqual(szenario.id, "win-mein-fehler")

    def test_jedes_szenario_hat_eine_passende_lektion(self):
        """Grundkurs: „braucht: Lektion n“ – jede voraussetzung zeigt auf eine vorhandene Lektion."""
        from n3xtbyt3.kern import grundkurs
        kurse = grundkurs.alle_kurse()
        for datei in SZENARIEN:
            daten = json.loads(datei.read_text(encoding="utf-8"))
            with self.subTest(szenario=datei.name):
                self.assertIn("voraussetzung", daten)
                self.assertIsNotNone(grundkurs.finde_lektion(kurse, daten["voraussetzung"]))

    def test_lektionen_haben_quelle_und_pruefstatus(self):
        from n3xtbyt3.kern import grundkurs
        from n3xtbyt3.kern.systeme import REIHENFOLGE
        for sid in REIHENFOLGE:
            kurs = grundkurs.lade_kurs(sid)
            self.assertTrue(kurs.lektionen, f"Grundkurs {sid} fehlt")
            for l in kurs.lektionen:
                self.assertIn(l.pruefstatus, ("ungeprueft", "bestaetigt"))
                self.assertTrue(l.quelle and all(q.startswith("https://") for q in l.quelle), l.id)

    def test_claude_szenarien_sind_ungeprueft_oder_bestaetigt(self):
        for datei in SZENARIEN:
            daten = json.loads(datei.read_text(encoding="utf-8"))
            self.assertIn(daten["pruefstatus"], ("ungeprueft", "bestaetigt"), datei.name)


if __name__ == "__main__":
    unittest.main()
