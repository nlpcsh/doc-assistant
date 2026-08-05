from classes.DataMgr import DataMgr
from ui.UIMgr import UIMgr

class MainApp:
    def __init__(self, root, base_dir):
        data_mgr = DataMgr(base_dir)
        self.ui_mgr = UIMgr(data_mgr)
        notebook = self.ui_mgr.create_main_window(root)
        self.ui_mgr.build_app_tabs(notebook)
