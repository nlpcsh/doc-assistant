from tkinter import ttk

from classes.docs.BaseDoc import BaseDoc

from classes.docs.civil_contract.CivilContractCreate import CivilContractCreate
from classes.docs.civil_contract.CivilContractReport import CivilContractReport

class CivilContractTab(BaseDoc):
    def __init__(self, parent, data_mgr):
        super().__init__(parent, data_mgr, "civil_contract", [])

        sub_nb = ttk.Notebook(self)
        sub_nb.pack(expand=True, fill="both")

        labels = data_mgr.get_labels()
        sub_nb.add(CivilContractCreate(sub_nb, data_mgr), text=labels["tabs"]["cc_create"])
        sub_nb.add(CivilContractReport(sub_nb, data_mgr), text=labels["tabs"]["cc_report"])