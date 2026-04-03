from tkinter import ttk

from classes.docs.BaseDoc import BaseDoc
from datetime import datetime

class WorkTravelOrder(BaseDoc):
    def __init__(self, parent, labels, base_dir, data_mgr):
        super().__init__(parent, labels, base_dir, data_mgr, "work_travel", "work_travel_order.docx")
        self.setup_ui_components()
        self.preselect_latest_project()

    def setup_ui_components(self):
        ttk.Label(self.container, text=self.labels["tabs"]["wt_order"], font=("Arial", 12, "bold")).pack(pady=10)
        self.wt_context = {}
        projects_list = list(self.data_mgr.data['projects'].keys())
        self.all_projects = self.add_dropdown("projects", projects_list)
        self.all_projects.bind("<<ComboboxSelected>>", self.on_project_selected)
        self.persons_dropdown = self.add_dropdown("select_person", [])

        self.add_text_field("wt_purpose", height=5, width=50)
        self.add_field("wt_destination")
        self.date_from = self.add_date_field("wt_from", preselect_today=True, width=11)
        self.date_to = self.add_date_field("wt_to", min_date_from=self.date_from, width=11)
        self.add_checkbox_field("wt_euro_per_day", self.labels["fields"]["wt_euro_per_day"], default_value=str(self.data_mgr.data['common'].get("euro_per_day", "")), width=5)
        self.add_checkbox_field("wt_nights_max_value", self.labels["fields"]["wt_night_money"], width=5)
        self.wt_travel_with_var, self.travel_multiselect = self.add_checkbox_multi(self.labels["fields"]["wt_travel_money"], self.labels["multiselect"]["travel_with"])
        self.add_checkbox_field("wt_other_expences", self.labels["fields"]["wt_other_expences"], default_value=self.data_mgr.data['common'].get("other_expences", ""), width=30)
        self.add_common_buttons("gen_work_travel")

    def preselect_latest_project(self):
        projects_list = list(self.data_mgr.data['projects'].keys())
        if projects_list:
            latest_project_id = self.get_latest_project_id(projects_list)
            self.all_projects.set(latest_project_id)
            self.on_project_selected(None)

    def get_latest_project_id(self, projects_list):
        return max(
            projects_list,
            key=lambda pid: datetime.strptime(
                self.data_mgr.data['projects'][pid].get('end_date', '1900-01-01'),
                '%Y-%m-%d'
            )
        )

    def on_project_selected(self, event):
        selected_project = self.all_projects.get()
        if selected_project in self.data_mgr.data['projects']:
            team = self.data_mgr.data['projects'][selected_project]['team']
            self.persons_dropdown['values'] = team
            if team:
                self.persons_dropdown.current(0)

    def add_project_and_person_data(self):
        project = self.data_mgr.get_project_by_id(self.all_projects.get())
        project_leader = self.data_mgr.get_coworker_by_id(project["project_lead"])
        self.person = self.data_mgr.get_coworker_by_id(self.persons_dropdown.get())
        wt_contract_info = project["description"]
        self.wt_context.update({
            "leader_titles": project_leader["titles"],
            "leader_names": project_leader["names"],
            "wt_person_titles": self.person["titles"],
            "wt_person_names": self.person["full_name"],
            "wt_person_work_place": self.person["department"] + ", " + self.person["work_place"],
            "wt_contract_info": wt_contract_info,
            "person_id": self.persons_dropdown.get()
        })
        return wt_contract_info

    def calculate_date_context(self):
        wt_from_str = self.date_from.get()
        wt_to_str = self.date_to.get()
        if wt_from_str and wt_to_str:
            try:
                wt_from = datetime.strptime(wt_from_str, '%d/%m/%Y')
                wt_to = datetime.strptime(wt_to_str, '%d/%m/%Y')
                total_days = (wt_to - wt_from).days + 1
                self.wt_context.update({
                    "wt_from": wt_from_str,
                    "wt_to": wt_to_str,
                    "wt_total_days": str(total_days),
                    "wt_nights_count": str(max(0, total_days - 1)),
                    "wt_date": wt_from.strftime('%Y%m%d'),
                })
            except ValueError:
                self.wt_context.update({
                    "wt_total_days": "Invalid dates",
                    "wt_nights_count": "",
                    "wt_date": "date_error"
                })
        else:
            self.wt_context.update({
                "wt_total_days": "",
                "wt_nights_count": "",
                "wt_date": "no_date"
            })

    def process_field_values(self):
        for field_key, _, widget in self.input_fields:
            try:
                value = widget.get("1.0", "end-1c").strip()
            except TypeError:
                value = widget.get().strip()
            self.wt_context[field_key] = value

    def process_money_sources(self):
        wt_contract_info = self.wt_context.get("wt_contract_info", "")
        
        if self.wt_context.get("wt_euro_per_day"):
            self.wt_context["wt_day_money_from"] = self.labels["messages"]["account_on"] + wt_contract_info
        else:
            self.wt_context["wt_day_money_from"] = self.labels["messages"]["account_on"] + self.labels["messages"]["third_party"]
        
        if self.wt_context.get("wt_nights_max_value"):
            self.wt_context["wt_nights_money_from"] = self.labels["messages"]["account_on"] + wt_contract_info
        else:
            self.wt_context["wt_nights_money_from"] = self.labels["messages"]["account_on"] + self.labels["messages"]["third_party"]

    def process_travel_options(self):
        wt_contract_info = self.wt_context.get("wt_contract_info", "")
        if self.wt_travel_with_var.get():
            self.wt_context["wt_travel_money_from"] = self.labels["messages"]["account_on"] + wt_contract_info
            selected_indices = self.travel_multiselect.curselection()
            selected_options = [self.labels["multiselect"]["travel_with"][i] for i in selected_indices]
            self.wt_context["wt_travel_with"] = ", ".join(selected_options)
        else:
            self.wt_context["wt_travel_money_from"] = self.labels["messages"]["account_on"] + self.labels["messages"]["third_party"]
            self.wt_context["wt_travel_with"] = ""
        
        for option in selected_options:
            if option == "кола":
                personal_car = self.person["car"]
                self.wt_context["wt_travel_money_from"] = f"Лично МПС {personal_car['brand']} {personal_car['model']} {personal_car['year']}г. с рег. номер {personal_car['plate']}, разход {personal_car['liters_per_100km']} л/100км, {personal_car['fuel_type']}."

    def get_context(self):
        self.wt_context = {}
        self.add_project_and_person_data()
        self.calculate_date_context()
        self.process_field_values()
        self.process_money_sources()
        self.process_travel_options()
        return self.wt_context
