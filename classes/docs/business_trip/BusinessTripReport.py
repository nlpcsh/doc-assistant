from classes.docs.BaseDoc import BaseDoc

class BusinessTripReport(BaseDoc):
    def __init__(self, parent, data_mgr):
        super().__init__(parent, data_mgr, "business_trip", ["business_trip_report.docx"])

        self.ui_mgr.add_tab_title(self, "bt_report")
        self.ui_mgr.add_dropdown(self, "projects", list(self.data_mgr.data['projects'].keys()))

        # self.ent_company = self.add_field("company")
        # self.ent_rep = self.add_field("rep")
        self.ui_mgr.add_common_buttons(self, "gen_business_trip")

    def final_action(self):
        pass

    def get_context(self):

        return {}