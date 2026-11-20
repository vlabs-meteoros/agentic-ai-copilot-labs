import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from kaveridesk.service import Desk
from kaveridesk.store import Store

DATA = Path(__file__).resolve().parent.parent / "data"
NOW = datetime(2026, 11, 20, 11, 0)


class TestDesk(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for f in DATA.glob("*.json"):
            shutil.copy(f, self.tmp)
        self.d = Desk(Store(self.tmp), NOW)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_breaches(self):
        self.assertEqual([t.id for t in self.d.breaches()], ["INC-1003", "INC-1009", "INC-1013"])

    def test_new_ticket_is_saved(self):
        t = self.d.new("Mouse not working", "IT", "P4", "test.user")
        again = Desk(Store(self.tmp), NOW)
        self.assertEqual(again.get(t.id).title, "Mouse not working")

    def test_unknown_category(self):
        with self.assertRaises(ValueError):
            self.d.new("Coffee machine empty", "Pantry", "P4", "test.user")


if __name__ == "__main__":
    unittest.main()
