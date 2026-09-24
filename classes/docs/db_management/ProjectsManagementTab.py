from classes.docs.db_management.BaseManagementTab import BaseManagementTab


class ProjectsManagementTab(BaseManagementTab):
    def __init__(self, parent, data_mgr):
        default_fields = {
            "name": "",
            "description": "",
            "start_date": "",
            "end_date": "",
            "team": "",
            "project_lead": "",
            "number": "",
        }
        super().__init__(parent, data_mgr, "projects", "Projects", default_fields)
