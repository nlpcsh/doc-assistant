from ui.WidgetFactory import WidgetFactory
from ui.DocumentUIHelper import DocumentUIHelper
from ui.SigningUIBuilder import SigningUIBuilder
from Helpers import Helpers

class UIMgr:
    def __init__(self, data_mgr):
        self.widget_factory = WidgetFactory()
        self.document_ui = DocumentUIHelper(data_mgr, self.widget_factory)
        self.signing_ui = SigningUIBuilder(data_mgr, self.widget_factory)
        self.labels = self.document_ui.labels
        self.data_mgr = data_mgr

    def create_main_window(self, root):
        tab_colors_preferences = Helpers.get_preferences().get("tabs", {})
        root.title(self.labels["app_title"])
        from tkinter import ttk

        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill="both")

        style = ttk.Style(root)
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TNotebook.Tab", padding=[5, 3], background=tab_colors_preferences["colors"]["background_color"], foreground=tab_colors_preferences["colors"]["text_color"])
        style.map(
            "TNotebook.Tab",
            background=[("selected", tab_colors_preferences["colors"]["selected"]), ("active", tab_colors_preferences["colors"]["active"])],
            foreground=[("selected", tab_colors_preferences["colors"]["selected_text"]), ("active", tab_colors_preferences["colors"]["active_text"])],
        )

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

    def __getattr__(self, name):
        if hasattr(self.document_ui, name):
            return getattr(self.document_ui, name)
        if hasattr(self.signing_ui, name):
            return getattr(self.signing_ui, name)
        if hasattr(self.widget_factory, name):
            return getattr(self.widget_factory, name)
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

    @staticmethod
    def build_toolbar(root):
        return SigningUIBuilder.build_toolbar(root)

    @staticmethod
    def build_buttons(toolbar, callbacks: dict, labels: dict):
        return SigningUIBuilder.build_buttons(toolbar, callbacks, labels)

    @staticmethod
    def build_canvas(content, width: int = 680, height: int = 900):
        return SigningUIBuilder.build_canvas(content, width, height)

    @staticmethod
    def build_sidebar(content, callbacks=None, labels=None):
        return SigningUIBuilder.build_sidebar(content, callbacks, labels)

    @staticmethod
    def build_page_frame(root):
        return SigningUIBuilder.build_page_frame(root)

    @staticmethod
    def create_toplevel(parent, title: str = "", geometry=None):
        return WidgetFactory.create_toplevel(parent, title, geometry)

    @staticmethod
    def ask_open_filename(title: str = "Open File", filetypes=None, initialdir=None):
        return WidgetFactory.ask_open_filename(title=title, filetypes=filetypes, initialdir=initialdir)

    @staticmethod
    def ask_string(title: str, prompt: str, show=None):
        return WidgetFactory.ask_string(title, prompt, show=show)

    @staticmethod
    def show_error(title: str, message: str):
        return WidgetFactory.show_error(title, message)

    @staticmethod
    def show_warning(title: str, message: str):
        return WidgetFactory.show_warning(title, message)

    @staticmethod
    def show_info(title: str, message: str):
        return WidgetFactory.show_info(title, message)
