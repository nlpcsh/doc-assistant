from tkinter import ttk

from classes.docs.BaseDoc import BaseDoc
from datetime import datetime

class WorkTravelOrder(BaseDoc):
    def __init__(self, parent, labels, base_dir, data_mgr):
        super().__init__(parent, labels, base_dir, data_mgr, "work_travel", "work_travel_order.docx")
        ttk.Label(self.container, text=labels["tabs"]["wt_order"], font=("Arial", 12, "bold")).pack(pady=10)
        self.wt_context = {}
        self.all_projects = self.add_dropdown("projects", list(self.data_mgr.data['projects'].keys()))
        self.all_projects.bind("<<ComboboxSelected>>", self.on_project_selected)
        self.persons_dropdown = self.add_dropdown("select_person", [])

        self.add_field("wt_purpose")
        self.add_field("wt_destination")
        self.date_from = self.add_date_field("wt_from", preselect_today=True)
        self.date_to = self.add_date_field("wt_to", min_date_from=self.date_from)
        self.add_checkbox_field("wt_euro_per_day", labels["fields"]["wt_euro_per_day"])
        self.add_checkbox_field("wt_nights_max_value", labels["fields"]["wt_night_money"])
        self.wt_travel_with_var, self.travel_multiselect = self.add_checkbox_multi(labels["fields"]["wt_travel_money"], self.labels["multiselect"])
        self.add_checkbox_field("wt_other_expences", labels["fields"]["wt_other_expences"])
        self.add_common_buttons("gen_work_travel")

    def on_project_selected(self, event):
        selected_project = self.all_projects.get()
        if selected_project in self.data_mgr.data['projects']:
            team = self.data_mgr.data['projects'][selected_project]['team']
            self.persons_dropdown['values'] = team # person_names
            if team: # person_names:
                self.persons_dropdown.current(0)

    def get_context(self):
        project = self.data_mgr.get_project_by_id(self.all_projects.get())
        project_leader = self.data_mgr.get_coworker_by_id(project["project_lead"])
        wt_person = self.data_mgr.get_coworker_by_id(self.persons_dropdown.get())
        wt_contract_info = project["description"]
        self.wt_context = {
            "leader_titles": project_leader["titles"],
            "leader_names": project_leader["names"],
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
                self.wt_context["wt_from"] = wt_from_str
                self.wt_context["wt_to"] = wt_to_str
                total_days = (wt_to - wt_from).days + 1
                self.wt_context["wt_total_days"] = str(total_days)
                self.wt_context["wt_nights_count"] = str(max(0, total_days - 1))  # Nights are usually one less than days
            except ValueError:
                self.wt_context["wt_total_days"] = "Invalid dates"
        else:
            self.wt_context["wt_total_days"] = ""
            self.wt_context["wt_nights_count"] = ""

        for field_key, _, widget in self.input_fields:
            self.wt_context[field_key] = widget.get().strip()
            if field_key == "wt_euro_per_day":
                if self.wt_context[field_key]:
                    self.wt_context["wt_day_money_from"] = self.labels["messages"]["account_on"] + wt_contract_info
                else:
                    self.wt_context["wt_day_money_from"] = self.labels["messages"]["account_on"] + self.labels["messages"]["third_party"]
            if field_key == "wt_nights_max_value":
                if self.wt_context[field_key]:
                    self.wt_context["wt_nights_money_from"] = self.labels["messages"]["account_on"] + wt_contract_info
                else:
                    self.wt_context["wt_nights_money_from"] = self.labels["messages"]["account_on"] + self.labels["messages"]["third_party"]

        # Add travel with options
        if self.wt_travel_with_var.get():
            self.wt_context["wt_travel_money_from"] = self.labels["messages"]["account_on"] + wt_contract_info
            selected_indices = self.travel_multiselect.curselection()
            selected_options = [self.labels["multiselect"][i] for i in selected_indices]
            self.wt_context["wt_travel_with"] = ", ".join(selected_options)
        else:
            self.wt_context["wt_travel_money_from"] = self.labels["messages"]["account_on"] + self.labels["messages"]["third_party"]
            self.wt_context["wt_travel_with"] = ""

        return self.wt_context
