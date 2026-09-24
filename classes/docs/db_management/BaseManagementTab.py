import tkinter as tk
from tkinter import messagebox, simpledialog, ttk


class BaseManagementTab(ttk.Frame):
    def __init__(self, parent, data_mgr, collection_name, title, default_fields=None):
        super().__init__(parent)
        self.data_mgr = data_mgr
        self.collection_name = collection_name
        self.title = title
        self.default_fields = default_fields or {}
        self.collection = self.data_mgr.data.get(self.collection_name, {})
        self.current_record_id = None
        self.form_widgets = {}
        self.labels = self.data_mgr.get_labels()

        self._build_ui()

    def _field_label(self, field_name):
        db_management = self.labels.get("db_management", {})
        collection_labels = db_management.get(self.collection_name, {})
        if isinstance(collection_labels, dict) and field_name in collection_labels:
            return collection_labels[field_name]

        if field_name in self.labels.get("fields", {}):
            return self.labels["fields"][field_name]

        if field_name in db_management:
            return db_management[field_name]

        label = field_name.replace(".", " / ").replace("_", " ")
        return label.title()

    def _build_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(top_frame, text=self.title).pack(anchor="w")

        selector_frame = ttk.Frame(top_frame)
        selector_frame.pack(fill="x", pady=(5, 0))

        db_management = self.labels.get("db_management", {})
        ttk.Label(selector_frame, text=db_management.get("select", "Select:")).pack(side="left", padx=(0, 8))

        self.selector_var = tk.StringVar()
        self.selector = ttk.Combobox(selector_frame, textvariable=self.selector_var, state="readonly", width=40)
        self.selector.pack(side="left", fill="x", expand=True)
        self.selector.bind("<<ComboboxSelected>>", lambda _event: self._load_selected_record())

        add_button = ttk.Button(selector_frame, text=db_management.get("add_new", "Add new"), command=self._add_new_record)
        add_button.pack(side="left", padx=(8, 0))

        self.fields_frame = ttk.Frame(self)
        self.fields_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self.save_button = ttk.Button(self, text=db_management.get("save", "Save"), command=self._save_current_record)
        self.save_button.pack(fill="x", padx=10, pady=(0, 10))

        self._refresh_selector()

    def _refresh_selector(self):
        values = sorted(self.data_mgr.data.get(self.collection_name, {}).keys())
        self.selector.configure(values=values)
        if not values:
            self.selector_var.set("")
            self._clear_fields()
            return

        if self.current_record_id in values:
            self.selector_var.set(self.current_record_id)
        else:
            self.selector_var.set(values[0])
        self._load_selected_record()

    def _clear_fields(self):
        for widget in self.form_widgets.values():
            widget.destroy()
        self.form_widgets = {}

    def _flatten_record(self, record):
        result = {}

        def add_value(prefix, value):
            if isinstance(value, dict):
                for key, nested in value.items():
                    child_prefix = f"{prefix}.{key}" if prefix else key
                    add_value(child_prefix, nested)
            elif isinstance(value, list):
                result[prefix] = value
            else:
                result[prefix] = value

        if isinstance(record, dict):
            for key, value in record.items():
                add_value(key, value)
        return result

    def _format_field_value(self, value):
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return ""
        return str(value)

    def _ensure_default_values(self, flat_record):
        merged = dict(self.default_fields)
        for key, value in flat_record.items():
            merged[key] = value
        return merged

    def _render_fields(self, record):
        self._clear_fields()
        flat_record = self._flatten_record(record)
        display_data = self._ensure_default_values(flat_record)

        for i, (field_name, value) in enumerate(sorted(display_data.items())):
            label = ttk.Label(self.fields_frame, text=self._field_label(field_name))
            label.grid(row=i, column=0, sticky="w", padx=(0, 8), pady=3)

            var = ttk.Entry(self.fields_frame, width=80)
            var.insert(0, self._format_field_value(value))
            var.grid(row=i, column=1, sticky="ew", pady=3)
            self.form_widgets[field_name] = var

        self.fields_frame.columnconfigure(1, weight=1)

    def _load_selected_record(self):
        record_id = self.selector_var.get()
        if not record_id:
            self.current_record_id = None
            self._render_fields({})
            return

        self.current_record_id = record_id
        current_record = self.data_mgr.data.get(self.collection_name, {}).get(record_id, {})
        self._render_fields(current_record)

    def _get_record_id_for_new_item(self):
        record_id = simpledialog.askstring("New item", f"Enter the new {self.title.lower()} ID:")
        if record_id is None:
            return None
        record_id = record_id.strip()
        if not record_id:
            messagebox.showwarning("Missing ID", "An ID is required before saving a new item.")
            return None
        return record_id

    def _add_new_record(self):
        item_id = self._get_record_id_for_new_item()
        if item_id is None:
            return

        collection = self.data_mgr.data.setdefault(self.collection_name, {})
        collection[item_id] = collection.get(item_id, {})
        self.data_mgr.save_data()
        self.current_record_id = item_id
        self._refresh_selector()
        self.selector_var.set(item_id)
        self._render_fields(collection.get(item_id, {}))

    def _set_nested_value(self, record, field_name, value):
        parts = field_name.split(".")
        current = record
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    def _coerce_value(self, field_name, raw_value, original_value):
        if raw_value is None:
            return None

        value = raw_value.strip()
        if original_value is not None:
            if isinstance(original_value, bool):
                return value.lower() in ("1", "true", "yes", "y")
            if isinstance(original_value, int):
                return int(value) if value else 0
            if isinstance(original_value, float):
                return float(value) if value else 0.0
            if isinstance(original_value, list):
                return [item.strip() for item in value.split(",") if item.strip()]

        if field_name.endswith("_date") or field_name.endswith("date"):
            return value
        return value

    def _save_current_record(self):
        record_id = self.selector_var.get().strip()
        if not record_id:
            messagebox.showwarning("Missing selection", "Select an item before saving.")
            return

        collection = self.data_mgr.data.setdefault(self.collection_name, {})
        current_record = collection.get(record_id, {})
        if not isinstance(current_record, dict):
            current_record = {}

        original_flat = self._flatten_record(current_record)
        for field_name, widget in self.form_widgets.items():
            value = widget.get()
            original_value = original_flat.get(field_name)
            converted = self._coerce_value(field_name, value, original_value)
            self._set_nested_value(current_record, field_name, converted)

        collection[record_id] = current_record
        self.data_mgr.data[self.collection_name] = collection
        self.data_mgr.save_data()
        self._render_fields(current_record)
        messagebox.showinfo("Saved", f"{self.title} saved successfully.")

    def get_collection(self):
        return self.data_mgr.data.get(self.collection_name, {})
