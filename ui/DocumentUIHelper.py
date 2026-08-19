import tkinter as tk
from tkinter import END, ttk, MULTIPLE, filedialog
from datetime import datetime
from os import path
import time
from tkcalendar import Calendar
from tkinterdnd2 import DND_FILES

from ui.WidgetFactory import WidgetFactory


class DocumentUIHelper:
    def __init__(self, data_mgr, widget_factory: WidgetFactory):
        self.data_mgr = data_mgr
        self.labels = self.data_mgr.get_labels()
        self.factory = widget_factory

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

    def _start_progress(self, owner):
        owner.progress.start()

        # Simulate a task that takes time to complete
        for i in range(101):
        # Simulate some work
            time.sleep(0.05)  
            owner.progress['value'] = i
            # Update the GUI
            owner.update_idletasks()  
        owner.progress.stop()

    def add_tab_title(self, owner, label_key):
        self.factory.add_label(owner.container, self.labels["tabs"][label_key], pady=10)

    def add_label(self, owner, text, container=None, **pack_kwargs):
        if container is None:
            container = owner.container if hasattr(owner, 'container') else owner
        return self.factory.add_label(container, text, **pack_kwargs)

    def add_frame(self, owner, label_key=None, show_by_default=True, padx=10, pady=5, container=None):
        if container is None:
            container = owner.container if hasattr(owner, 'container') else owner
        return self.factory.add_frame(container, label_text=self.labels["fields"][label_key] if label_key else None, show_by_default=show_by_default, padx=padx, pady=pady)

    def add_listbox(self, owner, options=None, selectmode=MULTIPLE, height=10, exportselection=0, container=None, pack=True, pack_kwargs=None):
        if container is None:
            container = owner.container if hasattr(owner, 'container') else owner
        return self.factory.add_listbox(container, options=options, selectmode=selectmode, height=height, exportselection=exportselection, pack=pack, pack_kwargs=pack_kwargs)

    def add_field(self, owner, label_key, show_by_default=True, initial_value="", width=30):
        field_frame = self.factory.add_frame(owner.container, pack_kwargs={"fill": "x", "padx": 10, "pady": 5})
        self.factory.add_label(field_frame, self.labels["fields"][label_key], side="left", padx=(0, 10))
        entry = self.factory.add_entry(field_frame, width=width, pack_kwargs={"side": "left"})

        if initial_value:
            entry.insert(0, initial_value)

        if not show_by_default:
            field_frame.pack_forget()

        owner.input_fields.append((label_key, field_frame, entry))
        return entry

    def add_text_field(self, owner, label_key, height=4, width=40, container=None):
        if container is None:
            container = owner.container
        field_frame = self.factory.add_frame(container, pack_kwargs={"fill": "x", "padx": 10, "pady": 5})
        self.factory.add_label(field_frame, self.labels["fields"][label_key], anchor="w")
        text_widget = self.factory.add_text(field_frame, height=height, width=width, pack_kwargs={"fill": "x"})

        owner.input_fields.append((label_key, field_frame, text_widget))
        return text_widget

    def add_checkbox(self, owner, checkbox_text, variable=None, command=None, container=None):
        if container is None:
            container = owner.container if hasattr(owner, 'container') else owner
        return self.factory.add_checkbutton(container, checkbox_text, variable=variable, command=command, anchor="w", padx=10, pady=5)

    def add_checkbox_field(self, owner, label_key, checkbox_text, default_value="", show_by_default=False, width=20, command=None):
        field_frame = self.factory.add_frame(owner.container, pack_kwargs={"fill": "x", "padx": 10, "pady": 5})

        checkbox_var = tk.BooleanVar(value=show_by_default)
        setattr(owner, f"{label_key}_var", checkbox_var)
        self.factory.add_checkbutton(field_frame, checkbox_text, variable=checkbox_var, command=command, side="left", padx=(0, 10))

        entry = self.factory.add_entry(field_frame, width=width)

        def toggle_visibility():
            if checkbox_var.get():
                entry.pack(side="left", padx=(5, 0))
                entry.delete(0, END)
                entry.insert(0, default_value)
            else:
                entry.pack_forget()
                entry.insert(0, "")

        checkbox_var.trace_add("write", lambda *args: toggle_visibility())

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
        self.factory.add_checkbutton(parent, checkbox_text, variable=var, anchor="w", padx=10, pady=5)

        height = min(len(options), 10)
        listbox = self.factory.add_listbox(parent, options=options, selectmode=MULTIPLE, height=height, exportselection=0, pack=False)

        def toggle():
            if var.get():
                listbox.pack(padx=10, pady=5, fill="x")
            else:
                listbox.pack_forget()

        var.trace_add("write", lambda *args: toggle())
        return var, listbox

    def add_date_field(self, owner, label_key, preselect_today=False, min_date_from=None, width=30):
        self.factory.add_label(owner.container, self.labels["fields"][label_key], anchor="w")

        date_frame = self.factory.add_frame(owner.container, pack_kwargs={"fill": "x", "padx": 5, "pady": 5})
        date_entry = tk.Entry(date_frame, width=width)
        date_entry.pack(side="left", padx=5)

        if preselect_today:
            today = datetime.today()
            date_entry.insert(0, today.strftime("%d/%m/%Y"))

        def open_calendar():
            cal_window = self.factory.create_toplevel(owner.winfo_toplevel(), title=self.labels["fields"][label_key])

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
            self.factory.add_button(cal_window, text=self.labels["signing"]["select_date"], command=select_date, pack_kwargs={"pady": 5})
            cal_window.grab_set()

        self.factory.add_button(date_frame, text="📅", command=open_calendar, widget_kwargs={"width": 3}, pack_kwargs={"side": "left", "padx": 2})
        return date_entry

    def add_common_buttons(self, owner, gen_label_key, container=None):
        if container is None:
            container = owner.container
        if path.exists(owner.signature_path + "sig.png"):
            owner.sig_path = owner.signature_path + "sig.png"

        owner.gen_btn = self.factory.add_button(container, text=self.labels["buttons"][gen_label_key], command=owner.start_generation, pack_kwargs={"pady": 20, "padx": 10})
        return owner.gen_btn

    def add_dropdown(self, owner, label_key, options, container=None):
        if container is None:
            container = owner.container
        self.factory.add_label(container, self.labels["fields"][label_key], anchor="w")
        combo = self.factory.add_combobox(container, values=options, state="readonly", width=37, pady=5)
        if options:
            combo.current(0)
        return combo

    def _create_file_upload_frame(self, container, label_text):
        frame = self.factory.add_frame(container, pack_kwargs={"fill": "x", "padx": 10, "pady": 5})
        self.factory.add_label(frame, label_text, anchor="w")
        upload_frame = tk.Frame(frame, relief="groove", bd=1)
        upload_frame.pack(fill="x", padx=2, pady=2)
        return frame, upload_frame

    def _create_file_listbox(self, upload_frame):
        return self.factory.add_listbox(upload_frame, height=4, exportselection=0, pack_kwargs={"fill": "x", "padx": 6, "pady": (6, 2)})

    def _add_files_to_list(self, file_paths, selected_files, file_listbox, owner):
        for file_path in file_paths:
            normalized_path = path.abspath(file_path)
            if not normalized_path or normalized_path in selected_files:
                continue
            selected_files.append(normalized_path)
            file_listbox.insert(END, path.basename(normalized_path))
        owner.uploaded_files = selected_files

    def _browse_for_files(self, selected_files, file_listbox, owner):
        file_paths = filedialog.askopenfilenames(
            title=self.labels["buttons"]["browse"],
            filetypes=[("All files", "*.*")],
            parent=owner.winfo_toplevel() if hasattr(owner, "winfo_toplevel") else None,
        )
        if file_paths:
            self._add_files_to_list(file_paths, selected_files, file_listbox, owner)

    def _extract_file_paths_from_drop(self, dropped_data):
        if not dropped_data:
            return []
        if dropped_data.startswith("{") and dropped_data.endswith("}"):
            dropped_data = dropped_data[1:-1]
        if dropped_data.startswith("(") and dropped_data.endswith(")"):
            dropped_data = dropped_data[1:-1]

        normalized_items = []
        for raw_item in dropped_data.replace("\n", " ").split():
            item = raw_item.strip().strip("{}()")
            if item:
                normalized_items.append(item)
        return normalized_items

    def _on_file_drop(self, event, selected_files, file_listbox, owner):
        file_paths = self._extract_file_paths_from_drop(event.data or "")
        if file_paths:
            self._add_files_to_list(file_paths, selected_files, file_listbox, owner)
        return "break"

    def _remove_selected_files(self, selected_files, file_listbox):
        for selected in file_listbox.curselection():
            selected_files.pop(selected)
            file_listbox.delete(selected)

    def add_file_upload(self, owner, label_text, container=None):
        if container is None:
            container = owner.container

        frame, upload_frame = self._create_file_upload_frame(container, label_text)
        file_listbox = self._create_file_listbox(upload_frame)

        button_row = tk.Frame(upload_frame)
        button_row.pack(fill="x", padx=6, pady=(0, 6))

        selected_files = []
        self.factory.add_button(
            button_row,
            text=self.labels["buttons"]["browse"],
            command=lambda: self._browse_for_files(selected_files, file_listbox, owner),
            pack_kwargs={"side": "left"},
        )
        self.factory.add_label(button_row, "Пуснете файлове тук", padx=(8, 0), anchor="w")

        self.factory.add_button(
            button_row,
            text=self.labels["buttons"]["remove_files"],
            command=lambda: self._remove_selected_files(selected_files, file_listbox),
            pack_kwargs={"side": "right"}
        )

        if DND_FILES:
            upload_frame.drop_target_register(DND_FILES)
            upload_frame.dnd_bind("<<Drop>>", lambda event: self._on_file_drop(event, selected_files, file_listbox, owner))

        owner.uploaded_files = selected_files
        owner.file_upload_listbox = file_listbox
        return {"frame": frame, "listbox": file_listbox, "selected_files": selected_files}

    def add_multiselect(self, owner, label_key, options, height=10):
        self.factory.add_label(owner.container, self.labels["fields"][label_key], anchor="w")
        listbox_height = min(max(len(options), 1), height)
        return self.factory.add_listbox(owner.container, options=options, selectmode=MULTIPLE, height=listbox_height, exportselection=0)

    def start_generation(self, owner):
        owner.gen_btn.config(state="disabled")
        owner.progress.pack(pady=5)
        self._start_progress(owner=owner)
        owner.status_label.pack()

    def reset_generation_ui(self, owner):
        owner.gen_btn.config(state="normal")
        owner.progress.pack_forget()
        owner.status_label.config(text="")

    def set_field_value(self, owner, label_key, value):
        for key, frame, widget in owner.input_fields:
            if key == label_key:
                if isinstance(widget, tk.Entry):
                    widget.delete(0, END)
                    widget.insert(0, value)
                elif isinstance(widget, tk.Text):
                    widget.delete("1.0", END)
                    widget.insert("1.0", value)
                break

    def set_field_state(self, owner, label_key, state):
        for key, frame, widget in owner.input_fields:
            if key == label_key:
                try:
                    widget.config(state=state)
                except Exception:
                    pass
                break
