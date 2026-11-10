import tempfile
import unittest
from pathlib import Path
from database import Database
from report import make_report

class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp.name) / "test.db")

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_price_drop_and_no_duplicate(self):
        pid = self.db.add_product("Мышь", 100, 4.5, "demo://one", "Магазин",
                                  "2026-01-01T00:00:00Z")
        self.db.add_product("Мышь", 75, 4.5, "demo://one", "Магазин",
                            "2026-01-02T00:00:00Z")
        self.assertEqual(self.db.stats()["count"], 1)
        self.assertEqual(len(self.db.price_history(pid)), 2)
        self.assertEqual(self.db.top_discounts()[0]["drop_pct"], 25.0)
        self.assertEqual(len(self.db.find_cheaper(80, "мыш")), 1)
        self.assertIn("Товаров: 1", make_report(self.db))

    def test_no_false_discount_on_increase(self):
        self.db.add_product("SSD", 100, 4, "demo://ssd", "Store",
                            "2026-01-01T00:00:00Z")
        self.db.add_product("SSD", 110, 4, "demo://ssd", "Store",
                            "2026-01-02T00:00:00Z")
        self.assertEqual(len(self.db.top_discounts()), 0)

if __name__ == "__main__":
    unittest.main()
