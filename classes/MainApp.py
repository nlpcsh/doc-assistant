from tkinter import ttk
import json

from os import path

from classes.tabs.CivilContractTab import CivilContractTab
from classes.tabs.WorkTravelTab import WorkTravelTab
from classes.DataMgr import DataMgr

class MainApp:
    def __init__(self, root, base_dir):
        labels_path = path.join(base_dir, "settings/labels.json")
        with open(labels_path, "r", encoding="utf-8") as f:
            self.labels = json.load(f)

        self.data_mgr = DataMgr("data/data.json")

        root.title(self.labels["app_title"])
        nb = ttk.Notebook(root)
        nb.pack(expand=True, fill="both")

        nb.add(WorkTravelTab(nb, self.labels, base_dir, self.data_mgr), text=self.labels["tabs"]["work_travel"])
        nb.add(CivilContractTab(nb, self.labels, base_dir, self.data_mgr), text=self.labels["tabs"]["civil_contract"])
