from classes.tabs.BaseDocTab import BaseDocTab

class CivilContractTab(BaseDocTab):
    def __init__(self, parent, labels, base_dir):
        super().__init__(parent, labels, base_dir, "contract_template.docx")

        # 1. Add the dropdown using the list 'names_list' from your JSON
        self.combo_name = self.add_dropdown("select_person", self.labels["names_list"])

        # 2. Add other fields as usual
        self.ent_ssn = self.add_field("ssn")
        self.ent_phone = self.add_field("phone")

        self.add_common_buttons("gen_contract")

    def get_context(self):
        # IMPORTANT: Use .get() on the combo box to grab the selected name
        return {
            'name': self.combo_name.get(), 
            'ssn': self.ent_ssn.get(),
            'phone': self.ent_phone.get()
        }