import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from classes.digisign.CertificateManager import CertificateManager
from classes.digisign.Preferences import Preferences


class SigningUtilsTests(unittest.TestCase):
    def test_pkcs12_load_without_password_returns_placeholder_certificate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs_dir = Path(temp_dir)
            with patch.object(Preferences, 'PREFS_DIR', prefs_dir), patch.object(Preferences, 'PREFS_FILE', prefs_dir / 'preferences.json'):
                cert = CertificateManager.load_certificate_file("/tmp/example-cert.p12")

                self.assertIsNotNone(cert)
                self.assertEqual(cert.cert_path, "/tmp/example-cert.p12")
                self.assertEqual(cert.friendly_name, "")
                self.assertEqual(cert.subject, "")
                self.assertEqual(cert.issuer, "")
                self.assertEqual(cert.thumbprint, "")
                self.assertEqual(cert.valid_to, "")
                self.assertIsNone(cert.password)

    def test_pkcs12_load_without_password_uses_preferences_if_present(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs_dir = Path(temp_dir)
            prefs_file = prefs_dir / 'preferences.json'
            prefs_dir.mkdir(parents=True, exist_ok=True)
            prefs_file.write_text(json.dumps({
                "selected_certificate_subject": "CN=Test Cert",
                "selected_certificate_issuer": "CN=Test Issuer",
                "selected_certificate_thumbprint": "ABC123",
                "selected_certificate_valid_to": "2030-01-01",
                "selected_certificate_friendly_name": "Test Cert Friendly",
            }))

            with patch.object(Preferences, 'PREFS_DIR', prefs_dir), patch.object(Preferences, 'PREFS_FILE', prefs_file):
                cert = CertificateManager.load_certificate_file("/tmp/example-cert.p12")

                self.assertIsNotNone(cert)
                self.assertEqual(cert.cert_path, "/tmp/example-cert.p12")
                self.assertEqual(cert.friendly_name, "Test Cert Friendly")
                self.assertEqual(cert.subject, "CN=Test Cert")
                self.assertEqual(cert.issuer, "CN=Test Issuer")
                self.assertEqual(cert.thumbprint, "ABC123")
                self.assertEqual(cert.valid_to, "2030-01-01")
                self.assertIsNone(cert.password)


if __name__ == "__main__":
    unittest.main()
