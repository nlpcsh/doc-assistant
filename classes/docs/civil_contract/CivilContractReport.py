from classes.docs.BaseDoc import BaseDoc
from enums.Enums import CCStatus
from Helpers import Helpers

class CivilContractReport(BaseDoc):
    def __init__(self, parent, data_mgr):
        super().__init__(
            parent,
            data_mgr,
            "civil_contract",
            ["civil_contract_person_report.docx", "cc_report_of_findings.docx"],
            output_folder="civil_contracts",
        )
        self.current_contracts_to_report = {
            contract_id: contract
            for contract_id, contract in data_mgr.data.get("civil_contracts", {}).items()
            if contract.get("status") != CCStatus.REPORTED.name
        }
        self.setup_ui_components()
        self.preselect_latest_contract()

    def setup_ui_components(self):
        self.ui_mgr.add_tab_title(self, "civil_contract_report")
        self.contract_ids = list(self.current_contracts_to_report)
        self.contracts_dropdown = self.ui_mgr.add_dropdown(self, "civil_contracts", self.contract_ids)
        self.contracts_dropdown.bind("<<ComboboxSelected>>", self.on_contract_selected)

        self.ui_mgr.add_text_field(self, "completed_task_description", height=5, width=70)
        self.ui_mgr.add_text_field(self, "personal_report", height=10, width=70)

        self.uploaded_files = []
        self.ui_mgr.add_file_upload(
            self, self.labels["fields"]["attachments"], container=self
        )
        self.ui_mgr.add_common_buttons(self, "gen_contract_report", container=self)

    def preselect_latest_contract(self):
        if self.contract_ids:
            self.contracts_dropdown.current(0)
            self.on_contract_selected(None)

    def on_contract_selected(self, event):
        """Refresh the selected contract context when the dropdown changes."""
        contract_id = self.contracts_dropdown.get()
        contract = self.current_contracts_to_report.get(contract_id, {})
        self.cc_context = {
            "contract_id": contract_id,
            "person_id": contract.get("person_id"),
        }

    def get_context(self):
        contract_id = self.contracts_dropdown.get()
        contract = self.current_contracts_to_report.get(contract_id, {})
        person_id = contract.get("person_id", "")
        person = self.data_mgr.get_coworker_by_id(person_id) or {}
        project = self.data_mgr.get_project_by_id(contract.get("project_id", "")) or {}
        project_leader = self.data_mgr.get_coworker_by_id(project.get("project_lead", "")) or {}

        self.cc_context = {
            "person_id": person_id,
            "project_info": project.get("description", ""),
            "leader_titles": project_leader.get("titles", ""),
            "leader_names": project_leader.get("names", ""),
            "cc_person_titles": person.get("titles", ""),
            "cc_person_names": person.get("full_name", person.get("names", "")),
            "person_titles": person.get("titles", ""),
            "person_names": person.get("full_name", person.get("names", "")),
            "personal_report": self._field_value("personal_report"),
            "completed_task_description": self._field_value("completed_task_description"),
            "cc_report_date": Helpers.get_current_date_str(dateformat="%d.%m.%Y"),
            "doc_date_and_ids_identifier": contract.get(
                "doc_date_and_ids_identifier", contract_id
            ),
            "sub_folder": f"/{person_id}/" if person_id else "/",
        }
        return self.cc_context

    def final_action(self):
        contract_id = self.contracts_dropdown.get()
        contract = self.current_contracts_to_report.get(contract_id)
        if not contract:
            return

        contract["status"] = CCStatus.REPORTED.name
        contract["completed_task_description"] = self.cc_context["completed_task_description"]
        contract["personal_report"] = self.cc_context["personal_report"]

        Helpers.copy_files_to_folder(self.uploaded_files, self._get_report_output_folder())
        self.data_mgr.save_data()

    def _get_report_output_folder(self):
        output_folders = self.data_mgr.get_output_folders()
        contract_id = self.contracts_dropdown.get()
        person_id = self.cc_context.get("person_id", "")
        sub_folder = f"/{person_id}/" if person_id else "/"
        return (
            f"{output_folders['common']}{output_folders['civil_contracts']}"
            f"{contract_id}{sub_folder}"
        )

    def _field_value(self, field_key):
        for key, _, widget in self.input_fields:
            if key == field_key:
                try:
                    return widget.get("1.0", "end-1c").strip()
                except TypeError:
                    return widget.get().strip()
        return ""
