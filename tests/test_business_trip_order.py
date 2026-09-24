import os
import sys
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

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
    def __init__(self, selected_indices=(), items=None):
        self.selected_indices = selected_indices
        self.items = items or ["(FLS) Филип Стаматов"]

    def curselection(self):
        return self.selected_indices

    def get(self, *args):
        if args and isinstance(args[0], int) and args[0] < len(self.items):
            return self.items[args[0]]
        raise TypeError("listbox index must be int")


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

    def test_get_latest_project_id_accepts_day_month_year_dates(self):
        order = BusinessTripOrder.__new__(BusinessTripOrder)
        order.projects_list = ["P01"]
        order.data_mgr = types.SimpleNamespace(
            get_project_by_id=lambda pid: {"end_date": "15.09.2033"}
        )

        self.assertEqual(order.get_latest_project_id(), "P01")

    def test_get_context_includes_bt_destination_obj(self):
        order = BusinessTripOrder.__new__(BusinessTripOrder)
        order.bt_purpose_field = DummyTextWidget("Trip purpose")
        order.bt_destination_field = DummyWidget("София - Хелзинки - София")
        order.persons_multiselect = DummyListbox((0,))
        order.date_from = DummyWidget("08/08/2026")
        order.date_to = DummyWidget("09/08/2026")
        order.bt_travel_with_var = DummyWidget()
        order.bt_travel_with_var.get = lambda: False
        order.input_fields = [
            ("bt_destination", None, order.bt_destination_field),
            ("bt_purpose", None, order.bt_purpose_field),
            ("bt_euro_per_day", None, DummyWidget("56")),
            ("bt_nights_max_value", None, DummyWidget("207")),
            ("bt_other_expences", None, DummyWidget("")),
        ]
        order.labels = {
            "fields": {},
            "messages": {"account_on": "За сметка на ", "third_party": "приемащата страна."},
            "multiselect": {"travel_with": ["кола", "самолет"]}
        }
        order.all_projects = DummyWidget("P001")
        order.selected_person_ids = ["FLS"]
        order.selected_persons = []
        order.data_mgr = types.SimpleNamespace(
            get_project_by_id=lambda pid: {"project_lead": "FLS", "description": "Project desc"},
            get_coworker_by_id=lambda cid: {"titles": "гл. ас.", "names": "Филип", "full_name": "Филип Стаматов", "department": "АФ", "work_place": "ИУ"}
        )

        class DummySelector:
            def get_destination_obj(self):
                return {"from": ["България", "София"], "to": ["Финландия", "Хелзинки"]}

        order.select_destination_section = DummySelector()

        context = order.get_context()
        self.assertIn("bt_destination_obj", context)
        self.assertEqual(
            context["bt_destination_obj"],
            {"from": ["България", "София"], "to": ["Финландия", "Хелзинки"]}
        )

    def test_on_destination_selection_changed_updates_destination_field_and_checkbox_fields(self):
        order = BusinessTripOrder.__new__(BusinessTripOrder)

        class EntryWidget:
            def __init__(self):
                self.val = ""
            def delete(self, *args):
                self.val = ""
            def insert(self, idx, val):
                self.val = str(val)
            def get(self, *args):
                return self.val

        order.bt_destination_field = EntryWidget()
        euro_entry = EntryWidget()
        nights_entry = EntryWidget()

        order.input_fields = [
            ("bt_destination", None, order.bt_destination_field),
            ("bt_euro_per_day", None, euro_entry),
            ("bt_nights_max_value", None, nights_entry),
        ]
        order.ui_mgr = types.SimpleNamespace(
            set_field_value=lambda o, k, v: [w.delete() or w.insert(0, v) for key, _, w in o.input_fields if key == k]
        )

        order.bt_euro_per_day_var = DummyWidget()
        order.bt_euro_per_day_var.get = lambda: True

        order.bt_nights_max_value_var = DummyWidget()
        order.bt_nights_max_value_var.get = lambda: True

        selector = types.SimpleNamespace(
            from_city="София",
            to_city="Хелзинки",
            daily="56",
            accommodation="207"
        )

        order.on_destination_selection_changed(selector)

        self.assertEqual(order.bt_destination_field.get(), "София - Хелзинки - София")
        self.assertEqual(euro_entry.get(), "56")
        self.assertEqual(nights_entry.get(), "207")


if __name__ == "__main__":
    unittest.main()
