import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from Helpers import Helpers
from classes.docs.BaseDoc import BaseDoc


class ReportAttachmentTests(unittest.TestCase):
    def test_copy_files_to_folder_preserves_file_names_and_creates_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            src_dir = Path(temp_dir) / "src"
            dest_dir = Path(temp_dir) / "reports" / "trip"
            src_dir.mkdir(parents=True, exist_ok=True)
            src_file = src_dir / "note.txt"
            src_file.write_text("hello", encoding="utf-8")

            copied_files = Helpers.copy_files_to_folder([str(src_file)], str(dest_dir))

            self.assertEqual(len(copied_files), 1)
            self.assertTrue(dest_dir.exists())
            self.assertTrue((dest_dir / "note.txt").exists())
            self.assertEqual((dest_dir / "note.txt").read_text(encoding="utf-8"), "hello")

    def test_build_output_path_uses_data_mgr_output_folders(self):
        base_doc = object.__new__(BaseDoc)
        base_doc.output_folder = "business_trip"
        base_doc.data_mgr = type(
            "DataMgrStub",
            (),
            {
                "get_output_folders": lambda self: {
                    "common": "/tmp/common/",
                    "business_trip": "/trip/",
                }
            },
        )()

        context = {
            "doc_date_and_ids_identifier": "20240101",
            "sub_folder": "/draft",
        }

        self.assertEqual(
            base_doc._build_output_path(context),
            "/tmp/common//trip/20240101/draft",
        )


if __name__ == "__main__":
    unittest.main()
