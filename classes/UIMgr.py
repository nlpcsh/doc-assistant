import tkinter as tk
import platform
from os import path
from tkinter import END, ttk, messagebox, filedialog, MULTIPLE, simpledialog
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from tkcalendar import Calendar

class UIMgr:
    def __init__(self, data_mgr):
        self.data_mgr = data_mgr
        self.labels = self.data_mgr.get_labels()

    def create_main_window(self, root):
        root.title(self.labels["app_title"])
        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill="both")
        return notebook

    def build_app_tabs(self, notebook):
        from classes.tabs.BusinessTripTab import BusinessTripTab
        from classes.tabs.CivilContractTab import CivilContractTab

        notebook.add(
            BusinessTripTab(notebook, self.data_mgr),
            text=self.labels["tabs"]["business_trip"],
        )
        notebook.add(
            CivilContractTab(notebook, self.data_mgr),
            text=self.labels["tabs"]["civil_contract"],
        )

    def initialize_document_container(self, owner):
        owner.container = ttk.Frame(owner, padding="20")
        owner.container.pack(fill="both", expand=True)

        owner.input_fields = []
        owner.progress = ttk.Progressbar(owner.container, orient="horizontal", length=200, mode="determinate")
        owner.status_label = ttk.Label(owner.container, text="")
        owner.preview_window = None
        owner.preview_canvas = None
        owner.preview_photo = None
        owner.preview_pdf_path = None
        owner.preview_page_width = None
        owner.preview_page_height = None
        owner.preview_scale = 1.0
        owner.preview_rect = None
        owner.selected_signature_rect = None

    def add_tab_title(self, owner, label_key, font=("Arial", 12, "bold")):
        ttk.Label(owner.container, text=self.labels["tabs"][label_key], font=font).pack(pady=10)

    def add_field(self, owner, label_key, show_by_default=True, initial_value="", width=30):
        field_frame = tk.Frame(owner.container)

        ttk.Label(field_frame, text=self.labels["fields"][label_key]).pack(side="left", padx=(0, 10))
        entry = ttk.Entry(field_frame, width=width)
        entry.configure(font=("Arial", 10))
        entry.pack(side="left")

        if initial_value:
            entry.insert(0, initial_value)

        if show_by_default:
            field_frame.pack(fill="x", padx=10, pady=5)
        else:
            field_frame.pack_forget()

        owner.input_fields.append((label_key, field_frame, entry))
        return entry

    def add_text_field(self, owner, label_key, height=4, width=40):
        field_frame = tk.Frame(owner.container)

        ttk.Label(field_frame, text=self.labels["fields"][label_key]).pack(anchor="w")
        text_widget = tk.Text(field_frame, height=height, width=width, wrap="word")
        text_widget.configure(font=("Arial", 10))
        text_widget.pack(fill="x")

        field_frame.pack(fill="x", padx=10, pady=5)

        owner.input_fields.append((label_key, field_frame, text_widget))
        return text_widget

    def add_checkbox_field(self, owner, label_key, checkbox_text, default_value="", show_by_default=False, width=20):
        field_frame = tk.Frame(owner.container)

        checkbox_var = tk.BooleanVar(value=show_by_default)
        ttk.Checkbutton(field_frame, text=checkbox_text, variable=checkbox_var).pack(side="left", padx=(0, 10))

        entry = ttk.Entry(field_frame, width=width)
        entry.configure(font=("Arial", 10))

        def toggle_visibility():
            if checkbox_var.get():
                entry.pack(side="left", padx=(5, 0))
                entry.delete(0, END)
                entry.insert(0, default_value)
            else:
                entry.pack_forget()
                entry.insert(0, "")

        checkbox_var.trace_add("write", lambda *args: toggle_visibility())

        field_frame.pack(fill="x", padx=10, pady=5)
        if show_by_default:
            entry.pack(side="left", padx=(5, 0))
        else:
            entry.pack_forget()

        owner.input_fields.append((label_key, field_frame, entry))
        return entry

    def add_checkbox_multi(self, owner, checkbox_text, options, parent=None):
        if parent is None:
            parent = owner.container
        var = tk.BooleanVar()
        checkbox = ttk.Checkbutton(parent, text=checkbox_text, variable=var)
        checkbox.pack(anchor="w", padx=10, pady=5)

        height = min(len(options), 10)
        listbox = tk.Listbox(parent, selectmode=MULTIPLE, height=height, exportselection=0)
        for option in options:
            listbox.insert(END, option)
        listbox.pack_forget()

        def toggle():
            if var.get():
                listbox.pack(after=checkbox, padx=10, pady=5)
            else:
                listbox.pack_forget()

        var.trace_add("write", lambda *args: toggle())
        return var, listbox

    def add_date_field(self, owner, label_key, preselect_today=False, min_date_from=None, width=30):
        ttk.Label(owner.container, text=self.labels["fields"][label_key]).pack(anchor="w")

        date_frame = tk.Frame(owner.container)
        date_frame.pack(pady=5, padx=5, fill="x")

        date_entry = ttk.Entry(date_frame, width=width)
        date_entry.pack(side="left", padx=5)

        if preselect_today:
            today = datetime.today()
            date_entry.insert(0, today.strftime("%d/%m/%Y"))

        def open_calendar():
            cal_window = self.create_toplevel(owner.winfo_toplevel(), title=self.labels["fields"][label_key])

            mindate = None
            if min_date_from:
                try:
                    min_date_str = min_date_from.get()
                    if min_date_str:
                        mindate = datetime.strptime(min_date_str, "%d/%m/%Y").date()
                except (ValueError, AttributeError):
                    pass

            def select_date():
                selected_date = calendar.get_date()
                date_entry.delete(0, END)
                date_entry.insert(0, selected_date)
                cal_window.destroy()

            today = datetime.today()
            calendar = Calendar(
                cal_window,
                selectmode="day",
                year=today.year,
                month=today.month,
                day=today.day,
                background="darkblue",
                foreground="white",
                date_pattern="dd/mm/yyyy",
                mindate=mindate,
            )
            calendar.pack(pady=10, padx=10)
            ttk.Button(cal_window, text="Select", command=select_date).pack(pady=5)
            cal_window.grab_set()

        ttk.Button(date_frame, text="📅", command=open_calendar, width=3).pack(side="left", padx=2)
        return date_entry

    def add_common_buttons(self, owner, gen_label_key):
        if path.exists(owner.signature_path + "sig.png"):
            owner.sig_path = owner.signature_path + "sig.png"
        else:
            ttk.Button(owner.container, text=self.labels["buttons"]["select_sig"], command=owner.get_signature).pack(pady=10)

        owner.gen_btn = ttk.Button(owner.container, text=self.labels["buttons"][gen_label_key], command=owner.start_generation)
        owner.gen_btn.pack(pady=20)

    def add_dropdown(self, owner, label_key, options):
        ttk.Label(owner.container, text=self.labels["fields"][label_key]).pack(anchor="w")
        combo = ttk.Combobox(owner.container, values=options, state="readonly", width=37)
        combo.pack(pady=5)
        if options:
            combo.current(0)
        return combo

    def add_multiselect(self, owner, label_key, options, height=10):
        ttk.Label(owner.container, text=self.labels["fields"][label_key]).pack(anchor="w")
        listbox_height = min(max(len(options), 1), height)
        listbox = tk.Listbox(owner.container, selectmode=MULTIPLE, height=listbox_height, exportselection=0)
        for option in options:
            listbox.insert(END, option)
        listbox.pack(pady=5, padx=10, fill="x")
        return listbox

    def start_generation(self, owner):
        owner.gen_btn.config(state="disabled")
        owner.progress.pack(pady=5)
        owner.status_label.pack()

    def reset_generation_ui(self, owner):
        owner.gen_btn.config(state="normal")
        owner.progress.pack_forget()
        owner.status_label.config(text="")

    def show_signature_preview(self, owner, pdf_paths):
        from classes.digisign.PdfSigner import PdfSigner

        # Open a separate signer window for each PDF path.
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
            preview_window = self.create_toplevel(owner.winfo_toplevel(), title="Sign PDF", geometry=geometry)
            signer = PdfSigner(preview_window)
            signer.preview_pdf_file(pdf_path)
            preview_window.grab_set()

            owner.preview_window = preview_window
            next_x += x_offset
            next_y += y_offset

    def create_toplevel(self, parent, title: str = "", geometry: Optional[str] = None):
        """Create a configured Toplevel window."""
        top = tk.Toplevel(parent)
        if title:
            top.title(title)
        if geometry:
            top.geometry(geometry)
        top.transient(parent)
        return top

    @staticmethod
    def set_window_title(window, title: str):
        try:
            window.title(title)
        except Exception:
            pass

    @staticmethod
    def build_page_frame(root: tk.Tk) -> Tuple[tk.Frame, tk.Label, tk.Spinbox, tk.IntVar, tk.Label]:
        """Create the page navigation frame."""
        page_frame = tk.Frame(root)
        page_frame.pack(fill="x", padx=8)

        tk.Label(page_frame, text="Page:").pack(side="left")
        page_var = tk.IntVar(value=1)
        page_spin = tk.Spinbox(
            page_frame,
            from_=1,
            to=1,
            width=5,
            textvariable=page_var
        )
        page_spin.pack(side="left", padx=(0, 12))

        info_label = tk.Label(page_frame, text="No file loaded")
        info_label.pack(side="left")

        return page_frame, page_spin, page_var, info_label

    # Dialog wrappers to centralize UI interactions
    @staticmethod
    def ask_open_filename(title: str = "Open File", filetypes=None, initialdir: Optional[str] = None) -> str:
        if filetypes is None:
            filetypes = [("All files", "*")]
        return filedialog.askopenfilename(title=title, filetypes=filetypes, initialdir=initialdir)

    @staticmethod
    def ask_string(title: str, prompt: str, show: Optional[str] = None) -> Optional[str]:
        return simpledialog.askstring(title, prompt, show=show)

    @staticmethod
    def show_error(title: str, message: str) -> None:
        messagebox.showerror(title, message)

    @staticmethod
    def show_warning(title: str, message: str) -> None:
        messagebox.showwarning(title, message)

    @staticmethod
    def show_info(title: str, message: str) -> None:
        messagebox.showinfo(title, message)

    @staticmethod
    def build_toolbar(root: tk.Tk) -> tk.Frame:
        """Create the top toolbar with PDF and certificate buttons."""
        toolbar = tk.Frame(root)
        toolbar.pack(fill="x", padx=8, pady=8)
        return toolbar

    @staticmethod
    def build_buttons(toolbar: tk.Frame, callbacks: dict) -> dict:
        """Create toolbar buttons with provided callbacks."""
        buttons = {}

        if platform.system() != "Linux":
            buttons["refresh_certs"] = tk.Button(
                toolbar,
                text="Refresh Certificates",
                command=callbacks["load_certificates"]
            )
            buttons["refresh_certs"].pack(side="left", padx=(8, 0))

        if platform.system() != "Windows":
            buttons["load_cert_file"] = tk.Button(
                toolbar,
                text="Load certificate file",
                command=callbacks["load_certificate_file"]
            )
            buttons["load_cert_file"].pack(side="left", padx=(8, 0))

        return buttons

    @staticmethod
    def build_canvas(content: tk.Frame, width: int = 680, height: int = 900) -> tk.Canvas:
        """Create the PDF preview canvas."""
        canvas = tk.Canvas(content, width=width, height=height, bg="#f0f0f0")
        canvas.pack(side="left", fill="both", expand=True)
        return canvas

    @staticmethod
    def build_sidebar(content: tk.Frame, callbacks: Optional[Dict[str, Any]] = None) -> Tuple[tk.Frame, Dict[str, Any]]:
        """Create the right sidebar with certificate and signing options."""
        if callbacks is None:
            callbacks = {}

        sidebar = tk.Frame(content, padx=12)
        sidebar.pack(side="right", fill="y")

        components = {}

        # Certificate section (platform-specific)
        if platform.system() != "Linux":
            tk.Label(sidebar, text="Digital Certificate:", font=("TkDefaultFont", 10, "bold")).pack(
                anchor="w", pady=(0, 6)
            )
            components["cert_combo"] = ttk.Combobox(sidebar, state="readonly", width=25)
            components["cert_combo"].pack(fill="x", pady=(0, 6))

            components["cert_status_label"] = tk.Label(
                sidebar,
                text="No certificate selected",
                wraplength=160,
                justify="left",
                fg="#666"
            )
            components["cert_status_label"].pack(anchor="w", pady=(0, 12))

        # Signer name info
        tk.Label(sidebar, text="Signer name:").pack(anchor="w")
        components["signer_name_label"] = tk.Label(
            sidebar,
            text="(From certificate)",
            wraplength=160,
            justify="left",
            fg="#666"
        )
        components["signer_name_label"].pack(anchor="w", pady=(0, 2))

        components["cert_validity_label"] = tk.Label(
            sidebar,
            text="",
            wraplength=160,
            justify="left",
            fg="#666"
        )
        components["cert_validity_label"].pack(anchor="w", pady=(0, 12))

        # Password info
        tk.Label(
            sidebar,
            text="Password is set outside this app on certificate load or sign use.",
            font=("TkDefaultFont", 8),
            fg="#999"
        ).pack(anchor="w", pady=(0, 12))

        # Visual-only option
        components["visual_only_var"] = tk.BooleanVar(value=False)
        tk.Checkbutton(
            sidebar,
            text="Visual signature only\n(no digital certificate)",
            variable=components["visual_only_var"],
            onvalue=True,
            offvalue=False
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            sidebar,
            text="Sign with image only, even if certificate is unavailable.",
            font=("TkDefaultFont", 8),
            fg="#999"
        ).pack(anchor="w", pady=(0, 12))

        # Signature declaration
        tk.Label(sidebar, text="Signature statement:").pack(anchor="w")
        components["signature_declaration_var"] = tk.StringVar(value="I'm the author")
        components["signature_declaration_combo"] = ttk.Combobox(
            sidebar,
            state="readonly",
            width=25,
            textvariable=components["signature_declaration_var"],
            values=["I'm the author", "I reviewed this document"]
        )
        components["signature_declaration_combo"].pack(fill="x", pady=(0, 12))
        components["signature_declaration_combo"].current(0)

        # Signature image
        load_sig_callback = callbacks.get("load_signature_image", lambda: None)
        tk.Button(sidebar, text="Load signature image", command=load_sig_callback).pack(fill="x")
        components["signature_image_label"] = tk.Label(
            sidebar,
            text="No signature image loaded",
            wraplength=160,
            justify="left"
        )
        components["signature_image_label"].pack(anchor="w", pady=(6, 12))

        # Selection display
        tk.Label(sidebar, text="Selection (PDF points):").pack(anchor="w")
        components["selection_label"] = tk.Label(
            sidebar,
            text="x=0.0 y=0.0 w=0.0 h=0.0",
            justify="left"
        )
        components["selection_label"].pack(anchor="w", pady=(0, 12))

        # Instructions
        tk.Label(sidebar, text="Instructions:").pack(anchor="w")
        tk.Label(
            sidebar,
            text="1) Select a certificate or load a certificate file\n2) Open a PDF\n3) Drag to draw signature box\n4) Load signature image (optional)\n5) Click Sign PDF",
            justify="left",
            fg="#333333"
        ).pack(anchor="w")

        # Sign button
        sign_callback = callbacks.get("complete_signing", lambda: None)
        tk.Button(sidebar, text="Sign PDF", command=sign_callback, bg="white", fg="blue").pack(
            fill="x", pady=(12, 0)
        )

        return sidebar, components