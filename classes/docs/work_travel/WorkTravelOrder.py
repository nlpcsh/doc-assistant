from tkinter import ttk

from classes.tabs.BaseDocTab import BaseDocTab
from datetime import datetime

class WorkTravelOrder(BaseDocTab):
    def __init__(self, parent, labels, base_dir, data_mgr):
        super().__init__(parent, labels, base_dir, data_mgr, "work_travel_order.docx")
        ttk.Label(self.container, text=labels["tabs"]["wt_order"], font=("Arial", 12, "bold")).pack(pady=10)
        self.wt_context = {}
        self.all_projects = self.add_dropdown("projects", list(self.data_mgr.data['projects'].keys()))
        self.all_projects.bind("<<ComboboxSelected>>", self.on_project_selected)
        self.persons_dropdown = self.add_dropdown("select_person", [])
    
        self.add_field("wt_purpose")
        self.add_field("wt_destination")
        self.date_from = self.add_date_field("wt_from")
        self.date_to = self.add_date_field("wt_to")
        self.add_field("wt_euro_per_day")
        self.add_field("wt_day_money_from")
        self.add_field("wt_nights_money_from")
        self.add_field("wt_travel_money_from")
        self.add_field("wt_other_expences")
        self.add_common_buttons("gen_work_travel")

    def on_project_selected(self, event):
        selected_project = self.all_projects.get()
        if selected_project in self.data_mgr.data['projects']:
            team = self.data_mgr.data['projects'][selected_project]['team']
            #person_names = [self.data_mgr.data['co_workers'][pid]["full_name"] for pid in team if pid in self.data_mgr.data['co_workers']]
            self.persons_dropdown['values'] = team # person_names
            if team: # person_names:
                self.persons_dropdown.current(0)

    def get_context(self):
        #TODO: fix it!
        project_leader = self.data_mgr.get_coworker_by_id(self.all_projects.get())
        wt_person = self.data_mgr.get_coworker_by_id(self.persons_dropdown.get())
        wt_contract_info = self.data_mgr.get_project_by_id(self.all_projects.get())["description"]
        self.wt_context = {
            "leader_titles": project_leader["titles"],
            "leader_name": project_leader["names"],
            "wt_person_titles": wt_person["titles"],
            "wt_person_names": wt_person["full_name"],
            "wt_person_work_place": wt_person["department"] + ", " + wt_person["work_place"],
            "wt_contract_info": wt_contract_info,
        }
        
        # Calculate total days
        wt_from_str = self.date_from.get()
        wt_to_str = self.date_to.get()
        if wt_from_str and wt_to_str:
            try:
                wt_from = datetime.strptime(wt_from_str, '%d/%m/%Y')
                wt_to = datetime.strptime(wt_to_str, '%d/%m/%Y')
                total_days = (wt_to - wt_from).days + 1
                self.wt_context["wt_total_days"] = str(total_days)
            except ValueError:
                self.wt_context["wt_total_days"] = "Invalid dates"
        else:
            self.wt_context["wt_total_days"] = ""

        return self.wt_context
