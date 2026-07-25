import os
import platform
import subprocess
import json
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from classes.DataClasses import CertificateInfo


class CertificateManager:
    """Manages X.509 certificates from local files and the Windows certificate store."""

    CERT_FILE_DIR = Path.home() / ".docassistant" / "certs"

    @staticmethod
    def list_certificates() -> List[CertificateInfo]:
        certificates: List[CertificateInfo] = []
        certificates.extend(CertificateManager._get_windows_certificates())
        certificates.extend(CertificateManager._get_file_certificates(certificates))
        return certificates

    @staticmethod
    def _get_windows_certificates() -> List[CertificateInfo]:
        if platform.system() != "Windows":
            return []
        try:
            result = subprocess.run(
                ['powershell', '-WindowStyle Hidden', '-NoProfile', '-Command', CertificateManager._powershell_cert_query()],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0 or not result.stdout.strip():
                return []
            return CertificateManager._parse_windows_cert_output(result.stdout)
        except Exception:
            return []

    @staticmethod
    def _powershell_cert_query() -> str:
        return r"""
$certs = Get-ChildItem -Path Cert:\CurrentUser\My -ErrorAction SilentlyContinue
$result = @()
foreach ($cert in $certs) {
    $result += @{
        FriendlyName = $cert.FriendlyName
        Subject = $cert.Subject
        Thumbprint = $cert.Thumbprint
        NotAfter = $cert.NotAfter.ToString('o')
        Issuer = $cert.Issuer
    }
}
$result | ConvertTo-Json -Depth 2
"""

    @staticmethod
    def _parse_windows_cert_output(output: str) -> List[CertificateInfo]:
        try:
            data = json.loads(output.strip())
        except ValueError:
            return []

        if not isinstance(data, list):
            data = [data]

        certs: List[CertificateInfo] = []
        for item in data:
            thumbprint = item.get("Thumbprint")
            if not thumbprint:
                continue
            friendly_name = item.get("FriendlyName", "").strip() or item.get("Subject", "Unknown")
            certs.append(
                CertificateInfo(
                    subject=item.get("Subject", ""),
                    issuer=item.get("Issuer", ""),
                    thumbprint=thumbprint,
                    valid_to=item.get("NotAfter", "").split("T")[0],
                    friendly_name=friendly_name,
                )
            )
        return certs

    @staticmethod
    def _get_file_certificates(existing: List[CertificateInfo]) -> List[CertificateInfo]:
        try:
            paths = CertificateManager._get_certificate_files()
        except Exception:
            return []

        certs: List[CertificateInfo] = []
        existing_thumbprints = {c.thumbprint for c in existing}
        for path in paths:
            cert = CertificateManager._load_single_certificate(path)
            if cert and cert.thumbprint not in existing_thumbprints:
                certs.append(cert)
        return certs

    @staticmethod
    def _load_single_certificate(path: str) -> Optional[CertificateInfo]:
        try:
            ext = os.path.splitext(path)[1].lower()
            if ext in {'.pfx', '.p12'}:
                return None
            return CertificateManager.load_certificate_file(path)
        except Exception:
            return None

    @staticmethod
    def _load_certificate_from_file(cert_path: str) -> Optional[CertificateInfo]:
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            try:
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            except Exception:
                cert = x509.load_der_x509_certificate(cert_data, default_backend())

            subject = cert.subject.rfc4514_string()
            issuer = cert.issuer.rfc4514_string()
            thumbprint = cert.fingerprint(hashes.SHA1()).hex().upper()
            valid_to = cert.not_valid_after_utc.isoformat().split('T')[0]
            friendly_name = CertificateManager._extract_cn(subject)
            return CertificateInfo(
                subject=subject,
                issuer=issuer,
                thumbprint=thumbprint,
                valid_to=valid_to,
                friendly_name=friendly_name,
                cert_path=cert_path,
            )
        except Exception:
            return None

    @staticmethod
    def load_certificate_file(cert_path: str, password: Optional[str] = None) -> Optional[CertificateInfo]:
        ext = os.path.splitext(cert_path)[1].lower()
        if ext in {'.pfx', '.p12'}:
            return CertificateManager._load_pkcs12_certificate(cert_path, password=password)
        return CertificateManager._load_certificate_from_file(cert_path)

    @staticmethod
    def _load_pkcs12_certificate(cert_path: str, password: Optional[str] = None) -> Optional[CertificateInfo]:
        try:
            from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
            with open(cert_path, 'rb') as f:
                pfx_data = f.read()
            pfx_password = password.encode() if isinstance(password, str) else password
            key, cert, additional = load_key_and_certificates(pfx_data, pfx_password, default_backend())
            if cert is None:
                return None
            subject = cert.subject.rfc4514_string()
            issuer = cert.issuer.rfc4514_string()
            thumbprint = cert.fingerprint(hashes.SHA1()).hex().upper()
            valid_to = cert.not_valid_after_utc.isoformat().split('T')[0]
            friendly_name = CertificateManager._extract_cn(subject)
            return CertificateInfo(
                subject=subject,
                issuer=issuer,
                thumbprint=thumbprint,
                valid_to=valid_to,
                friendly_name=friendly_name,
                cert_path=cert_path,
                password=password,
            )
        except Exception:
            return None

    @staticmethod
    def _extract_cn(subject: str) -> str:
        parts = subject.split(',')
        for part in parts:
            part = part.strip()
            if part.startswith('CN='):
                return part[3:].strip()
        return subject[:50]

    @staticmethod
    def _get_certificate_files() -> List[str]:
        cert_paths = []
        try:
            CertificateManager.CERT_FILE_DIR.mkdir(parents=True, exist_ok=True)
            for filename in os.listdir(CertificateManager.CERT_FILE_DIR):
                if filename.lower().endswith(('.pfx', '.p12', '.pem', '.crt', '.cer')):
                    cert_paths.append(str(CertificateManager.CERT_FILE_DIR / filename))
        except Exception:
            pass
        return cert_paths

    @staticmethod
    def _sign_pdf_with_pkcs12_file(
        pfx_path: str,
        password: Optional[str],
        pdf_path: str,
        output_path: str,
        signer_name: Optional[str] = None,
    ) -> bool:
        try:
            from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
            from pyhanko.sign import signers
            from pyhanko.sign.signers import SimpleSigner

            signer = SimpleSigner.load_pkcs12(
                pfx_file=pfx_path,
                passphrase=password.encode() if password else None,
            )

            with open(pdf_path, 'rb') as inf, open(output_path, 'wb') as outf:
                writer = IncrementalPdfFileWriter(inf)
                metadata = signers.PdfSignatureMetadata(
                    field_name='Signature1',
                    name=signer_name,
                    reason=f'Signed by {signer_name or os.path.basename(pfx_path)}',
                )
                signers.sign_pdf(writer, metadata, signer=signer, output=outf)
            return True
        except Exception:
            return False

    @staticmethod
    def sign_pdf_with_certificate(
        pdf_path: str,
        thumbprint_or_path: str,
        output_path: str,
        password: Optional[str] = None,
        signer_name: Optional[str] = None,
    ) -> bool:
        if thumbprint_or_path and os.path.exists(thumbprint_or_path) and thumbprint_or_path.lower().endswith(('.pfx', '.p12')):
            return CertificateManager._sign_pdf_with_pkcs12_file(
                thumbprint_or_path,
                password,
                pdf_path,
                output_path,
                signer_name,
            )

        if platform.system() != "Windows":
            return False

        try:
            temp_dir = tempfile.gettempdir()
            pfx_path = os.path.join(temp_dir, f'docassistant_cert_{os.path.basename(thumbprint_or_path)[:8]}.pfx')
            password = password or os.urandom(12).hex()
            ps_command = f"""
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -ErrorAction SilentlyContinue | Where-Object {{$_.Thumbprint -eq '{thumbprint_or_path}'}}
if ($cert) {{
    try {{
        $pfxPassword = ConvertTo-SecureString -String '{password}' -AsPlainText -Force
        Export-PfxCertificate -Cert $cert -FilePath \"{pfx_path}\" -Password $pfxPassword -ChainOption BuildChain -ErrorAction Stop | Out-Null
        Write-Output 'SUCCESS'
    }} catch {{
        Write-Output \"FAILED: $($_.Exception.Message)\"
    }}
}} else {{
    Write-Output 'NOT_FOUND'
}}
"""
            result = subprocess.run(
                ['powershell', '-WindowStyle Hidden', '-NoProfile', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=25,
            )
            if result.returncode != 0 or 'SUCCESS' not in result.stdout:
                return False
            return CertificateManager._sign_pdf_with_pkcs12_file(pfx_path, password, pdf_path, output_path, signer_name)
        except Exception:
            return False
