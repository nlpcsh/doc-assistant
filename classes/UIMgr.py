import tkinter as tk
from os import path
from tkinter import END, ttk, messagebox, filedialog, Frame, Text, BooleanVar, Listbox, MULTIPLE, Toplevel, simpledialog
from datetime import datetime

from tkcalendar import Calendar

from classes.digisign.signing_utils import build_signature_rect, render_pdf_page_to_photoimage

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
        field_frame = Frame(owner.container)

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
        field_frame = Frame(owner.container)

        ttk.Label(field_frame, text=self.labels["fields"][label_key]).pack(anchor="w")
        text_widget = Text(field_frame, height=height, width=width, wrap="word")
        text_widget.configure(font=("Arial", 10))
        text_widget.pack(fill="x")

        field_frame.pack(fill="x", padx=10, pady=5)

        owner.input_fields.append((label_key, field_frame, text_widget))
        return text_widget

    def add_checkbox_field(self, owner, label_key, checkbox_text, default_value="", show_by_default=False, width=20):
        field_frame = Frame(owner.container)

        checkbox_var = BooleanVar(value=show_by_default)
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

    def add_checkbox_multi(self, owner, checkbox_text, options):
        var = BooleanVar()
        checkbox = ttk.Checkbutton(owner.container, text=checkbox_text, variable=var)
        checkbox.pack(anchor="w", padx=10, pady=5)

        height = min(len(options), 10)
        listbox = Listbox(owner.container, selectmode=MULTIPLE, height=height, exportselection=0)
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

        date_frame = Frame(owner.container)
        date_frame.pack(pady=5, padx=5, fill="x")

        date_entry = ttk.Entry(date_frame, width=width)
        date_entry.pack(side="left", padx=5)

        if preselect_today:
            today = datetime.today()
            date_entry.insert(0, today.strftime("%d/%m/%Y"))

        def open_calendar():
            cal_window = Toplevel(owner.winfo_toplevel())
            cal_window.title(self.labels["fields"][label_key])

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
            cal_window.transient(owner.winfo_toplevel())
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

    def start_generation(self, owner):
        owner.gen_btn.config(state="disabled")
        owner.progress.pack(pady=5)
        owner.status_label.pack()

    def reset_generation_ui(self, owner):
        owner.gen_btn.config(state="normal")
        owner.progress.pack_forget()
        owner.status_label.config(text="")

    def show_signature_preview(self, owner, pdf_path):
        owner.preview_pdf_path = pdf_path
        owner.selected_signature_rect = None

        if owner.preview_window and owner.preview_window.winfo_exists():
            owner.preview_window.destroy()

        owner.preview_window = tk.Toplevel(owner.winfo_toplevel())
        owner.preview_window.title("Place signature")
        owner.preview_window.geometry("1000x900")

        toolbar = ttk.Frame(owner.preview_window)
        toolbar.pack(fill="x", padx=8, pady=6)
        ttk.Label(toolbar, text="Click inside the document to place the visible signature. Then sign the PDF.").pack(side="left")
        ttk.Button(toolbar, text="Sign PDF", command=owner.sign_current_document).pack(side="right")

        owner.preview_canvas = tk.Canvas(owner.preview_window, bg="white")
        owner.preview_canvas.pack(fill="both", expand=True, padx=8, pady=8)
        owner.preview_canvas.bind("<Button-1>", lambda event: self.on_signature_click(owner, event))

        self.load_preview_pdf(owner, pdf_path)

    def load_preview_pdf(self, owner, pdf_path):
        owner.preview_photo, owner.preview_page_width, owner.preview_page_height, owner.preview_scale = render_pdf_page_to_photoimage(
            pdf_path,
            max_width=900,
            max_height=1100,
        )
        owner.preview_canvas.config(width=owner.preview_photo.width(), height=owner.preview_photo.height())
        owner.preview_canvas.delete("all")
        owner.preview_canvas.create_image(0, 0, anchor="nw", image=owner.preview_photo)

    def on_signature_click(self, owner, event):
        if not owner.preview_page_width or not owner.preview_page_height:
            return

        pdf_click_x = event.x / owner.preview_scale
        pdf_click_y = event.y / owner.preview_scale
        width = 140
        height = 60
        owner.selected_signature_rect = build_signature_rect(
            page_width=owner.preview_page_width,
            page_height=owner.preview_page_height,
            click_x=pdf_click_x,
            click_y=pdf_click_y,
            signature_width=width,
            signature_height=height,
        )

        owner.preview_canvas.delete("preview_marker")
        owner.preview_canvas.create_rectangle(
            event.x - 30,
            event.y - 20,
            event.x + 30,
            event.y + 20,
            outline="red",
            width=2,
            tags="preview_marker",
        )
        owner.preview_canvas.create_text(event.x, event.y, text="Signature", fill="red", tags="preview_marker")
