from tkinter import ttk
import json

from classes.tabs.CivilContractTab import CivilContractTab
from classes.tabs.WorkTravelTab import WorkTravelTab

class MainApp:
    def __init__(self, root, base_dir):
        with open("settings/labels.json", "r") as f:
            self.labels = json.load(f)

        root.title(self.labels["app_title"])
        nb = ttk.Notebook(root)
        nb.pack(expand=True, fill="both")

        nb.add(CivilContractTab(nb, self.labels, base_dir), text=self.labels["tabs"]["civil_contract"])
        nb.add(WorkTravelTab(nb, self.labels, base_dir), text=self.labels["tabs"]["work_travel"])
