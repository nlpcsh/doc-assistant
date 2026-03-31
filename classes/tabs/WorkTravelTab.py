from tkinter import ttk

from classes.docs.work_travel.WorkTravelOrder import WorkTravelOrder
from classes.docs.work_travel.WorkTravelReport import WorkTravelReport

class WorkTravelTab(ttk.Frame):
    def __init__(self, parent, labels, base_dir, data_mgr):
        super().__init__(parent)
        sub_nb = ttk.Notebook(self)
        sub_nb.pack(expand=True, fill="both")
        sub_nb.add(WorkTravelReport(sub_nb, labels, base_dir, data_mgr), text="Отчет за командировка")
        sub_nb.add(WorkTravelOrder(sub_nb, labels, base_dir, data_mgr), text="Поръчка за командировка")
