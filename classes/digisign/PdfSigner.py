from os import path, remove, replace
import tempfile
from typing import List, Optional, Tuple

from tkinter import Tk, Event, IntVar, Frame, BooleanVar, StringVar

from PIL import Image, ImageTk
try:
    import pymupdf as fitz
except ImportError:  # pragma: no cover - compatibility fallback
    import fitz
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.units import cm

from classes.digisign.DataClasses import SignaturePlacement, CertificateInfo
from classes.digisign.CertificateManager import CertificateManager
from classes.digisign.Preferences import Preferences
from classes.digisign.PdfPreviewRenderer import PdfPreviewRenderer
from classes.digisign.SignatureOverlay import SignatureOverlay
from ui.UIMgr import UIMgr

DEFAULT_WIDTH = 8 * cm
DEFAULT_HEIGHT = 3 * cm

class PdfSigner:
    """
    PDF signing part of the application.

    Manages PDF signing with digital certificates and visual signatures.
    Handles UI interactions, certificate management, and PDF operations.
    """

    def __init__(self, root: Tk, labels: dict):
        self.root = root
        self.labels = labels
        # Window title is managed by UIMgr

        # Initialize state
        self._initialize_state()

        # Build UI
        self._build_ui()
        self.preview_renderer = PdfPreviewRenderer(self.canvas, self.canvas_width, self.canvas_height)

        # Setup event handlers
        self._setup_event_handlers()

        # Load initial data
        self.load_certificates()
        self.load_preferences()

    def _initialize_state(self) -> None:
        """Initialize application state variables."""
        # Canvas dimensions from preferences
        self.canvas_width = Preferences.get_canvas_width()
        self.canvas_height = Preferences.get_canvas_height()

        # PDF state
        self.pdf_path: Optional[str] = None
        self.reader: Optional[PdfReader] = None
        self.page_size: Tuple[float, float] = (0.0, 0.0)
        self.selection: Optional[SignaturePlacement] = None
        self.drag_start: Optional[Tuple[float, float]] = None
        self.selection_rect_id: Optional[int] = None
        self.fitz_doc: Optional[fitz.Document] = None
        self.page_image_tk: Optional[ImageTk.PhotoImage] = None

        # Signature state
        self.signature_image_path: Optional[str] = None

        # Certificate state
        self.selected_certificate: Optional[CertificateInfo] = None
        self.available_certificates: List[CertificateInfo] = []
        self.selected_certificate_password: Optional[str] = None

        # Page navigation variables
        self.page_var = IntVar(value=1)

    def _build_ui(self) -> None:
        """Build the user interface."""
        # Toolbar
        toolbar = UIMgr.build_toolbar(self.root)
        self._toolbar_buttons = UIMgr.build_buttons(toolbar, {
            "load_certificates": self.load_certificates,
            "load_certificate_file": self.load_certificate_file,
        }, self.labels)

        # Page navigation
        self.page_frame, self.page_spin, self.page_var, self.info_label = UIMgr.build_page_frame(self.root)
        self.page_spin.config(command=self.on_page_change)

        # Main content area
        content = Frame(self.root)
        content.pack(fill="both", expand=True, padx=8, pady=8)

        # Canvas with dimensions from instance variables
        self.canvas = UIMgr.build_canvas(content, self.canvas_width, self.canvas_height)

        # Sidebar
        _, sidebar_components = UIMgr.build_sidebar(content, {
            "load_signature_image": self.load_signature_image,
            "complete_signing": self.complete_signing,
        }, labels=self.labels)
        self._setup_sidebar_components(sidebar_components)

    def _setup_sidebar_components(self, components: dict) -> None:
        """Extract and store sidebar components."""
        # Certificate UI components
        self.certificate_combo = components.get("cert_combo")
        self.certificate_status_label = components.get("cert_status_label")
        self.signer_name_label = components.get("signer_name_label")
        self.certificate_validity_label = components.get("cert_validity_label")

        # Signature UI components
        self.visual_only_var = components.get("visual_only_var", BooleanVar(value=False))
        self.signature_image_label = components.get("signature_image_label")
        self.selection_label = components.get("selection_label")

        # Signature declaration
        self.signature_declaration_var = components.get("signature_declaration_var", StringVar(value="I'm the author"))
        self.signature_declaration_combo = components.get("signature_declaration_combo")

    def _setup_event_handlers(self) -> None:
        """Bind event handlers to UI components."""
        if self.certificate_combo:
            self.certificate_combo.bind("<<ComboboxSelected>>", self._update_certificate_display)

        if self.signature_declaration_combo:
            self.signature_declaration_combo.bind("<<ComboboxSelected>>", self._on_signature_declaration_selected)

        # Canvas events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def load_certificates(self) -> None:
        """Load available certificates from the local certificate directory and Windows store."""
        try:
            all_certificates = CertificateManager.list_certificates()
            # Filter out expired certificates
            self.available_certificates = [cert for cert in all_certificates if not self._is_certificate_expired(cert)]
            cert_names = [cert.friendly_name for cert in self.available_certificates]

            if self.certificate_combo:
                self.certificate_combo['values'] = cert_names

                # Apply certificate preferences after loading
                self._apply_certificate_preferences()

                if not cert_names and self.certificate_status_label:
                        self.certificate_status_label.config(
                            text="No certificates found",
                            fg="#d9534f"
                        )
        except Exception as exc:
            if self.certificate_status_label:
                self.certificate_status_label.config(
                    text=f"Error loading certificates:\n{str(exc)[:50]}",
                    fg="#d9534f"
                )

    def load_certificate_file(self) -> None:
        """Allow the user to select a local certificate file for signing."""
        path = UIMgr.ask_open_filename(
            title=self.labels["signing"]["select_certificate"],
            filetypes=[
                ("PKCS#12 files", "*.pfx;*.p12"),
                ("Certificate files", "*.pem;*.crt;*.cer"),
                ("All files", "*.*")
            ]
        )
        if not path:
            return

        password = None
        if path.lower().endswith(('.pfx', '.p12')):
            password = UIMgr.ask_string(
                self.labels["signing"]["enter_password"],
                self.labels["signing"]["enter_password_description"],
                show="*"
            )

        cert_info = CertificateManager.load_certificate_file(path, password=password)

        if not cert_info:
            UIMgr.show_error(
                "Load certificate",
                f"Unable to load certificate file:\n{path}\n\n"
                f"Check:\n"
                f"- File format (must be .pfx/.p12 or PEM/DER)\n"
                f"- File password (if password-protected)\n"
                f"- File permissions and integrity\n\n"
                f"See the terminal/console for detailed error messages."
            )
            return

        cert_info.password = password
        self.available_certificates.append(cert_info)
        self.selected_certificate_password = None

        if self.certificate_combo:
            self.certificate_combo['values'] = [cert.friendly_name for cert in self.available_certificates]
            self.certificate_combo.current(len(self.available_certificates) - 1)
        self._update_certificate_display(cert_info)

    def _update_certificate_display(self, cert: Optional[CertificateInfo] = None) -> None:
        """Update the certificate display labels based on selected certificate"""
        cert = self._resolve_certificate(cert)
        self.selected_certificate = cert

        if not cert:
            self._clear_certificate_display()
            self._clear_certificate_preferences()
            return

        self._update_certificate_labels(cert)
        self._update_certificate_preferences(cert)

    def _resolve_certificate(self, cert: Optional[CertificateInfo]) -> Optional[CertificateInfo]:
        if cert:
            return cert

        if not self.certificate_combo:
            return self.selected_certificate

        index = self.certificate_combo.current()
        if 0 <= index < len(self.available_certificates):
            return self.available_certificates[index]

        return None

    def _update_certificate_labels(self, cert: CertificateInfo) -> None:
        status_text = f"Subject: {cert.friendly_name}\nValid to: {cert.valid_to}"

        if self.certificate_status_label:
            self.certificate_status_label.config(text=status_text, fg="#5cb85c")

        self.selected_certificate_password = None

        signer_name = self._extract_signer_name_from_cert(cert)
        if self.signer_name_label:
            self.signer_name_label.config(text=signer_name or "Unknown")

        if self.certificate_validity_label:
            valid_text = f"Valid to: {cert.valid_to}"
            color = "#d9534f" if self._is_certificate_expired(cert) else "#5cb85c"
            self.certificate_validity_label.config(text=valid_text, fg=color)

    def _clear_certificate_display(self) -> None:
        if self.certificate_status_label:
            self.certificate_status_label.config(text="No certificate selected", fg="#666")

        if self.signer_name_label:
            self.signer_name_label.config(text="(From certificate)")

        if self.certificate_validity_label:
            self.certificate_validity_label.config(text="", fg="#666")

    def _update_certificate_preferences(self, cert: CertificateInfo) -> None:
        Preferences.set_selected_certificate_thumbprint(cert.thumbprint)
        Preferences.set_selected_certificate_friendly_name(cert.friendly_name)
        Preferences.set_selected_certificate_subject(cert.subject)
        Preferences.set_selected_certificate_issuer(cert.issuer)
        Preferences.set_selected_certificate_path(cert.cert_path)
        Preferences.set_valid_to(cert.valid_to)

    def _clear_certificate_preferences(self) -> None:
        Preferences.set_selected_certificate_thumbprint(None)
        Preferences.set_selected_certificate_friendly_name(None)
        Preferences.set_selected_certificate_subject(None)
        Preferences.set_selected_certificate_issuer(None)
        Preferences.set_selected_certificate_path(None)
        Preferences.set_valid_to(None)

    def _extract_signer_name_from_cert(self, cert: Optional[CertificateInfo]) -> str:
        """Extract signer name from certificate subject"""
        if not cert:
            return "Signer"

        # Try to extract CN from subject
        subject = cert.subject
        parts = subject.split(',')
        for part in parts:
            part = part.strip()
            if part.startswith('CN='):
                name = part[3:].strip()
                # Remove quotes if present
                return name.strip('\'"')

        # Fallback to friendly name
        return cert.friendly_name.strip('\'"') if cert.friendly_name else "Signer"

    def _is_certificate_expired(self, cert: CertificateInfo) -> bool:
        """Check if a certificate has expired"""
        try:
            from datetime import datetime
            # Parse the valid_to date (ISO format with timezone)
            valid_to_str = cert.valid_to.split('.')[0]  # Remove microseconds and timezone
            valid_to = datetime.fromisoformat(valid_to_str)
            now = datetime.now()
            return now > valid_to
        except Exception:
            # If we can't parse, assume it's not expired
            return False

    def _apply_certificate_preferences(self) -> None:
        """Apply saved certificate preferences to the current certificate list"""
        index = self._find_preferred_certificate_index()

        if index is None:
            self._handle_no_certificates()
            return

        self._select_certificate_by_index(index)


    def _find_preferred_certificate_index(self) -> Optional[int]:
        certs = self.available_certificates
        if not certs:
            return None

        thumbprint = Preferences.get_selected_certificate_thumbprint()
        name = Preferences.get_selected_certificate_friendly_name()

        for i, cert in enumerate(certs):
            if thumbprint and cert.thumbprint == thumbprint:
                return i
            if name and cert.friendly_name == name:
                return i

        return 0  # fallback to first certificate

    def _select_certificate_by_index(self, index: int) -> None:
        cert = self.available_certificates[index]
        self.selected_certificate = cert

        if self.certificate_combo:
            self.certificate_combo.current(index)

        self._update_certificate_display(cert)

    def _handle_no_certificates(self) -> None:
        self.selected_certificate = None

        if self.certificate_status_label:
            self.certificate_status_label.config(
                text="No certificates available",
                fg="#666"
            )

        if self.signer_name_label:
            self.signer_name_label.config(text="(From certificate)")

    def load_preferences(self) -> None:
        """Load and apply saved preferences (signature image and certificate)."""
        self._load_signature_image()
        self._restore_certificate_from_preferences()
        self._apply_certificate_preferences()
        self._load_signature_declaration()

    def _load_signature_image(self) -> None:
        img_path = Preferences.get_signature_image_path()
        if img_path and path.isfile(img_path):
            self.signature_image_path = img_path
            self.update_signature_image_label()

    def _restore_certificate_from_preferences(self) -> None:
        crt_path = Preferences.get_selected_certificate_path()
        if not crt_path or not path.isfile(crt_path):
            return

        cert = self._build_certificate_info_from_path(crt_path)
        if cert:
            self._add_certificate_if_missing(cert)

    def _build_certificate_info_from_path(self, crt_path: str) -> Optional[CertificateInfo]:
        try:
            ext = path.splitext(crt_path)[1].lower()
            if ext in {'.pfx', '.p12'}:
                if Preferences.PREFS_FILE.exists():
                    cert_info = CertificateManager._load_certificate_info_from_preferences(crt_path)
                    self._update_certificate_labels(cert_info)
                    return cert_info
                return CertificateInfo(
                    subject="",
                    issuer="",
                    thumbprint="",
                    valid_to="N/A",
                    friendly_name="N/A",
                    cert_path=crt_path,
                    password=None,
                )

            return CertificateManager.load_certificate_file(crt_path)
        except Exception as exc:
            UIMgr.show_error("Error", f"Failed to get digital signature data:\n{exc}")
            return None

    def _prompt_for_certificate_password(self, crt_path: str) -> Optional[CertificateInfo]:
        while True:
            password = UIMgr.ask_string(
                self.labels["signing"]["enter_password"],
                self.labels["signing"]["enter_password_description"],
                show="*"
            )
            if password is None:
                return None

            cert = CertificateManager.load_certificate_file(crt_path, password=password)
            if cert:
                cert.password = password
                self.selected_certificate_password = None
                return cert

            UIMgr.show_error(
                self.labels["signing"]["enter_password"],
                self.labels["signing"]["invalid_password"]
            )

    def _add_certificate_if_missing(self, cert: CertificateInfo) -> None:
        if any(c.thumbprint == cert.thumbprint for c in self.available_certificates):
            return

        self.available_certificates.append(cert)

        if self.certificate_combo:
            self.certificate_combo['values'] = [
                c.friendly_name for c in self.available_certificates
            ]

    def _load_signature_declaration(self) -> None:
        declaration = Preferences.get_signature_declaration()
        if declaration in ["I'm the author", "I reviewed this document"]:
            self.signature_declaration_var.set(declaration)

    def _on_signature_declaration_selected(self, event: Optional[Event] = None) -> None:
        """Handle signature statement selection."""
        declaration = self.signature_declaration_var.get()
        Preferences.set_signature_declaration(declaration)

    def load_signature_image(self) -> None:
        path = UIMgr.ask_open_filename(title=self.labels["signing"]["load_signature_image"], filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All files", "*.*")])
        if not path:
            return
        self.signature_image_path = path
        self.update_signature_image_label()
        # Save preference
        Preferences.set_signature_image_path(path)

    def update_signature_image_label(self) -> None:
        if self.signature_image_path:
            self.signature_image_label.config(text=path.basename(self.signature_image_path))
        else:
            self.signature_image_label.config(text=self.labels["signing"]["no_signature_image_loaded"])

    def preview_pdf_file(self, pdf_path: str) -> None:
        try:
            reader = PdfReader(pdf_path)
        except Exception as exc:
            UIMgr.show_error(self.labels["signing"]["preview_pdf"], f"{self.labels['signing']['preview_error']}\n{exc}")
            return

        self.pdf_path = pdf_path
        self.reader = reader
        self.page_var.set(1)
        self.page_spin.config(to=len(reader.pages))

        if self.fitz_doc:
            try:
                self.fitz_doc.close()
            except Exception:
                pass
        try:
            self.fitz_doc = fitz.open(pdf_path)
        except Exception as exc:
            self.fitz_doc = None
            UIMgr.show_warning(self.labels["signing"]["preview_pdf"], f"{self.labels['signing']['preview_error']}\n{exc}")

        self.load_page(0)

    def on_page_change(self) -> None:
        if not self.reader:
            return
        page_index = max(1, min(len(self.reader.pages), self.page_var.get())) - 1
        self.load_page(page_index)

    def pdf_page_size(self, page) -> Tuple[float, float]:
        box = page.mediabox
        width = float(box.width)
        height = float(box.height)
        return width, height

    def pdf_to_canvas_coords(self, x: float, y: float, page_size: Tuple[float, float]) -> Tuple[float, float]:
        return self.preview_renderer.pdf_to_canvas_coords(x, y, page_size)

    def canvas_to_pdf_coords(self, x: float, y: float, page_size: Tuple[float, float]) -> Tuple[float, float]:
        return self.preview_renderer.canvas_to_pdf_coords(x, y, page_size)

    def load_page(self, page_index: int) -> None:
        if not self.reader:
            return
        page = self.reader.pages[page_index]
        self.page_size = self.pdf_page_size(page)
        self.selection = None
        self.drag_start = None
        self.selection_rect_id = None
        self.page_image_tk = None
        self.redraw_canvas()
        page_w, page_h = self.page_size
        self.info_label.config(text=f"{path.basename(self.pdf_path)} — page {page_index + 1}/{len(self.reader.pages)} — {page_w:.0f}x{page_h:.0f} pts")
        self.update_selection_label()
        self.update_signature_image_label()

    def get_page_preview_text(self, page) -> str:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if not text.strip():
            page_w, page_h = self.page_size
            return f"No text preview available for this page.\nPage size: {page_w:.0f} x {page_h:.0f} pts"

        lines = text.strip().splitlines()
        if len(lines) > 60:
            lines = lines[:60] + ["..."]
        return "\n".join(lines)

    def render_page_preview(self, page_index: int):
        return self.preview_renderer.render_page_preview(self.fitz_doc, page_index)

    def redraw_canvas(self) -> None:
        self.canvas.delete("all")
        if not self.pdf_path or not self.reader:
            self.canvas.create_text(self.canvas_width / 2, self.canvas_height / 2, text="Open a PDF to start", fill="#666")
            return

        page_w, page_h = self.page_size
        scale = min(self.canvas_width / page_w, self.canvas_height / page_h)
        disp_w = int(page_w * scale)
        disp_h = int(page_h * scale)
        x0 = (self.canvas_width - disp_w) / 2
        y0 = (self.canvas_height - disp_h) / 2
        x1 = x0 + disp_w
        y1 = y0 + disp_h

        self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="#444")
        preview_image = self.render_page_preview(self.page_var.get() - 1)
        if preview_image:
            preview_image = preview_image.resize((disp_w, disp_h), Image.LANCZOS)
            self.page_image_tk = ImageTk.PhotoImage(preview_image)
            self.canvas.create_image(x0, y0, anchor="nw", image=self.page_image_tk)
        else:
            preview_page = self.reader.pages[self.page_var.get() - 1]
            preview_text = self.get_page_preview_text(preview_page)
            self.canvas.create_text(
                x0 + 10,
                y0 + 10,
                text=preview_text,
                anchor="nw",
                fill="#222",
                font=("Courier", 9),
                width=disp_w - 20,
            )

        if self.selection:
            sel_x0, sel_y0 = self.pdf_to_canvas_coords(self.selection.x, self.selection.y + self.selection.height, self.page_size)
            sel_x1, sel_y1 = self.pdf_to_canvas_coords(self.selection.x + self.selection.width, self.selection.y, self.page_size)
            self.canvas.create_rectangle(sel_x0, sel_y0, sel_x1, sel_y1, outline="#007bff", width=2)

    def on_mouse_down(self, event: Event) -> None:
        if not self.pdf_path:
            return
        self.drag_start = (event.x, event.y)
        if self.selection_rect_id is not None:
            self.canvas.delete(self.selection_rect_id)
            self.selection_rect_id = None

    def on_mouse_drag(self, event: Event) -> None:
        if not self.drag_start:
            return
        x0, y0 = self.drag_start
        x1, y1 = event.x, event.y
        if self.selection_rect_id is not None:
            self.canvas.delete(self.selection_rect_id)
        self.selection_rect_id = self.canvas.create_rectangle(x0, y0, x1, y1, outline="#007bff", width=2)

    def on_mouse_up(self, event: Event) -> None:
        if not self.drag_start or not self.reader:
            return
        x0, y0 = self.drag_start
        x1, y1 = event.x, event.y
        self.drag_start = None
        if abs(x1 - x0) < 10 or abs(y1 - y0) < 10:
            return

        left = min(x0, x1)
        right = max(x0, x1)
        top = min(y0, y1)
        bottom = max(y0, y1)

        pdf_x, pdf_top = self.canvas_to_pdf_coords(left, top, self.page_size)
        pdf_right, pdf_bottom = self.canvas_to_pdf_coords(right, bottom, self.page_size)
        width = abs(pdf_right - pdf_x)
        height = abs(pdf_top - pdf_bottom)
        y = min(pdf_top, pdf_bottom)

        page_index = self.page_var.get() - 1
        self.selection = SignaturePlacement(page_number=page_index, x=pdf_x, y=y, width=width, height=height)
        self.update_selection_label()
        self.redraw_canvas()

    def update_selection_label(self) -> None:
        if not self.selection:
            self.selection_label.config(text="x=0.0 y=0.0 w=0.0 h=0.0")
            return
        self.selection_label.config(text=f"x={self.selection.x:.1f} y={self.selection.y:.1f} w={self.selection.width:.1f} h={self.selection.height:.1f}")

    def complete_signing(self) -> None:
        is_visual_only = self.visual_only_var.get()
        if not self._validate_signing_request(is_visual_only):
            return

        certificate_result = self._prepare_certificate_for_signing(is_visual_only)
        if certificate_result is None:
            return
        certificate_to_use, cert_password = certificate_result

        page_w, page_h = self.pdf_page_size(self.reader.pages[self.selection.page_number])

        overlay_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        overlay_path = overlay_pdf.name
        overlay_pdf.close()

        try:
            output_pdf, signing_succeeded, signer_name = self._create_signed_pdf(
                overlay_path, page_w, page_h, certificate_to_use, cert_password, is_visual_only
            )

            # If visual_only is not checked and digital signing failed, don't proceed
            if not is_visual_only and not signing_succeeded:
                if path.exists(output_pdf):
                    remove(output_pdf)
                UIMgr.show_error(self.labels["signing"]["signing_title"], self.labels["signing"]["digital_signature_failed"])
                return

            self.preview_pdf_file(output_pdf)

            self._show_signing_success(output_pdf, signer_name, is_visual_only)
        except Exception as exc:
            UIMgr.show_error(self.labels["signing"]["signing_title"], f"{self.labels['signing']['signing_error']}\n{exc}")
        finally:
            try:
                remove(overlay_path)
            except OSError:
                pass

    def _validate_signing_request(self, is_visual_only: bool) -> bool:
        if not self.pdf_path or not self.reader:
            message = self.labels["signing"]["no_pdf_loaded"]
        elif not self.selection:
            message = self.labels["signing"]["draw_signature_box"]
        elif not self.selected_certificate and not is_visual_only:
            message = self.labels["signing"]["select_certificate"]
        else:
            return True

        UIMgr.show_warning(self.labels["signing"]["signing_title"], message)
        return False

    def _prepare_certificate_for_signing(
        self, is_visual_only: bool
    ) -> Optional[Tuple[Optional[CertificateInfo], Optional[str]]]:
        if is_visual_only or not self.selected_certificate:
            return None, None

        certificate = self.selected_certificate
        if not certificate.cert_path or not certificate.cert_path.lower().endswith(('.pfx', '.p12')):
            return certificate, None

        cert_password = UIMgr.ask_string(
            self.labels["signing"]["enter_password"],
            self.labels["signing"]["enter_password_description"],
            show="*"
        )
        if cert_password is None:
            UIMgr.show_warning(
                self.labels["signing"]["signing_title"],
                self.labels["signing"]["signing_cancelled"]
            )
            return None

        actual_certificate = CertificateManager.load_certificate_file(
            certificate.cert_path, password=cert_password
        )
        if actual_certificate is None:
            UIMgr.show_error(
                self.labels["signing"]["signing_title"],
                self.labels["signing"]["invalid_password"]
            )
            return None

        actual_certificate.password = cert_password
        self.selected_certificate = actual_certificate
        self._replace_selected_certificate_in_list(actual_certificate)
        self._update_certificate_preferences(actual_certificate)
        self._update_certificate_labels(actual_certificate)
        return actual_certificate, cert_password

    def _create_signed_pdf(
        self,
        overlay_path: str,
        page_width: float,
        page_height: float,
        certificate: Optional[CertificateInfo],
        cert_password: Optional[str],
        is_visual_only: bool,
    ) -> Tuple[str, bool, str]:
        signature_declaration = self.signature_declaration_var.get()
        signer_name = (
            "Visual Signature"
            if is_visual_only
            else self._extract_signer_name_from_cert(self.selected_certificate)
        )
        self.create_signature_overlay(
            self.selection,
            signer_name,
            signature_declaration,
            overlay_path,
            page_width,
            page_height,
            signature_image_path=self.signature_image_path,
            visual_only=is_visual_only
        )
        output_pdf = path.splitext(self.pdf_path)[0] + "_signed.pdf"
        signing_succeeded = self.merge_overlay(
            self.pdf_path,
            overlay_path,
            self.selection,
            output_pdf,
            certificate=certificate,
            password=cert_password,
            signer_name=signer_name
        )
        return output_pdf, signing_succeeded, signer_name

    def _show_signing_success(
        self, output_pdf: str, signer_name: str, is_visual_only: bool
    ) -> None:
        if is_visual_only:
            message = (
                f"{self.labels['signing']['pdf_signed_visual']}\n{output_pdf}\n\n"
                f"{self.labels['signing']['type']}: "
                f"{self.labels['signing']['visual_signature_only']}"
            )
        else:
            message = (
                f"{self.labels['signing']['pdf_signed_digital']}\n{output_pdf}\n\n"
                f"{self.labels['signing']['certificate']}: {self.selected_certificate.issuer}\n"
                f"{self.labels['signing']['signer']}: {signer_name}"
            )
        UIMgr.show_info(self.labels["signing"]["signing_title"], message)

    @staticmethod
    def create_signature_overlay(
        placement: SignaturePlacement,
        signer_name: str,
        signature_type: str,
        output_path: str,
        page_width: float,
        page_height: float,
        signature_image_path: Optional[str] = None,
        visual_only: bool = False,
    ) -> None:
        SignatureOverlay.create(
            placement=placement,
            signer_name=signer_name,
            signature_type=signature_type,
            output_path=output_path,
            page_width=page_width,
            page_height=page_height,
            signature_image_path=signature_image_path,
            visual_only=visual_only,
        )

    def _replace_selected_certificate_in_list(self, actual_certificate: CertificateInfo) -> None:
        for index, cert in enumerate(self.available_certificates):
            if cert.cert_path == actual_certificate.cert_path:
                self.available_certificates[index] = actual_certificate
                break

        if self.certificate_combo:
            self.certificate_combo['values'] = [c.friendly_name for c in self.available_certificates]
            current_index = next((i for i, c in enumerate(self.available_certificates) if c.cert_path == actual_certificate.cert_path), None)
            if current_index is not None:
                self.certificate_combo.current(current_index)

    @staticmethod
    def merge_overlay(
        pdf_path: str,
        overlay_path: str,
        placement: SignaturePlacement,
        output_pdf: str,
        certificate: Optional[CertificateInfo] = None,
        password: Optional[str] = None,
        signer_name: Optional[str] = None
    ) -> bool:
        """Merge overlay with PDF and add digital signature

        Returns True if digital signing succeeded (or was not attempted), False if it failed
        """
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        overlay_reader = PdfReader(overlay_path)
        overlay_page = overlay_reader.pages[0]

        for index, page in enumerate(reader.pages):
            if index == placement.page_number:
                page.merge_page(overlay_page)
            writer.add_page(page)

        # Write the PDF with visual signature
        with open(output_pdf, "wb") as out_file:
            writer.write(out_file)

        # Add digital signature if certificate is provided
        if certificate:
            return PdfSigner._add_digital_signature(output_pdf, certificate, placement, password, signer_name)

        # No certificate provided, so visual-only signing is successful
        return True

    @staticmethod
    def _add_digital_signature(
        pdf_path: str,
        certificate: CertificateInfo,
        placement: SignaturePlacement,
        password: Optional[str] = None,
        signer_name: Optional[str] = None
    ) -> bool:
        """
        Add digital signature to PDF using X.509 certificate from Windows store

        Returns True if signing succeeded, False otherwise
        """
        try:
            temp_signed = pdf_path + ".temp"

            # Use CertificateManager to try real cryptographic signing first
            from classes.digisign.CertificateManager import CertificateManager
            success = CertificateManager.sign_pdf_with_certificate(
                pdf_path,
                certificate.cert_path if certificate.cert_path else certificate.thumbprint,
                temp_signed,
                password=password,
                signer_name=signer_name
            )

            if success and path.exists(temp_signed):
                replace(temp_signed, pdf_path)
                print("✓ Digital signature added successfully")
                return True

            return False

        except Exception as e:
            print(f"✗ Digital signature error: {e}")
            return False
