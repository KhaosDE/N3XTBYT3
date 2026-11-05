"""Tests für das Selbst-Update – ohne echtes Netz (GitHub wird nachgebaut)."""

import hashlib
import re
import tempfile
import unittest
from pathlib import Path

from n3xtbyt3_update import aktualisierung as up

from tests.hilfen import Datenordner

WURZEL = Path(__file__).resolve().parents[1]
INHALT = b"neue Version"
SUMME = hashlib.sha256(INHALT).hexdigest()


def release(tag="build-30", exe_url=None, mit_summe=True):
    assets = [{"name": "N3XTBYT3.exe", "size": len(INHALT),
               "browser_download_url": exe_url or up.DOWNLOAD_PRAEFIX + tag + "/N3XTBYT3.exe"}]
    if mit_summe:
        assets.append({"name": "N3XTBYT3.exe.sha256", "size": 80,
                       "browser_download_url": up.DOWNLOAD_PRAEFIX + tag + "/N3XTBYT3.exe.sha256"})
    return {"tag_name": tag, "assets": assets}


class AngebotTest(unittest.TestCase):
    def test_nur_neuere_builds(self):
        self.assertIsNone(up.angebot_aus_release(release("build-30"), 30))
        self.assertIsNone(up.angebot_aus_release(release("build-29"), 30))
        self.assertIsNone(up.angebot_aus_release({"tag_name": "v1.0"}, 30))
        angebot = up.angebot_aus_release(release("build-31"), 30)
        self.assertEqual(angebot.build, 31)
        self.assertTrue(angebot.url.endswith("/build-31/N3XTBYT3.exe"))

    def test_fremde_adressen_und_fehlende_pruefsumme(self):
        with self.assertRaises(up.UpdateFehler):
            up.angebot_aus_release(release("build-31", exe_url="https://example.com/N3XTBYT3.exe"), 30)
        with self.assertRaises(up.UpdateFehler):
            up.angebot_aus_release(release("build-31", mit_summe=False), 30)
        with self.assertRaises(up.UpdateFehler):
            up._anfrage("https://example.com/")

    def test_pruefsumme_lesen(self):
        self.assertEqual(up.pruefsumme_lesen(f"{SUMME.upper()}  N3XTBYT3.exe\n"), SUMME)
        with self.assertRaises(up.UpdateFehler):
            up.pruefsumme_lesen("kaputt")


class AblaufTest(unittest.TestCase):
    def setUp(self):
        self._daten = Datenordner()
        self._daten.__enter__()
        self.tmp = tempfile.TemporaryDirectory()
        self.exe = Path(self.tmp.name) / "N3XTBYT3.exe"
        self.exe.write_bytes(b"alte Version")
        self.gestartet = []

    def tearDown(self):
        self.tmp.cleanup()
        self._daten.__exit__(None, None, None)

    def _holen_datei(self, inhalt=INHALT):
        def holen(url, ziel, fortschritt=None):
            if url.endswith(".sha256"):
                ziel.write_text(f"{SUMME}  N3XTBYT3.exe\n", encoding="utf-8")
            else:
                ziel.write_bytes(inhalt)
                if fortschritt:
                    fortschritt(len(inhalt), len(inhalt))
        return holen

    def test_aktualisiert_tauscht_und_startet(self):
        ok = up.aktualisieren(self.exe, 30, holen_json=lambda url: release("build-31"),
                              holen_datei=self._holen_datei(), starten=self.gestartet.append)
        self.assertTrue(ok)
        self.assertEqual(self.exe.read_bytes(), INHALT)
        self.assertEqual(self.exe.with_name("N3XTBYT3.exe.alt").read_bytes(), b"alte Version")
        self.assertEqual(self.gestartet, [self.exe])
        up.aufraeumen(self.exe)
        self.assertEqual(sorted(p.name for p in Path(self.tmp.name).iterdir()), ["N3XTBYT3.exe"])

    def test_aktuell_nichts_zu_tun(self):
        ok = up.aktualisieren(self.exe, 31, holen_json=lambda url: release("build-31"),
                              holen_datei=self._holen_datei(), starten=self.gestartet.append)
        self.assertFalse(ok)
        self.assertEqual(self.exe.read_bytes(), b"alte Version")

    def test_falsche_pruefsumme_laesst_alte_version_stehen(self):
        with self.assertRaises(up.UpdateFehler):
            up.aktualisieren(self.exe, 30, holen_json=lambda url: release("build-31"),
                             holen_datei=self._holen_datei(b"beschaedigt"), starten=self.gestartet.append)
        self.assertEqual(self.exe.read_bytes(), b"alte Version")
        self.assertEqual(self.gestartet, [])
        self.assertEqual(sorted(p.name for p in Path(self.tmp.name).iterdir()), ["N3XTBYT3.exe"])

    def test_beim_start_aus_dem_quelltext_kein_update(self):
        # Nicht als .exe gestartet: nie ins Netz
        self.assertFalse(up.eingeschaltet([]))
        self.assertFalse(up.beim_start(["--kein-update"]))


class EinstellungTest(unittest.TestCase):
    def test_auto_update_abschaltbar(self):
        from n3xtbyt3.kern import einstellungen
        with Datenordner():
            self.assertTrue(einstellungen.lade()["auto_update"])
            werte = einstellungen.lade()
            werte["auto_update"] = False
            einstellungen.speichere(werte)
            self.assertFalse(einstellungen.lade()["auto_update"])


class NetzNurImUpdateTest(unittest.TestCase):
    def test_update_spricht_nur_mit_den_releases_dieses_repositorys(self):
        adressen = set()
        for datei in (WURZEL / "n3xtbyt3_update").rglob("*.py"):
            adressen |= set(re.findall(r"https?://[^\s\"']+", datei.read_text(encoding="utf-8")))
        erlaubt = ("https://api.github.com/repos/KhaosDE/N3XTBYT3/releases/latest",
                   "https://github.com/KhaosDE/N3XTBYT3/releases/download/")
        self.assertTrue(adressen)
        self.assertTrue(all(a.startswith(erlaubt) for a in adressen), adressen)

    def test_lernprogramm_kennt_das_update_nicht(self):
        funde = [str(d) for paket in ("n3xtbyt3", "n3xtbyt3_mcp") for d in (WURZEL / paket).rglob("*.py")
                 if "n3xtbyt3_update" in d.read_text(encoding="utf-8")]
        self.assertEqual(funde, [])


class FensterTest(unittest.TestCase):
    def test_fortschrittsfenster(self):
        import os
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        try:
            import pygame  # noqa: F401
        except ImportError:  # pragma: no cover
            self.skipTest("pygame-ce nicht installiert")
        from n3xtbyt3_update.fenster import Fortschrittsfenster
        f = Fortschrittsfenster()
        self.assertTrue(f.zeige("Neue Version wird geladen: Build 30 → Build 31", 0.4))
        self.assertTrue(f.zeige("Build 31 wird gestartet …", None))
        f.schliessen()


if __name__ == "__main__":
    unittest.main()
