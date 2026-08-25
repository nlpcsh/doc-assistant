import json
from os import path
from pathlib import Path
from typing import Optional, Dict, Any


class Preferences:
    """Manages application preferences (saved settings)."""

    PREFS_DIR = Path.home() / ".digisign"
    PREFS_FILE = PREFS_DIR / "preferences.json"

    @classmethod
    def _ensure_dir(self) -> None:
        """Ensure preferences directory exists."""
        self.PREFS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load(self) -> Dict[str, Any]:
        """Load preferences from disk."""
        self._ensure_dir()
        if self.PREFS_FILE.exists():
            try:
                with open(self.PREFS_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    @classmethod
    def save(self, prefs: Dict[str, Any]) -> None:
        """Save preferences to disk."""
        self._ensure_dir()
        try:
            with open(self.PREFS_FILE, "w") as f:
                json.dump(prefs, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save preferences: {e}")

    @classmethod
    def get_signature_image_path(self) -> Optional[str]:
        """Get the last used signature image path."""
        prefs = self.load()
        img_path = prefs.get("signature_image_path")
        # Validate that file still exists
        if img_path and path.isfile(img_path):
            return img_path
        return None

    @classmethod
    def set_signature_image_path(self, path: Optional[str]) -> None:
        """Save the signature image path."""
        prefs = self.load()
        prefs["signature_image_path"] = path
        self.save(prefs)

    @classmethod
    def get_selected_certificate_thumbprint(self) -> Optional[str]:
        """Get the last selected certificate thumbprint."""
        prefs = self.load()
        return prefs.get("selected_certificate_thumbprint")

    @classmethod
    def set_selected_certificate_thumbprint(self, thumbprint: Optional[str]) -> None:
        """Save the selected certificate thumbprint."""
        prefs = self.load()
        prefs["selected_certificate_thumbprint"] = thumbprint
        self.save(prefs)

    @classmethod
    def get_selected_certificate_friendly_name(self) -> Optional[str]:
        """Get the last selected certificate friendly name (fallback if thumbprint not found)."""
        prefs = self.load()
        return prefs.get("selected_certificate_friendly_name")

    @classmethod
    def set_selected_certificate_friendly_name(self, friendly_name: Optional[str]) -> None:
        """Save the selected certificate friendly name."""
        prefs = self.load()
        prefs["selected_certificate_friendly_name"] = friendly_name
        self.save(prefs)

    @classmethod
    def get_selected_certificate_subject(self) -> Optional[str]:
        """Get the last selected certificate subject."""
        prefs = self.load()
        return prefs.get("selected_certificate_subject")

    @classmethod
    def set_selected_certificate_subject(self, subject: Optional[str]) -> None:
        """Save the selected certificate subject."""
        prefs = self.load()
        prefs["selected_certificate_subject"] = subject
        self.save(prefs)

    @classmethod
    def get_selected_certificate_issuer(self) -> Optional[str]:
        """Get the last selected certificate issuer."""
        prefs = self.load()
        return prefs.get("selected_certificate_issuer")

    @classmethod
    def set_selected_certificate_issuer(self, issuer: Optional[str]) -> None:
        """Save the selected certificate issuer."""
        prefs = self.load()
        prefs["selected_certificate_issuer"] = issuer
        self.save(prefs)

    @classmethod
    def get_valid_to(self) -> Optional[str]:
        """Get the last selected certificate valid to date."""
        prefs = self.load()
        return prefs.get("selected_certificate_valid_to")

    @classmethod
    def set_valid_to(self, valid_to: Optional[str]) -> None:
        """Save the selected certificate valid to date."""
        prefs = self.load()
        prefs["selected_certificate_valid_to"] = valid_to
        self.save(prefs)
    
    @classmethod
    def get_selected_certificate_path(self) -> Optional[str]:
        """Get the last selected certificate file path."""
        prefs = self.load()
        crt_path = prefs.get("selected_certificate_path")
        if crt_path and path.isfile(crt_path):
            return crt_path
        return None

    @classmethod
    def set_selected_certificate_path(self, path: Optional[str]) -> None:
        """Save the selected certificate file path."""
        prefs = self.load()
        prefs["selected_certificate_path"] = path
        self.save(prefs)

    @classmethod
    def get_signature_declaration(self) -> Optional[str]:
        """Get the saved signature declaration."""
        prefs = self.load()
        return prefs.get("signature_declaration")

    @classmethod
    def set_signature_declaration(self, declaration: Optional[str]) -> None:
        """Save the signature declaration."""
        prefs = self.load()
        prefs["signature_declaration"] = declaration
        self.save(prefs)

    @classmethod
    def get_canvas_width(self) -> int:
        """Get the saved canvas width, or default to 680."""
        prefs = self.load()
        return prefs.get("canvas_width", 680)

    @classmethod
    def set_canvas_width(self, width: int) -> None:
        """Save the canvas width."""
        prefs = self.load()
        prefs["canvas_width"] = width
        self.save(prefs)

    @classmethod
    def get_canvas_height(self) -> int:
        """Get the saved canvas height, or default to 900."""
        prefs = self.load()
        return prefs.get("canvas_height", 900)

    @classmethod
    def set_canvas_height(self, height: int) -> None:
        """Save the canvas height."""
        prefs = self.load()
        prefs["canvas_height"] = height
        self.save(prefs)
