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
        self.cc_report = CivilContractReport(sub_nb, data_mgr)
        sub_nb.add(self.cc_report, text=labels["tabs"]["cc_report"])
        self.sub_nb = sub_nb
        sub_nb.bind("<<NotebookTabChanged>>", self.refresh_report_if_selected)
        # <Map> fires when this tab is shown in the main notebook
        self.bind("<Map>", self.refresh_report_if_selected)

    def refresh_report_if_selected(self, event=None):
        if self.sub_nb.nametowidget(self.sub_nb.select()) is self.cc_report:
            self.cc_report.refresh_contracts()