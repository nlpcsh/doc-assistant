from tkinter import ttk

from classes.docs.db_management.CoWorkersManagementTab import CoWorkersManagementTab
from classes.docs.db_management.PasswordChangeTab import PasswordChangeTab
from classes.docs.db_management.ProjectsManagementTab import ProjectsManagementTab


class DBManagementTab(ttk.Frame):
    def __init__(self, parent, data_mgr):
        super().__init__(parent)
        self.data_mgr = data_mgr

        sub_nb = ttk.Notebook(self)
        sub_nb.pack(expand=True, fill="both")

        labels = data_mgr.get_labels()
        sub_nb.add(CoWorkersManagementTab(sub_nb, data_mgr), text=labels["tabs"].get("db_management_co_workers", "Co-workers"))
        sub_nb.add(ProjectsManagementTab(sub_nb, data_mgr), text=labels["tabs"].get("db_management_projects", "Projects"))
        sub_nb.add(PasswordChangeTab(sub_nb, data_mgr), text=labels["tabs"].get("db_management_password_change", "Password"))
