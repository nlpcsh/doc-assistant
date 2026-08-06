
from datetime import datetime

from classes.docs.BaseDoc import BaseDoc
from enums.Enums import CCStatus

class CivilContractCreate(BaseDoc):
    def __init__(self, parent, data_mgr):
        super().__init__(parent, data_mgr, "civil_contract", ["civil_contract_create.docx", "cc_pl_report.docx"], output_folder='civil_contracts')
        self.setup_ui_components()
        self.preselect_latest_project()

    def setup_ui_components(self):
        self.ui_mgr.add_tab_title(self, "civil_contract_create")
        self.cc_context = {}
        self.projects_list = self.data_mgr.get_all_projects()
        self.all_projects = self.ui_mgr.add_dropdown(self, "projects", self.projects_list)
        self.all_projects.bind("<<ComboboxSelected>>", self.on_project_selected)
        self.persons_dropdown = self.ui_mgr.add_dropdown(self, "select_person", [])
        self.cc_start_date = self.ui_mgr.add_date_field(self, "cc_start_date", preselect_today=False)
        self.cc_task = self.ui_mgr.add_text_field(self, "cc_task")
        self.cc_task_start_date = self.ui_mgr.add_date_field(self, "cc_task_start_date", preselect_today=False)
        self.cc_task_end_date = self.ui_mgr.add_date_field(self, "cc_task_end_date", preselect_today=False, min_date_from=self.cc_task_start_date)
        self.cc_payment_due_date = self.ui_mgr.add_date_field(self, "cc_payment_due_date", preselect_today=False)
        self.cc_task_amount = self.ui_mgr.add_field(self, "cc_task_amount", width=20)
        self.cc_task_amount_in_words = self.ui_mgr.add_field(self, "cc_task_amount_in_words", width=70)
        self.cc_person_responsibility = self.ui_mgr.add_text_field(self, "cc_person_responsibility", height=3, width=70)
        self.cc_penalty = self.ui_mgr.add_text_field(self, "cc_penalty", height=3, width=70)

        self.buttons_frame = self.ui_mgr.add_frame(self, show_by_default=True)
        self.ui_mgr.add_common_buttons(self, "gen_contract", container=self.buttons_frame)

    def preselect_latest_project(self):
        if self.projects_list:
            latest_project_id = self.get_latest_project_id()
            self.all_projects.set(latest_project_id)
            self.on_project_selected(None)

    def get_latest_project_id(self):
        return max(
            self.projects_list,
            key=lambda pid: datetime.strptime(
                self.data_mgr.get_project_by_id(pid).get('end_date', '2001-01-01'),
                '%Y-%m-%d'
            )
        )

    def on_project_selected(self, event):
        selected_project = self.all_projects.get()
        project = self.data_mgr.get_project_by_id(selected_project)
        options = []
        if project:
            team = project.get('team', [])
            for coworker_id in team:
                coworker = self.data_mgr.get_coworker_by_id(coworker_id)
                options.append(f"({coworker_id}) {coworker.get('names', 'Unknown')}")
        self.persons_dropdown['values'] = options
        if options:
            self.persons_dropdown.current(0)
        else:
            self.persons_dropdown.set('')

    def get_context(self):
        self.cc_context = {}
        self._populate_contract_fields()

        self.cc_context["sub_folder"] = ""
        self.cc_context["doc_date_and_ids_identifier"] = self._build_doc_identifier()
        self._populate_project_context()
        self._populate_person_context()

        return self.cc_context

    def _populate_contract_fields(self):
        self.cc_context["cc_task"] = self._get_text_value(self.cc_task)
        self.cc_context["cc_start_date"] = self._get_date_value(self.cc_start_date)
        self.cc_context["cc_task_start_date"] = self._get_date_value(self.cc_task_start_date)
        self.cc_context["cc_task_end_date"] = self._get_date_value(self.cc_task_end_date)
        self.cc_context["cc_payment_due_date"] = self._get_date_value(self.cc_payment_due_date)
        self.cc_context["cc_task_amount"] = self._get_text_value(self.cc_task_amount)
        self.cc_context["cc_task_amount_in_words"] = self._get_text_value(self.cc_task_amount_in_words)
        self.cc_context["cc_person_responsibility"] = self._get_text_value(self.cc_person_responsibility)
        self.cc_context["cc_penalty"] = self._get_text_value(self.cc_penalty)

    def _get_text_value(self, widget):
        try:
            return widget.get("1.0", "end-1c").strip()
        except TypeError:
            return widget.get().strip()

    def _get_date_value(self, widget, date_format="%d.%m.%Y"):
        value = widget.get()
        if value:
            try:
                return datetime.strptime(value, '%d/%m/%Y').strftime(date_format)
            except ValueError:
                pass
        return ""

    def _build_doc_identifier(self):
        selected_person_id = self._extract_selected_person_id()
        project_id = self.all_projects.get()
        task_starting_date = self._get_date_value(self.cc_task_start_date, date_format="%Y_%m_%d")
        if task_starting_date:
            return f"{task_starting_date}_{project_id}_{selected_person_id}"
        else:
            return f"no_start_date_{project_id}_{selected_person_id}"

    def _extract_selected_person_id(self):
        selected_person = self.persons_dropdown.get()
        return selected_person.split(')')[0].strip('(') if selected_person else ""

    def _populate_project_context(self):
        selected_project = self.all_projects.get()
        project = self.data_mgr.get_project_by_id(selected_project)
        if project:
            project_lead_id = project.get('project_lead')
            if project_lead_id:
                pl = self.data_mgr.get_coworker_by_id(project_lead_id)
                if pl:
                    self.cc_context["project_leader_names"] = pl.get('names', 'Unknown')
                    self.cc_context["project_leader_title"] = pl.get('titles', 'Unknown')
                    self.cc_context["project_leader_full_name"] = pl.get('full_name', 'Unknown')
        self.cc_context["project_info"] = project.get('description', 'Unknown') if project else 'Unknown'
        self.cc_context["project_nb"] = project.get('number', 'Unknown') if project else 'Unknown'

    def _populate_person_context(self):
        person_id = self._extract_selected_person_id()
        if not person_id:
            return

        person = self.data_mgr.get_coworker_by_id(person_id)
        if not person:
            return

        self.cc_context["person_full_name"] = person.get('full_name', 'Unknown')
        self.cc_context["person_titles"] = person.get('titles', 'Unknown')
        self.cc_context["person_egn"] = person.get('egn', 'Unknown')
        person_address = person.get('address', 'Unknown')
        self.cc_context["person_address"] = person_address.get('main_line', 'Unknown') if isinstance(person_address, dict) else person_address
        self.cc_context["person_zip"] = person_address.get('zip', 'Unknown') if isinstance(person_address, dict) else 'Unknown'
        self.cc_context["person_city"] = person_address.get('city', 'Unknown') if isinstance(person_address, dict) else 'Unknown'
        self.cc_context["person_municipality"] = person_address.get('municipality', 'Unknown') if isinstance(person_address, dict) else 'Unknown'
        person_id_data = person.get('id', {})
        self.cc_context["person_id_number"] = person_id_data.get('number', 'Unknown')
        self.cc_context["person_id_issuer"] = person_id_data.get('issuer', 'Unknown')
        self.cc_context["person_id_issue_date"] = person_id_data.get('issue_date', 'Unknown')
        self.cc_context["person_bank_account"] = person.get('iban', 'Unknown')

    def final_action(self):
        project_id = self.all_projects.get()
        person_id = self._extract_selected_person_id()
        cc_title = self.cc_context["doc_date_and_ids_identifier"]
        new_civil_contract = {
            cc_title: {
                "project_id": project_id,
                "cc_task": self.cc_context["cc_task"],
                "cc_number": "",
                "person_id": person_id,
                "cc_task_start_date": self.cc_context["cc_task_start_date"],
                "cc_task_end_date": self.cc_context["cc_task_end_date"],
                "doc_date_and_ids_identifier": cc_title,
                "status": CCStatus.GENERATED.name
            }
        }
        self.data_mgr.save_new_civil_contract(new_civil_contract)