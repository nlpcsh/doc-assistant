import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from Helpers import Helpers


class ExportHelpersTests(unittest.TestCase):
    def test_build_common_export_payload_merges_shared_fields(self):
        payload = Helpers.build_common_export_payload(
            document_id="doc-1",
            project_id="project-1",
            status="GENERATED",
            extra_fields={"bt_heading": "Trip"},
        )

        self.assertEqual(payload["project_id"], "project-1")
        self.assertEqual(payload["doc_date_and_ids_identifier"], "doc-1")
        self.assertEqual(payload["status"], "GENERATED")
        self.assertEqual(payload["bt_heading"], "Trip")


if __name__ == "__main__":
    unittest.main()
