import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from classes.digisign.signing_utils import build_signature_rect


class SigningUtilsTests(unittest.TestCase):
    def test_build_signature_rect_uses_click_center(self):
        rect = build_signature_rect(
            page_width=612,
            page_height=792,
            click_x=100,
            click_y=100,
            signature_width=100,
            signature_height=50,
        )

        self.assertAlmostEqual(rect.x0, 50)
        self.assertAlmostEqual(rect.x1, 150)
        self.assertAlmostEqual(rect.y0, 667)
        self.assertAlmostEqual(rect.y1, 717)


if __name__ == "__main__":
    unittest.main()
