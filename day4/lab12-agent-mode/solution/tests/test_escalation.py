import json
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from kaveridesk.service import Desk
from kaveridesk.store import Store

DATA = Path(__file__).resolve().parent.parent / "data"
NOW = datetime(2026, 11, 20, 11, 0)


class TestEscalation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for f in DATA.glob("*.json"):
            shutil.copy(f, self.tmp)
        self.d = Desk(Store(self.tmp), NOW)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_escalates_at_risk_and_breached_to_leads(self):
        done = self.d.escalate()
        self.assertEqual([(t.id, new) for t, _, _, new in done],
                         [("INC-1003", "A05"), ("INC-1009", "A01"), ("INC-1013", "A04"), ("INC-1005", "A07")])
        t = Desk(Store(self.tmp), NOW).get("INC-1009")
        self.assertTrue(t.escalated)
        self.assertEqual(t.assignee, "A01")
        self.assertIn("was assigned to A02", t.notes[-1])

    def test_dry_run_saves_nothing(self):
        before = (Path(self.tmp) / "tickets.json").read_text()
        self.assertEqual(len(self.d.escalate(dry_run=True)), 4)
        self.assertEqual((Path(self.tmp) / "tickets.json").read_text(), before)

    def test_second_run_escalates_nothing(self):
        self.d.escalate()
        self.assertEqual(Desk(Store(self.tmp), NOW).escalate(), [])

    def test_old_json_without_field_loads(self):
        rows = json.loads((Path(self.tmp) / "tickets.json").read_text())
        self.assertTrue(all("escalated" not in r for r in rows))
        self.assertFalse(self.d.get("INC-1001").escalated)


if __name__ == "__main__":
    unittest.main()
