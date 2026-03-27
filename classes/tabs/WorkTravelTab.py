from tkinter import ttk

from classes.tabs.BaseDocTab import BaseDocTab

class WorkTravelTab(BaseDocTab):
    def __init__(self, parent, labels, base_dir):
        super().__init__(parent, labels, base_dir, "work_travel.docx")
        ttk.Label(self.container, text=labels["tabs"]["work_travel"], font=("Arial", 12, "bold")).pack(pady=10)

        self.ent_company = self.add_field("company")
        self.ent_rep = self.add_field("rep")
        self.add_common_buttons("gen_work_travel")

    def get_context(self):
        return {'company': self.ent_company.get(), 'rep': self.ent_rep.get()}