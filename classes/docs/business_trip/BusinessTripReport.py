from tkinter import ttk

from classes.docs.BaseDoc import BaseDoc

class BusinessTripReport(BaseDoc):
    def __init__(self, parent, data_mgr):
        super().__init__(parent, data_mgr, "business_trip", ["business_trip_report.docx"])

        labels = data_mgr.get_labels()
        ttk.Label(self.container, text=labels["tabs"]["bt_report"], font=("Arial", 12, "bold")).pack(pady=10)

        self.add_dropdown("projects", list(self.data_mgr.data['projects'].keys()))

        # self.ent_company = self.add_field("company")
        # self.ent_rep = self.add_field("rep")
        self.add_common_buttons("gen_business_trip")

    def get_context(self):

        return {}