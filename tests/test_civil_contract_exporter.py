import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from classes.docs.civil_contract.CivilContractExporter import CivilContractExporter
from enums.Enums import CCStatus


class CivilContractExporterTests(unittest.TestCase):
    def test_build_civil_contract_payload_includes_expected_properties(self):
        payload = CivilContractExporter.build_civil_contract_payload(
            contract_title="20240101_proj_123",
            project_id="proj-1",
            person_id="person-1",
            context={
                "cc_task": "Task description",
                "cc_task_start_date": "01.01.2024",
                "cc_task_end_date": "02.01.2024",
            },
        )

        self.assertEqual(payload["project_id"], "proj-1")
        self.assertEqual(payload["cc_task"], "Task description")
        self.assertEqual(payload["person_id"], "person-1")
        self.assertEqual(payload["status"], CCStatus.GENERATED.name)
        self.assertEqual(payload["doc_date_and_ids_identifier"], "20240101_proj_123")


if __name__ == "__main__":
    unittest.main()
