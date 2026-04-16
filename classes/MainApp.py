from tkinter import ttk

from classes.tabs.CivilContractTab import CivilContractTab
from classes.tabs.WorkTravelTab import WorkTravelTab
from classes.DataMgr import DataMgr

class MainApp:
    def __init__(self, root, base_dir):
        data_mgr = DataMgr(base_dir)
        labels = data_mgr.get_labels()

        root.title(labels["app_title"])
        nb = ttk.Notebook(root)
        nb.pack(expand=True, fill="both")

        nb.add(WorkTravelTab(nb, data_mgr), text=labels["tabs"]["work_travel"])
        nb.add(CivilContractTab(nb, data_mgr), text=labels["tabs"]["civil_contract"])
