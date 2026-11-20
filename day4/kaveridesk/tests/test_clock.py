import unittest
from datetime import date, datetime

from kaveridesk.clock import add_bh, bh_between


class TestClock(unittest.TestCase):
    def test_add_within_day(self):
        self.assertEqual(add_bh(datetime(2026, 11, 16, 10, 0), 4), datetime(2026, 11, 16, 14, 0))

    def test_add_over_weekend(self):
        self.assertEqual(add_bh(datetime(2026, 11, 20, 16, 0), 4), datetime(2026, 11, 23, 11, 0))

    def test_between_same_day(self):
        self.assertEqual(bh_between(datetime(2026, 11, 16, 9, 0), datetime(2026, 11, 16, 12, 30)), 3.5)

    def test_holiday_skipped(self):
        h = {date(2026, 11, 27)}
        self.assertEqual(add_bh(datetime(2026, 11, 26, 17, 0), 2, h), datetime(2026, 11, 30, 10, 0))


if __name__ == "__main__":
    unittest.main()
