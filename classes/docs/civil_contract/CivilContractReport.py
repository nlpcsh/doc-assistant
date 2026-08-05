from classes.docs.BaseDoc import BaseDoc

class CivilContractReport(BaseDoc):
    def __init__(self, parent, data_mgr):
        super().__init__(parent, data_mgr, "civil_contract", ["civil_contract_person_report.docx", "cc_report_of_findings.docx"])
        self.setup_ui_components()

    def setup_ui_components(self):
        self.ui_mgr.add_common_buttons(self, "gen_contract_report", container=self)
