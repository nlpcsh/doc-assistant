from classes.docs.BaseDoc import BaseDoc
from enums.Enums import BTStatus
from Helpers import Helpers

class BusinessTripReport(BaseDoc):
    def __init__(self, parent, data_mgr):
        super().__init__(parent, data_mgr, "business_trip", [])
        self.data_mgr.update_business_trip_statuses()
        self.current_bts_to_report = self.data_mgr.get_all_bussiness_trips_by_status([BTStatus.READY_TO_REPORT, BTStatus.PL_REPORTED])
        self.project_leader_id = None
        self.setup_ui_components()
        self.preselect_latest_business_trip()

    def setup_ui_components(self):
        self.ui_mgr.add_tab_title(self, "bt_report")
        self.business_trip_ids = list(self.current_bts_to_report)
        self.business_trips_dropdown = self.ui_mgr.add_dropdown(
            self, "business_trips", self.business_trip_ids
        )
        self.business_trips_dropdown.bind("<<ComboboxSelected>>", self.on_business_trip_selected)
        self.ui_mgr.add_field(self, "bt_order_number")


        self.generate_only_report_var = self.ui_mgr.create_int_var(value=0)
        self.generate_only_report_checkbox = self.ui_mgr.add_checkbox(
            self,
            self.labels["fields"]["generate_only_report"],
            variable=self.generate_only_report_var,
            command=self.on_generate_only_report_checkbox_changed,
        )

        self.report_fields_frame = self.ui_mgr.add_frame(self)
        self.persons_dropdown = self.ui_mgr.add_dropdown(
            self, "select_person", [], container=self.report_fields_frame
        )
        self.ui_mgr.add_text_field(
            self, "bt_personal_report", height=10, width=70, container=self.report_fields_frame
        )

        self.uploaded_files = []
        self.ui_mgr.add_file_upload(self, self.labels["fields"]["attachments"], container=self.report_fields_frame)

        self.buttons_frame = self.ui_mgr.add_frame(self, show_by_default=True)
        self.ui_mgr.add_common_buttons(self, "get_bt_report", container=self.buttons_frame)

    def on_generate_only_report_checkbox_changed(self):
        if self.generate_only_report_var.get() == 1:
            self.ui_mgr.set_field_state(self, "bt_order_number", "disabled")
            self.ui_mgr.set_widget_visibility(self.report_fields_frame, False)
        else:
            self.ui_mgr.set_field_state(self, "bt_order_number", "normal")
            self.ui_mgr.set_widget_visibility(self.report_fields_frame, True, before=self.buttons_frame)

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

    def _update_project_leader_id(self):
        business_trip = self.current_bts_to_report.get(self.business_trips_dropdown.get(), {})
        project = self.data_mgr.get_project_by_id(business_trip.get("project_id", "")) or {}
        project_lead_id = project.get("project_lead")
        if project_lead_id and project_lead_id in business_trip.get("person_ids", []):
            self.project_leader_id = project_lead_id
        else:
            self.project_leader_id = None

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
        bt_order_number = business_trip.get("bt_order_number")
        if bt_order_number:
            self.ui_mgr.set_field_value(self, "bt_order_number", bt_order_number)
        self._update_project_leader_id()

    def get_context(self):
        self.bt_context = {}
        business_trip = self.current_bts_to_report.get(self.business_trips_dropdown.get(), {})
        project = self.data_mgr.get_project_by_id(business_trip.get("project_id", "")) or {}
        leader_id = project.get("project_lead")
        self.bt_context['leader_id'] = leader_id
        leader = self.data_mgr.get_coworker_by_id(leader_id) or {}
        all_bt_persons = [
            self.data_mgr.get_coworker_by_id(person_id) or {}
            for person_id in business_trip.get("person_ids", "")
        ]

        persons_bank_info = "\n".join(
            f"{index}.\t{person.get('titles', '')} {person.get('full_name', '')}, "
            f"IBAN: {person.get('iban', '')}"
            for index, person in enumerate(all_bt_persons, 1)
        )

        if self.generate_only_report_var.get() == 1:
            self.template_names.append("business_trip_report_money.docx")
        elif self.project_leader_id and leader_id == self.project_leader_id:
            self.template_names = ["business_trip_report_personal.docx", "business_trip_report_money.docx"]
        else:
            self.template_names.append("business_trip_report_personal.docx")

        doc_date_and_ids_identifier = self.business_trips_dropdown.get()

        self.bt_context['selected_person_id'] = self.persons_dropdown.get().strip().split(")", 1)[0].lstrip("(") if self.persons_dropdown.get() else None
        selected_person = self.data_mgr.get_coworker_by_id(self.bt_context['selected_person_id'])

        return {
            "bt_person_title": selected_person.get("titles", ""),
            "bt_person_names": selected_person.get("full_name", ""),
            "bt_headline": business_trip.get("bt_heading", ""),
            "leader_titles": leader.get("titles", ""),
            "leader_names": leader.get("names", ""),
            "bt_order_number": self._field_value("bt_order_number"),
            "bt_personal_report": self._field_value("bt_personal_report"),
            "person_id": self.bt_context['selected_person_id'],
            "persons_bank_info": persons_bank_info,
            "current_date": Helpers.get_current_date_str(dateformat="%d.%m.%Y"),
            "bt_contract_info": project.get("description", ""),
            "doc_date_and_ids_identifier": doc_date_and_ids_identifier,
            "sub_folder": f"/{self.bt_context['selected_person_id']}/",
        }

    def _get_report_output_folder(self):
        doc_identifier = self.business_trips_dropdown.get()
        sub_folder = f"/{self.bt_context['selected_person_id']}/" if self.bt_context['selected_person_id'] else "/"
        output_folders = self.data_mgr.get_output_folders()
        return f"{output_folders['common']}{output_folders['business_trip']}{doc_identifier}{sub_folder}"

    def final_action(self):
        business_trip = self.current_bts_to_report.get(self.business_trips_dropdown.get())
        if self.bt_context['selected_person_id'] not in business_trip['reported_ids']:
            business_trip['reported_ids'].append(self.bt_context['selected_person_id'])
        is_all_persons_reported = len(business_trip['person_ids']) == len(business_trip['reported_ids'])
        if self.bt_context['leader_id'] == self.bt_context['selected_person_id'] or self.generate_only_report_var.get() == 1:
            business_trip['status'] = BTStatus.PL_REPORTED.name
        if is_all_persons_reported and business_trip['status'] == BTStatus.PL_REPORTED.name:
            business_trip['status'] = BTStatus.REPORTED.name
        report_folder = self._get_report_output_folder()
        if getattr(self, "uploaded_files", None):
            Helpers.copy_files_to_folder(self.uploaded_files, report_folder)
        self.data_mgr.save_data()

    def _field_value(self, field_key):
        for key, _, widget in self.input_fields:
            if key == field_key:
                try:
                    return widget.get("1.0", "end-1c").strip()
                except TypeError:
                    return widget.get().strip()
        return ""