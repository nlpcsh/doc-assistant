import platform
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional, Tuple

from Helpers import Helpers
from ui.WidgetFactory import WidgetFactory


class SigningUIBuilder:
    def __init__(self, data_mgr, widget_factory: WidgetFactory):
        self.data_mgr = data_mgr
        self.labels = self.data_mgr.get_labels()
        self.factory = widget_factory

    def show_signature_preview(self, owner, pdf_paths):
        from classes.digisign.PdfSigner import PdfSigner

        x_offset = 30
        y_offset = 30
        next_x = 100
        next_y = 100

        if owner.preview_window and owner.preview_window.winfo_exists():
            try:
                next_x = owner.preview_window.winfo_rootx() + x_offset
                next_y = owner.preview_window.winfo_rooty() + y_offset
            except Exception:
                pass
            owner.preview_window.destroy()
            owner.preview_window = None

        for pdf_path in pdf_paths:
            owner.preview_pdf_path = pdf_path
            owner.selected_signature_rect = None

            geometry = f"1100x900+{next_x}+{next_y}"
            preview_window = self.factory.create_toplevel(owner.winfo_toplevel(), title=self.labels["signing"]["signing_title"], geometry=geometry)
            signer = PdfSigner(preview_window, self.labels)
            signer.preview_pdf_file(pdf_path)
            preview_window.focus_set()

            owner.preview_window = preview_window
            next_x += x_offset
            next_y += y_offset

    @staticmethod
    def build_toolbar(root: tk.Tk) -> tk.Frame:
        toolbar = tk.Frame(root)
        toolbar.pack(fill="x", padx=8, pady=8)
        return toolbar

    @staticmethod
    def build_buttons(toolbar: tk.Frame, callbacks: dict, labels: dict) -> dict:
        buttons = {}

        if platform.system() != "Linux":
            buttons["refresh_certs"] = tk.Button(
                toolbar,
                text=labels["signing"]["refresh_certs"],
                command=callbacks["load_certificates"],
            )
            buttons["refresh_certs"].pack(side="left", padx=(8, 0))

        if platform.system() != "Windows":
            buttons["load_cert_file"] = tk.Button(
                toolbar,
                text=labels["signing"]["load_cert_file"],
                command=callbacks["load_certificate_file"],
            )
            buttons["load_cert_file"].pack(side="left", padx=(8, 0))

        return buttons

    @staticmethod
    def build_canvas(content: tk.Frame, width: int = 680, height: int = 900) -> tk.Canvas:
        canvas = tk.Canvas(content, width=width, height=height, bg="#f0f0f0")
        canvas.pack(side="left", fill="both", expand=True)
        return canvas

    @staticmethod
    def build_sidebar(content: tk.Frame, callbacks: Optional[Dict[str, Any]] = None, labels: Optional[Dict[str, str]] = None) -> Tuple[tk.Frame, Dict[str, Any]]:
        if callbacks is None:
            callbacks = {}
        if labels is None:
            labels = {}

        sidebar = tk.Frame(content, padx=12)
        sidebar.pack(side="right", fill="y")

        components: Dict[str, Any] = {}

        if platform.system() != "Linux":
            tk.Label(
                sidebar,
                text=labels["signing"]["digital_certificate"],
                font=Helpers.get_ui_font(size_key="label_size", bold=True),
            ).pack(anchor="w", pady=(0, 6))
            components["cert_combo"] = ttk.Combobox(sidebar, state="readonly", width=25)
            components["cert_combo"].pack(fill="x", pady=(0, 6))

            components["cert_status_label"] = tk.Label(
                sidebar,
                text=labels["signing"]["no_certificate_selected"],
                wraplength=160,
                justify="left",
                fg="#666",
            )
            components["cert_status_label"].pack(anchor="w", pady=(0, 12))

        tk.Label(sidebar, text=labels["signing"]["signer"], font=Helpers.get_ui_font(size_key="label_size", bold=True)).pack(anchor="w")
        components["signer_name_label"] = tk.Label(
            sidebar,
            text="(From certificate)",
            wraplength=160,
            justify="left",
            fg="#666",
        )
        components["signer_name_label"].pack(anchor="w", pady=(0, 2))

        components["cert_validity_label"] = tk.Label(
            sidebar,
            text=labels["signing"]["no_certificate_selected"],
            wraplength=160,
            justify="left",
            fg="#666",
        )
        components["cert_validity_label"].pack(anchor="w", pady=(0, 12))

        tk.Label(
            sidebar,
            text=labels["signing"]["password_info"],
            font=Helpers.get_ui_font(size_key="label_size"),
            fg="#999",
        ).pack(anchor="w", pady=(0, 12))

        components["visual_only_var"] = tk.BooleanVar(value=False)
        tk.Checkbutton(
            sidebar,
            text=labels["signing"]["visual_signature_only"],
            variable=components["visual_only_var"],
            onvalue=True,
            offvalue=False,
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            sidebar,
            text=labels["signing"]["visual_signature_info"],
            font=Helpers.get_ui_font(size_key="label_size"),
            fg="#999",
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(sidebar, text=labels["signing"]["signature_statement"], font=Helpers.get_ui_font(size_key="label_size", bold=True)).pack(anchor="w")
        components["signature_declaration_var"] = tk.StringVar(value="I'm the author")
        components["signature_declaration_combo"] = ttk.Combobox(
            sidebar,
            state="readonly",
            width=25,
            textvariable=components["signature_declaration_var"],
            values=["I'm the author", "I reviewed this document"],
        )
        components["signature_declaration_combo"].pack(fill="x", pady=(0, 12))
        components["signature_declaration_combo"].current(0)

        load_sig_callback = callbacks.get("load_signature_image", lambda: None)
        tk.Button(sidebar, text=labels["signing"]["load_signature_image"], command=load_sig_callback).pack(fill="x")
        components["signature_image_label"] = tk.Label(
            sidebar,
            text=labels["signing"]["no_signature_image_loaded"],
            wraplength=160,
            justify="left",
        )
        components["signature_image_label"].pack(anchor="w", pady=(6, 12))

        tk.Label(sidebar, text=labels["signing"]["selection_display"], font=Helpers.get_ui_font(size_key="label_size", bold=True)).pack(anchor="w")
        components["selection_label"] = tk.Label(
            sidebar,
            text="x=0.0 y=0.0 w=0.0 h=0.0",
            justify="left",
        )
        components["selection_label"].pack(anchor="w", pady=(0, 12))

        tk.Label(sidebar, text=labels["signing"]["instructions"], font=Helpers.get_ui_font(size_key="label_size", bold=True)).pack(anchor="w")
        tk.Label(
            sidebar,
            text=labels["signing"]["instructions_text"],
            justify="left",
            fg="#333333",
        ).pack(anchor="w")

        sign_callback = callbacks.get("complete_signing", lambda: None)
        tk.Button(sidebar, text=labels["signing"]["signing_title"], command=sign_callback, bg="white", fg="blue").pack(
            fill="x", pady=(12, 0)
        )

        return sidebar, components

    @staticmethod
    def build_page_frame(root: tk.Tk) -> Tuple[tk.Frame, tk.Label, tk.Spinbox, tk.IntVar, tk.Label]:
        page_frame = tk.Frame(root)
        page_frame.pack(fill="x", padx=8)

        tk.Label(page_frame, text="Page:").pack(side="left")
        page_var = tk.IntVar(value=1)
        page_spin = tk.Spinbox(
            page_frame,
            from_=1,
            to=1,
            width=5,
            textvariable=page_var,
        )
        page_spin.pack(side="left", padx=(0, 12))

        info_label = tk.Label(page_frame, text="No file loaded")
        info_label.pack(side="left")

        return page_frame, page_spin, page_var, info_label
