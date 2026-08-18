from tkinter import font

from classes.DataMgr import DataMgr
from ui.UIMgr import UIMgr

class MainApp:
    def __init__(self, root, base_dir, current_font):
        data_mgr = DataMgr(base_dir)
        self.defaultFont = font.nametofont("TkDefaultFont")
        self.defaultFont.configure(family=current_font[0],
                                   size=current_font[1],
                                   weight=current_font[2])
        self.ui_mgr = UIMgr(data_mgr)
        notebook = self.ui_mgr.create_main_window(root)
        self.ui_mgr.build_app_tabs(notebook)
