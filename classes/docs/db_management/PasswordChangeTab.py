import tkinter as tk
from tkinter import messagebox, ttk


class PasswordChangeTab(ttk.Frame):
    def __init__(self, parent, data_mgr):
        super().__init__(parent)
        self.data_mgr = data_mgr
        self.labels = data_mgr.get_labels()
        self._build_ui()

    def _label(self, key, default):
        db_management = self.labels.get("db_management", {})
        password_section = db_management.get("password_change", {})
        if isinstance(password_section, dict):
            return password_section.get(key, default)
        return default

    def _build_ui(self):
        form = ttk.Frame(self, padding=16)
        form.pack(fill="both", expand=True)

        self.current_password_var = tk.StringVar()
        self.new_password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()

        ttk.Label(form, text=self._label("current_password", "Current password")).grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 6)
        )
        current_entry = ttk.Entry(form, textvariable=self.current_password_var, show="*", width=40)
        current_entry.grid(row=0, column=1, sticky="ew", pady=(0, 6))

        ttk.Label(form, text=self._label("new_password", "New password")).grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=(0, 6)
        )
        new_entry = ttk.Entry(form, textvariable=self.new_password_var, show="*", width=40)
        new_entry.grid(row=1, column=1, sticky="ew", pady=(0, 6))

        ttk.Label(form, text=self._label("confirm_password", "Confirm password")).grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=(0, 6)
        )
        confirm_entry = ttk.Entry(form, textvariable=self.confirm_password_var, show="*", width=40)
        confirm_entry.grid(row=2, column=1, sticky="ew", pady=(0, 6))

        apply_button = ttk.Button(form, text=self._label("apply", "Apply"), command=self._apply_password_change)
        apply_button.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        form.columnconfigure(1, weight=1)
        current_entry.focus_set()
        self.current_entry = current_entry
        self.new_entry = new_entry
        self.confirm_entry = confirm_entry

    def _apply_password_change(self):
        try:
            self.data_mgr.change_database_password(
                self.current_password_var.get(),
                self.new_password_var.get(),
                self.confirm_password_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror(self._label("error_title", "Error"), str(exc))
            return

        messagebox.showinfo(self._label("success_title", "Success"), self._label("password_changed", "Database password changed successfully."))
        self.current_password_var.set("")
        self.new_password_var.set("")
        self.confirm_password_var.set("")
        self.current_entry.focus_set()
