
from datetime import datetime

from classes.docs.BaseDoc import BaseDoc

class CivilContractCreate(BaseDoc):
    def __init__(self, parent, data_mgr):
        super().__init__(parent, data_mgr, "civil_contract", ["civil_contract_create.docx", "cc_pl_report.docx"])
        self.setup_ui_components()
        self.preselect_latest_project()

    def setup_ui_components(self):
        self.ui_mgr.add_tab_title(self, "civil_contract_create")
        self.bt_context = {}
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
        self.bt_context = {}
        self.bt_context["cc_task"] = self.cc_task.get()
        # get date in format dd.mm.yyyy
        self.bt_context["cc_start_date"] = self.cc_start_date.get().strftime("%d.%m.%Y") if self.cc_start_date.get() else ""
        self.bt_context["cc_task_start_date"] = self.cc_task_start_date.get().strftime("%d.%m.%Y") if self.cc_task_start_date.get() else ""
        self.bt_context["cc_task_end_date"] = self.cc_task_end_date.get().strftime("%d.%m.%Y") if self.cc_task_end_date.get() else ""
        self.bt_context["cc_payment_due_date"] = self.cc_payment_due_date.get().strftime("%d.%m.%Y") if self.cc_payment_due_date.get() else ""
        self.bt_context["cc_task_amount"] = self.cc_task_amount.get()
        self.bt_context["cc_task_amount_in_words"] = self.cc_task_amount_in_words.get()
        self.bt_context["cc_person_responsibility"] = self.cc_person_responsibility.get()
        self.bt_context["cc_penalty"] = self.cc_penalty.get()

        return self.bt_context