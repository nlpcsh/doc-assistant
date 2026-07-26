from tkinter import ttk

from classes.docs.BaseDoc import BaseDoc
from datetime import datetime

class BusinessTripOrder(BaseDoc):
    def __init__(self, parent, data_mgr):
        super().__init__(parent, data_mgr, "business_trip", ["business_trip_order.docx", "business_trip_report.docx"])
        self.setup_ui_components()
        self.preselect_latest_project()

    def setup_ui_components(self):
        ttk.Label(self.container, text=self.labels["tabs"]["bt_order"], font=("Arial", 12, "bold")).pack(pady=10)
        self.bt_context = {}
        self.projects_list = self.data_mgr.get_all_projects()
        self.all_projects = self.add_dropdown("projects", self.projects_list)
        self.all_projects.bind("<<ComboboxSelected>>", self.on_project_selected)
        self.persons_dropdown = self.add_dropdown("select_person", [])

        self.add_text_field("bt_purpose", height=5, width=50)
        self.add_field("bt_destination")
        self.date_from = self.add_date_field("bt_from", preselect_today=True, width=11)
        self.date_to = self.add_date_field("bt_to", min_date_from=self.date_from, width=11)
        self.add_checkbox_field("bt_euro_per_day", self.labels["fields"]["bt_euro_per_day"], default_value=str(self.data_mgr.data['common'].get("euro_per_day", "")), width=5)
        self.add_checkbox_field("bt_nights_max_value", self.labels["fields"]["bt_night_money"], width=5)
        self.bt_travel_with_var, self.travel_multiselect = self.add_checkbox_multi(self.labels["fields"]["bt_travel_money"], self.labels["multiselect"]["travel_with"])
        self.add_checkbox_field("bt_other_expences", self.labels["fields"]["bt_other_expences"], default_value=self.data_mgr.data['common'].get("other_expences", ""), width=30)
        self.add_common_buttons("gen_business_trip")

    def preselect_latest_project(self):
        if self.projects_list:
            latest_project_id = self.get_latest_project_id()
            self.all_projects.set(latest_project_id)
            self.on_project_selected(None)

    def get_latest_project_id(self):
        return max(
            self.projects_list,
            key=lambda pid: datetime.strptime(
                self.data_mgr.get_project_by_id(pid).get('end_date', '1900-01-01'),
                '%Y-%m-%d'
            )
        )

    def on_project_selected(self, event):
        selected_project = self.all_projects.get()
        if selected_project in self.data_mgr.get_all_projects():
            team = self.data_mgr.get_project_by_id(selected_project)['team']
            self.persons_dropdown['values'] = team
            if team:
                self.persons_dropdown.current(0)

    def add_project_and_person_data(self):
        project = self.data_mgr.get_project_by_id(self.all_projects.get())
        project_leader = self.data_mgr.get_coworker_by_id(project["project_lead"])
        self.person = self.data_mgr.get_coworker_by_id(self.persons_dropdown.get())
        bt_contract_info = project["description"]
        self.bt_context.update({
            "leader_titles": project_leader["titles"],
            "leader_names": project_leader["names"],
            "leader_full_name": project_leader["full_name"],
            "leader_work_place": project_leader["department"] + ", " + project_leader["work_place"],
            "bt_person_titles": self.person["titles"],
            "bt_person_names": self.person["full_name"],
            "bt_person_work_place": self.person["department"] + ", " + self.person["work_place"],
            "bt_contract_info": bt_contract_info,
            "person_id": self.persons_dropdown.get()
        })
        return bt_contract_info

    def calculate_date_context(self):
        bt_from_str = self.date_from.get()
        bt_to_str = self.date_to.get()
        if bt_from_str and bt_to_str:
            try:
                bt_from = datetime.strptime(bt_from_str, '%d/%m/%Y')
                bt_to = datetime.strptime(bt_to_str, '%d/%m/%Y')
                total_days = (bt_to - bt_from).days + 1
                self.bt_context.update({
                    "bt_from": bt_from_str,
                    "bt_to": bt_to_str,
                    "bt_total_days": str(total_days),
                    "bt_nights_count": str(max(0, total_days - 1)),
                    "bt_date": bt_from.strftime('%Y%m%d'),
                })
            except ValueError:
                self.bt_context.update({
                    "bt_total_days": "Invalid dates",
                    "bt_nights_count": "",
                    "bt_date": "date_error"
                })
        else:
            self.bt_context.update({
                "bt_total_days": "",
                "bt_nights_count": "",
                "bt_date": "no_date"
            })

    def process_field_values(self):
        for field_key, _, widget in self.input_fields:
            try:
                value = widget.get("1.0", "end-1c").strip()
            except TypeError:
                value = widget.get().strip()
            self.bt_context[field_key] = value

    def process_money_sources(self):
        bt_contract_info = self.bt_context.get("bt_contract_info", "")
        
        if self.bt_context.get("bt_euro_per_day"):
            self.bt_context["bt_day_money_from"] = self.labels["messages"]["account_on"] + bt_contract_info
        else:
            self.bt_context["bt_day_money_from"] = self.labels["messages"]["account_on"] + self.labels["messages"]["third_party"]
        
        if self.bt_context.get("bt_nights_max_value"):
            self.bt_context["bt_nights_money_from"] = self.labels["messages"]["account_on"] + bt_contract_info
        else:
            self.bt_context["bt_nights_money_from"] = self.labels["messages"]["account_on"] + self.labels["messages"]["third_party"]

    def process_travel_options(self):
        bt_contract_info = self.bt_context.get("bt_contract_info", "")
        if self.bt_travel_with_var.get():
            self.bt_context["bt_travel_money_from"] = self.labels["messages"]["account_on"] + bt_contract_info
            selected_indices = self.travel_multiselect.curselection()
            # TODO: Handle case when no options are selected
            selected_options = [self.labels["multiselect"]["travel_with"][i] for i in selected_indices]
            self.bt_context["bt_travel_with"] = ", ".join(selected_options)
        else:
            self.bt_context["bt_travel_money_from"] = self.labels["messages"]["account_on"] + self.labels["messages"]["third_party"]
            self.bt_context["bt_travel_with"] = ""
        
        for option in selected_options:
            if option == "кола":
                personal_car = self.person["car"]
                self.bt_context["bt_travel_money_from"] = f"Лично МПС {personal_car['brand']} {personal_car['model']} {personal_car['year']}г. с рег. номер {personal_car['plate']}, разход {personal_car['liters_per_100km']} л/100км, {personal_car['fuel_type']}."

    def get_context(self):
        self.bt_context = {}
        self.add_project_and_person_data()
        self.calculate_date_context()
        self.process_field_values()
        self.process_money_sources()
        self.process_travel_options()
        return self.bt_context
