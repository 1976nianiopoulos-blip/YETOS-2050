"""Regression checks for the NASA Climate 2050 Lens."""

import unittest
from s2050_climate_lens import load_2050


class TestClimate2050(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df, cls.meta, cls.stats = load_2050()

    def test_01_daily_calendar(self):
        self.assertEqual(len(self.df), 365)
        self.assertTrue(self.df["date"].is_unique)
        self.assertEqual(
            self.df["date"].iloc[0].strftime("%Y-%m-%d"),
            "2050-01-01",
        )
        self.assertEqual(
            self.df["date"].iloc[-1].strftime("%Y-%m-%d"),
            "2050-12-31",
        )

    def test_02_provenance(self):
        self.assertEqual(self.meta["model"], "MPI-ESM1-2-HR")
        self.assertEqual(self.meta["scenario"], "ssp245")
        self.assertEqual(self.meta["year"], 2050)
        self.assertEqual(self.meta["grid_latitude"], 52.625)
        self.assertEqual(self.meta["grid_longitude"], -8.625)

    def test_03_original_csv_integrity(self):
        expected = (
            "9EF5888C7797C84B3C669DB0E252839"
            "F7E6BA241B23BA73AF045292039A02220"
        )
        self.assertEqual(
            self.meta["csv_sha256"].upper(), expected
        )

    def test_04_precipitation_statistics(self):
        s = self.stats
        self.assertAlmostEqual(s["annual_mm"], 1179.33, places=2)
        self.assertAlmostEqual(s["max_daily_mm"], 29.08, places=2)
        self.assertEqual(s["days_below_1mm"], 144)
        self.assertEqual(s["days_at_least_10mm"], 23)
        self.assertEqual(s["days_at_least_15mm"], 5)
        self.assertEqual(s["days_at_least_20mm"], 2)
        self.assertEqual(s["days_at_least_25mm"], 2)

    def test_05_driest_60_days(self):
        s = self.stats
        self.assertEqual(s["driest_60_start"], "2050-04-17")
        self.assertEqual(s["driest_60_end"], "2050-06-15")
        self.assertAlmostEqual(s["driest_60_mm"], 119.27, places=2)
        self.assertEqual(s["longest_below_1mm"], 12)