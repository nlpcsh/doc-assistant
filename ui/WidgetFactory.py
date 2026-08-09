import tkinter as tk
from tkinter import END, ttk, messagebox, filedialog, MULTIPLE, simpledialog
from typing import Any, Dict, Optional


class WidgetFactory:
    def add_frame(
        self,
        container,
        label_text: Optional[str] = None,
        show_by_default: bool = True,
        padx: int = 10,
        pady: int = 5,
        pack: bool = True,
        pack_kwargs: Optional[Dict[str, Any]] = None,
    ):
        frame = tk.Frame(container)
        if label_text:
            ttk.Label(frame, text=label_text).pack(anchor="w")
        if pack and show_by_default:
            kwargs = {"fill": "x", "padx": padx, "pady": pady}
            if pack_kwargs:
                kwargs.update(pack_kwargs)
            frame.pack(**kwargs)
        elif not show_by_default and pack:
            frame.pack_forget()
        return frame

    def add_label(self, container, text: str, **pack_kwargs):
        label = ttk.Label(container, text=text)
        label.pack(**pack_kwargs)
        return label

    def add_listbox(
        self,
        container,
        options=None,
        selectmode=MULTIPLE,
        height: int = 10,
        exportselection: int = 0,
        pack: bool = True,
        pack_kwargs: Optional[Dict[str, Any]] = None,
    ):
        listbox = tk.Listbox(container, selectmode=selectmode, height=height, exportselection=exportselection)
        if options:
            for option in options:
                listbox.insert(END, option)
        if pack:
            kwargs = {"padx": 10, "pady": 5, "fill": "x"}
            if pack_kwargs:
                kwargs.update(pack_kwargs)
            listbox.pack(**kwargs)
        return listbox

    def add_entry(self, container, width: int = 30, pack_kwargs: Optional[Dict[str, Any]] = None):
        entry = tk.Entry(container, width=width)
        entry.configure()
        if pack_kwargs is None:
            pack_kwargs = {}
        entry.pack(**pack_kwargs)
        return entry

    def add_text(self, container, height: int = 4, width: int = 40, wrap: str = "word", pack_kwargs: Optional[Dict[str, Any]] = None):
        text_widget = tk.Text(container, height=height, width=width, wrap=wrap)
        text_widget.configure()
        if pack_kwargs is None:
            pack_kwargs = {"fill": "x"}
        text_widget.pack(**pack_kwargs)
        return text_widget

    def add_checkbutton(self, container, checkbox_text: str, variable=None, command=None, **pack_kwargs):
        if variable is None:
            variable = tk.BooleanVar()
        checkbox = ttk.Checkbutton(container, text=checkbox_text, variable=variable, command=command)
        checkbox.pack(**pack_kwargs)
        return checkbox

    def add_button(self, container, text: str, command=None, widget_kwargs: Optional[Dict[str, Any]] = None, pack_kwargs: Optional[Dict[str, Any]] = None):
        if widget_kwargs is None:
            widget_kwargs = {}
        button = ttk.Button(container, text=text, command=command, **widget_kwargs)
        if pack_kwargs is None:
            pack_kwargs = {}
        button.pack(**pack_kwargs)
        return button

    def add_combobox(self, container, values, state: str = "readonly", width: int = 37, **pack_kwargs):
        combo = ttk.Combobox(container, values=values, state=state, width=width)
        combo.pack(**pack_kwargs)
        return combo

    def create_int_var(self, value: int = 0):
        return tk.IntVar(value=value)

    def set_widget_visibility(self, widget, visible: bool, fill: str = "x", padx: int = 10, pady: int = 5, before=None):
        if visible:
            if before is not None:
                widget.pack(fill=fill, padx=padx, pady=pady, before=before)
            else:
                widget.pack(fill=fill, padx=padx, pady=pady)
        else:
            widget.pack_forget()

    @staticmethod
    def create_toplevel(parent, title: str = "", geometry: Optional[str] = None):
        top = tk.Toplevel(parent)
        if title:
            top.title(title)
        if geometry:
            top.geometry(geometry)
        top.transient(parent)
        return top

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
