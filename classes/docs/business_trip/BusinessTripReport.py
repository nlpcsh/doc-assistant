from classes.docs.BaseDoc import BaseDoc
from datetime import datetime
import tkinter as tk
from enums.Enums import BTStatus
from Helpers import Helpers

class BusinessTripReport(BaseDoc):
    def __init__(self, parent, data_mgr):
        super().__init__(parent, data_mgr, "business_trip", ["business_trip_report_personal.docx", "business_trip_report.docx"])
        self.data_mgr.update_business_trip_statuses()
        self.current_bts_to_report = self.data_mgr.get_all_bussiness_trips_by_status(BTStatus.READY_TO_REPORT)
        self.setup_ui_components()
        self.preselect_latest_business_trip()

    def setup_ui_components(self):
        self.ui_mgr.add_tab_title(self, "bt_report")
        self.business_trip_ids = list(self.current_bts_to_report)
        self.business_trips_dropdown = self.ui_mgr.add_dropdown(
            self, "business_trips", self.business_trip_ids
        )
        self.business_trips_dropdown.bind("<<ComboboxSelected>>", self.on_business_trip_selected)
        self.persons_dropdown = self.ui_mgr.add_dropdown(self, "select_person", [])
        self.ui_mgr.add_field(self, "bt_order_number")
        self.ui_mgr.add_text_field(self, "bt_personal_report", height=10, width=70)
        self.ui_mgr.add_common_buttons(self, "get_bt_report")

    def preselect_latest_business_trip(self):
        if not self.business_trip_ids:
            return
        latest_id = max(
            self.business_trip_ids,
            key=lambda bt_id: Helpers.parse_date(
                self.current_bts_to_report[bt_id].get("end_date"),
                dateformat="%d/%m/%Y"
            ),
        )
        self.business_trips_dropdown.set(latest_id)
        self.on_business_trip_selected(None)

    def on_business_trip_selected(self, event):
        business_trip = self.current_bts_to_report.get(self.business_trips_dropdown.get(), {})
        person_ids = business_trip.get("person_ids", [])
        options = [
            f"({person_id}) {self.data_mgr.get_coworker_by_id(person_id).get('full_name', 'Unknown')}"
            if self.data_mgr.get_coworker_by_id(person_id)
            else f"({person_id}) Unknown"
            for person_id in person_ids
        ]
        self.persons_dropdown['values'] = options
        if options:
            self.persons_dropdown.current(0)
        else:
            self.persons_dropdown.set('')

    def final_action(self):
        business_trip = self.current_bts_to_report.get(self.business_trips_dropdown.get())
        if business_trip:
            business_trip["status"] = BTStatus.REPORTED.name
            self.data_mgr.save_data()

    def get_context(self):
        business_trip = self.current_bts_to_report.get(self.business_trips_dropdown.get(), {})
        project = self.data_mgr.get_project_by_id(business_trip.get("project_id", "")) or {}
        leader = self.data_mgr.get_coworker_by_id(project.get("project_lead", "")) or {}

        selected_person_ids = [
            self.persons_dropdown.get(index).split(")", 1)[0].lstrip("(")
            for index in self.persons_dropdown.curselection()
        ]
        if not selected_person_ids:
            selected_person_ids = list(business_trip.get("person_ids", []))
        all_bt_persons = [
            self.data_mgr.get_coworker_by_id(person_id) or {}
            for person_id in selected_person_ids
        ]
        persons_bank_info = "\n".join(
            f"{index}.\t{person.get('titles', '')} {person.get('full_name', '')}, "
            f"IBAN: {person.get('iban', '')}"
            for index, person in enumerate(all_bt_persons, 1)
        )

        return {
            "leader_titles": leader.get("titles", ""),
            "leader_names": leader.get("names", ""),
            "leader_full_name": leader.get("full_name", ""),
            "leader_work_place": f"{leader.get('department', '')}, {leader.get('work_place', '')}",
            "bt_contract_info": project.get("description", ""),
            "bt_purpose": business_trip.get("bt_heading", ""),
            "bt_order_number": self._field_value("bt_order_number"),
            "bt_personal_report": self._field_value("bt_personal_report"),
            "person_id": "_".join(selected_person_ids),
            "persons_bank_info": persons_bank_info,
        }

    def _field_value(self, field_key):
        for key, _, widget in self.input_fields:
            if key == field_key:
                try:
                    return widget.get("1.0", "end-1c").strip()
                except TypeError:
                    return widget.get().strip()
        return ""