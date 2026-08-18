import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from classes.DataMgr import DataMgr
from enums.Enums import BTStatus


class DataMgrBusinessTripStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        base_dir = Path(self.temp_dir.name)
        (base_dir / "data").mkdir()
        (base_dir / "settings").mkdir()
        (base_dir / "data" / "data.json").write_text(
            json.dumps({
                "business_trips": {
                    "generated": {"status": "GENERATED"},
                    "ready": {"status": "READY_TO_REPORT"},
                    "reported": {"status": "PL_REPORTED"},
                },
                "projects": {},
                "co_workers": {}
            }),
            encoding="utf-8",
        )
        (base_dir / "settings" / "labels.json").write_text("{}", encoding="utf-8")
        self.data_mgr = DataMgr(str(base_dir))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_returns_trips_for_multiple_enum_statuses(self):
        result = self.data_mgr.get_all_bussiness_trips_by_status(
            [BTStatus.READY_TO_REPORT, BTStatus.PL_REPORTED]
        )

        self.assertEqual(set(result), {"ready", "reported"})

    def test_accepts_mixed_status_representations(self):
        result = self.data_mgr.get_all_bussiness_trips_by_status(
            [BTStatus.READY_TO_REPORT, "GENERATED"]
        )

        self.assertEqual(set(result), {"generated", "ready"})

    def test_empty_or_unknown_status_list_returns_no_trips(self):
        self.assertEqual(self.data_mgr.get_all_bussiness_trips_by_status([]), {})
        self.assertEqual(
            self.data_mgr.get_all_bussiness_trips_by_status([BTStatus.REPORTED]), {}
        )

    def test_scalar_status_behavior_is_preserved(self):
        self.assertEqual(
            set(self.data_mgr.get_all_bussiness_trips_by_status(BTStatus.READY_TO_REPORT)),
            {"ready"},
        )
        self.assertEqual(
            set(self.data_mgr.get_all_bussiness_trips_by_status("PL_REPORTED")),
            {"reported"},
        )
        self.assertEqual(self.data_mgr.get_all_bussiness_trips_by_status(3), {})

    def test_lookup_helpers_return_expected_values(self):
        self.data_mgr.data["projects"] = {"proj-1": {"name": "Alpha"}}
        self.data_mgr.data["co_workers"] = {"cw-1": {"full_name": "John Doe"}}
        self.data_mgr.preferences["output_folders"] = {"common": "out/", "business_trip": "bt/"}
        self.data_mgr.save_data()

        self.assertEqual(self.data_mgr.get_project_by_id("proj-1"), {"name": "Alpha"})
        self.assertEqual(self.data_mgr.get_coworker_by_id("cw-1"), {"full_name": "John Doe"})
        self.assertEqual(self.data_mgr.get_all_projects(), ["proj-1"])
        self.assertEqual(self.data_mgr.get_output_folders(), {"common": "out/", "business_trip": "bt/"})

    def test_save_new_methods_persist_data_to_disk(self):
        self.data_mgr.save_new_bussiness_trip({"trip-1": {"status": "GENERATED"}})
        self.data_mgr.save_new_civil_contract({"contract-1": {"status": "GENERATED"}})

        data_file = Path(self.data_mgr.base_dir) / "data" / "data.json"
        saved_data = json.loads(data_file.read_text(encoding="utf-8"))

        self.assertIn("trip-1", saved_data["business_trips"])
        self.assertIn("contract-1", saved_data["civil_contracts"])


if __name__ == "__main__":
    unittest.main()
