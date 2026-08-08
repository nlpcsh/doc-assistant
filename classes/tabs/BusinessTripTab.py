from tkinter import ttk

from classes.docs.business_trip.BusinessTripOrder import BusinessTripOrder
from classes.docs.business_trip.BusinessTripReport import BusinessTripReport
from classes.docs.business_trip.BusinessTripOrderEdit import BusinessTripOrderEdit

class BusinessTripTab(ttk.Frame):
    def __init__(self, parent, data_mgr):
        super().__init__(parent)
        sub_nb = ttk.Notebook(self)
        sub_nb.pack(expand=True, fill="both")

        labels = data_mgr.get_labels()
        sub_nb.add(BusinessTripOrder(sub_nb, data_mgr), text=labels["tabs"]["bt_order"])
        sub_nb.add(BusinessTripOrderEdit(sub_nb, data_mgr), text=labels["tabs"]["bt_order_edit"])
        sub_nb.add(BusinessTripReport(sub_nb, data_mgr), text=labels["tabs"]["bt_report"])