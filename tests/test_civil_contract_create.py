import os
import sys
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

base_doc_stub = types.ModuleType("classes.docs.BaseDoc")
class BaseDoc:
    pass
base_doc_stub.BaseDoc = BaseDoc
sys.modules["classes.docs.BaseDoc"] = base_doc_stub

exporter_stub = types.ModuleType("classes.docs.civil_contract.CivilContractExporter")
class CivilContractExporter:
    @staticmethod
    def build_civil_contract_payload(*args, **kwargs):
        return {}
exporter_stub.CivilContractExporter = CivilContractExporter
sys.modules["classes.docs.civil_contract.CivilContractExporter"] = exporter_stub

enums_stub = types.ModuleType("enums.Enums")
class CCStatus:
    pass
enums_stub.CCStatus = CCStatus
sys.modules["enums.Enums"] = enums_stub

from classes.docs.civil_contract.CivilContractCreate import CivilContractCreate

class DummyWidget:
    def __init__(self, value=""):
        self.value = value

    def get(self, *args):
        if len(args) == 0:
            return self.value
        return self.value

class DummyTextWidget(DummyWidget):
    def get(self, *args):
        if args:
            return self.value
        raise TypeError("text widget requires args")

class CivilContractCreateValidationTests(unittest.TestCase):
    def test_reports_missing_required_fields(self):
        contract = CivilContractCreate.__new__(CivilContractCreate)
        contract.cc_start_date = DummyWidget("")
        contract.cc_task = DummyTextWidget("   ")
        contract.cc_task_start_date = DummyWidget("")
        contract.cc_task_end_date = DummyWidget("")
        contract.cc_payment_due_date = DummyWidget("")
        contract.cc_task_amount = DummyWidget("")
        contract.cc_task_amount_in_words = DummyWidget("")
        contract.cc_person_responsibility = DummyTextWidget("")
        contract.cc_penalty = DummyTextWidget("")
        contract.labels = {"fields": {}}

        missing = contract.get_missing_required_fields()
        self.assertIn("cc_start_date", missing)
        self.assertIn("cc_task", missing)
        self.assertIn("cc_task_start_date", missing)
        self.assertIn("cc_task_end_date", missing)
        self.assertIn("cc_payment_due_date", missing)
        self.assertIn("cc_task_amount", missing)
        self.assertIn("cc_task_amount_in_words", missing)
        self.assertIn("cc_person_responsibility", missing)
        self.assertIn("cc_penalty", missing)

    def test_accepts_valid_text_and_date_fields(self):
        contract = CivilContractCreate.__new__(CivilContractCreate)
        contract.cc_start_date = DummyWidget("10/08/2026")
        contract.cc_task = DummyTextWidget("Do work")
        contract.cc_task_start_date = DummyWidget("10/08/2026")
        contract.cc_task_end_date = DummyWidget("11/08/2026")
        contract.cc_payment_due_date = DummyWidget("15/08/2026")
        contract.cc_task_amount = DummyWidget("1000")
        contract.cc_task_amount_in_words = DummyWidget("One thousand")
        contract.cc_person_responsibility = DummyTextWidget("Complete tasks")
        contract.cc_penalty = DummyTextWidget("None")
        contract.labels = {"fields": {}}

        self.assertEqual(contract.get_missing_required_fields(), [])

if __name__ == "__main__":
    unittest.main()
