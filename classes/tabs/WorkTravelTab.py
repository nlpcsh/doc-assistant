from tkinter import ttk

from classes.docs.work_travel.WorkTravelOrder import WorkTravelOrder
from classes.docs.work_travel.WorkTravelReport import WorkTravelReport

class WorkTravelTab(ttk.Frame):
    def __init__(self, parent, data_mgr):
        super().__init__(parent)
        sub_nb = ttk.Notebook(self)
        sub_nb.pack(expand=True, fill="both")

        labels = data_mgr.get_labels()
        sub_nb.add(WorkTravelOrder(sub_nb, data_mgr), text=labels["tabs"]["wt_order"])
        sub_nb.add(WorkTravelReport(sub_nb, data_mgr), text=labels["tabs"]["wt_report"])