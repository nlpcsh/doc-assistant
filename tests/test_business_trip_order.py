import os
import sys
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

if "docxtpl" not in sys.modules:
    docxtpl_stub = types.ModuleType("docxtpl")
    docxtpl_stub.DocxTemplate = object
    sys.modules["docxtpl"] = docxtpl_stub

base_doc_stub = types.ModuleType("classes.docs.BaseDoc")
class BaseDoc:
    pass
base_doc_stub.BaseDoc = BaseDoc
sys.modules["classes.docs.BaseDoc"] = base_doc_stub

exporter_stub = types.ModuleType("classes.docs.business_trip.BusinessTripExporter")
class BusinessTripExporter:
    @staticmethod
    def build_business_trip_payload(*args, **kwargs):
        return {}
exporter_stub.BusinessTripExporter = BusinessTripExporter
sys.modules["classes.docs.business_trip.BusinessTripExporter"] = exporter_stub

from classes.docs.business_trip.BusinessTripOrder import BusinessTripOrder


class DummyWidget:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value


class DummyTextWidget:
    def __init__(self, value=""):
        self.value = value

    def get(self, *args):
        if args:
            return self.value
        raise TypeError("text widget requires arguments")


class DummyListbox:
    def __init__(self, selected_indices=()):
        self.selected_indices = selected_indices

    def curselection(self):
        return self.selected_indices

    def get(self, *args):
        raise Exception("listbox")


class BusinessTripOrderValidationTests(unittest.TestCase):
    def test_reports_missing_required_fields(self):
        order = BusinessTripOrder.__new__(BusinessTripOrder)
        order.bt_purpose_field = DummyTextWidget("   ")
        order.bt_destination_field = DummyWidget("")
        order.persons_multiselect = DummyWidget("")
        order.date_from = DummyWidget("")
        order.date_to = DummyWidget("08/08/2026")

        self.assertEqual(order.get_missing_required_fields(), ["bt_purpose", "bt_destination", "persons_multiselect", "bt_from"])

    def test_accepts_non_empty_text_widget_value(self):
        order = BusinessTripOrder.__new__(BusinessTripOrder)
        order.bt_purpose_field = DummyTextWidget("Trip purpose")
        order.bt_destination_field = DummyWidget("Sofia")
        order.persons_multiselect = DummyListbox((0,))
        order.date_from = DummyWidget("08/08/2026")
        order.date_to = DummyWidget("09/08/2026")

        self.assertEqual(order.get_missing_required_fields(), [])

    def test_marks_person_multiselect_missing_when_nothing_is_selected(self):
        order = BusinessTripOrder.__new__(BusinessTripOrder)
        order.bt_purpose_field = DummyTextWidget("Trip purpose")
        order.bt_destination_field = DummyWidget("Sofia")
        order.persons_multiselect = DummyListbox(())
        order.date_from = DummyWidget("08/08/2026")
        order.date_to = DummyWidget("09/08/2026")

        self.assertIn("persons_multiselect", order.get_missing_required_fields())


if __name__ == "__main__":
    unittest.main()
