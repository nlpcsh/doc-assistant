import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from classes.docs.business_trip.BusinessTripExporter import BusinessTripExporter
from enums.Enums import BTStatus


class BusinessTripExporterTests(unittest.TestCase):
    def test_build_business_trip_payload_includes_all_expected_properties(self):
        payload = BusinessTripExporter.build_business_trip_payload(
            bt_title="20240101_test_123",
            project_id="proj-1",
            context={
                "bt_purpose": "Trip purpose",
                "bt_from": "01/01/2024",
                "bt_to": "02/01/2024",
                "bt_travel_with": "car",
                "bt_day_money_from": "day source",
                "bt_nights_money_from": "night source",
                "bt_travel_money_from": "travel source",
                "bt_destination": "Sofia",
                "bt_euro_per_day": "1",
                "bt_nights_max_value": "1",
                "bt_other_expences": "1",
                "bt_contract_info": "Contract",
                "leader_titles": "Dr",
                "leader_names": "Name",
                "leader_full_name": "Full Name",
                "leader_work_place": "Office",
                "bt_all_persons": "All persons",
            },
            selected_person_ids=["p1", "p2"],
            based_on="old-id",
        )

        self.assertEqual(payload["project_id"], "proj-1")
        self.assertEqual(payload["bt_heading"], "Trip purpose")
        self.assertEqual(payload["person_ids"], ["p1", "p2"])
        self.assertEqual(payload["based_on"], "old-id")
        self.assertEqual(payload["status"], BTStatus.GENERATED.name)
        self.assertEqual(payload["doc_date_and_ids_identifier"], "20240101_test_123")


if __name__ == "__main__":
    unittest.main()
