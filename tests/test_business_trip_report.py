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

from classes.docs.business_trip.BusinessTripReport import BusinessTripReport


class DummyWidget:
    def __init__(self, value=""):
        self.value = value

    def get(self, *args):
        if args:
            return self.value
        raise TypeError("text widget requires arguments")


class DummyVar:
    def __init__(self, value=0):
        self.value = value

    def get(self):
        return self.value


class DummyDataMgr:
    def __init__(self):
        self.data = {"business_trips": {"BT1": {"bt_order_number": "", "reported_ids": [], "person_ids": ["P1"], "status": "READY_TO_REPORT"}}}
        self.saved = False

    def save_data(self):
        self.saved = True


class BusinessTripReportTests(unittest.TestCase):
    def test_final_action_persists_order_number(self):
        report = BusinessTripReport.__new__(BusinessTripReport)
        report.current_bts_to_report = {"BT1": {"bt_order_number": "", "reported_ids": [], "person_ids": ["P1"], "status": "READY_TO_REPORT"}}
        report.business_trips_dropdown = type("Dropdown", (), {"get": lambda self: "BT1"})()
        report.bt_context = {"selected_person_id": "P1", "leader_id": "P1"}
        report.generate_only_report_var = DummyVar(0)
        report.uploaded_files = []
        report.input_fields = [("bt_order_number", None, DummyWidget("ABC-123"))]
        report._get_report_output_folder = lambda: "output"
        report.data_mgr = DummyDataMgr()

        report.final_action()

        self.assertEqual(report.current_bts_to_report["BT1"]["bt_order_number"], "ABC-123")
        self.assertEqual(report.data_mgr.data["business_trips"]["BT1"]["bt_order_number"], "ABC-123")
        self.assertTrue(report.data_mgr.saved)


if __name__ == "__main__":
    unittest.main()
