import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from Helpers import Helpers


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


if __name__ == "__main__":
    unittest.main()
