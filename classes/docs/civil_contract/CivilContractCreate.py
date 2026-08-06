
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
