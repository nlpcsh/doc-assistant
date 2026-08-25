import os
import sys
import tkinter as tk
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from ui.CountryCitySelector import CountryCitySelector


class CountryCitySelectorTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_initialization_has_no_text_fields_and_stores_properties(self):
        selector = CountryCitySelector(self.root)
        self.assertFalse(hasattr(selector, "text_fields"))
        self.assertFalse(hasattr(selector, "text_frame"))
        self.assertEqual(selector.from_country, "България")
        self.assertEqual(selector.from_city, "София")
        self.assertEqual(selector.to_country, "")
        self.assertEqual(selector.to_city, "")
        self.assertEqual(selector.accommodation, "170")
        self.assertEqual(selector.daily, "46")
        self.assertEqual(
            selector.get_destination_obj(),
            {"from": ["България", "София"], "to": ["", ""]}
        )

    def test_second_pair_selection_updates_properties_and_rates(self):
        callback_called = []
        selector = CountryCitySelector(
            self.root,
            on_selection_change=lambda s: callback_called.append(True)
        )

        selector.set_selection(
            from_country="България",
            from_city="София",
            to_country="Финландия",
            to_city="Хелзинки"
        )

        self.assertEqual(selector.from_country, "България")
        self.assertEqual(selector.from_city, "София")
        self.assertEqual(selector.to_country, "Финландия")
        self.assertEqual(selector.to_city, "Хелзинки")
        self.assertEqual(selector.accommodation, "207")
        self.assertEqual(selector.daily, "56")
        self.assertEqual(selector.destination, "София - Хелзинки - София")
        self.assertEqual(
            selector.get_destination_obj(),
            {"from": ["България", "София"], "to": ["Финландия", "Хелзинки"]}
        )
        self.assertTrue(len(callback_called) > 0)


if __name__ == "__main__":
    unittest.main()
