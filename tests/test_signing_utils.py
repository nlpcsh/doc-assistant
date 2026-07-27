import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from classes.digisign.CertificateManager import CertificateManager


class SigningUtilsTests(unittest.TestCase):
    def test_pkcs12_load_without_password_returns_placeholder_certificate(self):
        cert = CertificateManager.load_certificate_file("/tmp/example-cert.p12")

        self.assertIsNotNone(cert)
        self.assertEqual(cert.cert_path, "/tmp/example-cert.p12")
        self.assertEqual(cert.friendly_name, "example-cert")
        self.assertIsNone(cert.password)


if __name__ == "__main__":
    unittest.main()
