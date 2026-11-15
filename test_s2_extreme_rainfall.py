import unittest
from collections import defaultdict
from math import inf, nan

from s2_extreme_rainfall import run_s2
from s1_irrigation import SOILS


class TestS2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.summaries = run_s2()

    def test_row_counts(self):
        self.assertEqual(len(self.rows), 1460)
        self.assertEqual(len(self.summaries), 4)
        counts = defaultdict(int)
        for r in self.rows:
            counts[(r["soil"], r["scenario"])] += 1
        self.assertTrue(all(n == 365 for n in counts.values()))

    def test_only_one_day_changes_rainfall(self):
        for soil in SOILS:
            base = {
                r["date"]: r for r in self.rows
                if r["soil"] == soil
                and r["scenario"] == "Baseline"
            }
            storm = {
                r["date"]: r for r in self.rows
                if r["soil"] == soil
                and r["scenario"] == "S2_synthetic_storm"
            }

            for day in base:
                expected = (
                    120.0 if day == "2023-10-20"
                    else 0.0
                )
                self.assertAlmostEqual(
                    storm[day]["P_total_mm"]
                    - base[day]["P_total_mm"],
                    expected
                )
                self.assertEqual(
                    storm[day]["P_added_mm"], expected
                )
                self.assertEqual(
                    storm[day]["ET0_A10_mm"],
                    base[day]["ET0_A10_mm"]
                )

    def test_mass_balance_and_storage(self):
        for row in self.rows:
            self.assertLessEqual(
                abs(row["residual_mm"]), 1e-8
            )
            soil = SOILS[row["soil"]]
            self.assertGreaterEqual(
                row["S_end_mm"], soil["WP"] - 1e-7
            )
            self.assertLessEqual(
                row["S_end_mm"], soil["SAT"] + 1e-7
            )

        for summary in self.summaries:
            self.assertLessEqual(
                abs(summary["annual_residual_mm"]), 1e-6
            )

    def test_event_changes_unretained_proxy(self):
        for soil in SOILS:
            event = [
                r for r in self.rows
                if r["soil"] == soil
                and r["date"] == "2023-10-20"
            ]
            base = next(
                r for r in event
                if r["scenario"] == "Baseline"
            )
            storm = next(
                r for r in event
                if r["scenario"] == "S2_synthetic_storm"
            )
            self.assertGreater(
                storm["unretained_water_mm"],
                base["unretained_water_mm"]
            )

    def test_zero_added_rain_is_identical(self):
        rows, _ = run_s2(added_rain_mm=0)
        for soil in SOILS:
            base = [
                r for r in rows
                if r["soil"] == soil
                and r["scenario"] == "Baseline"
            ]
            storm = [
                r for r in rows
                if r["soil"] == soil
                and r["scenario"] == "S2_synthetic_storm"
            ]
            for a, b in zip(base, storm):
                for key in (
                    "P_total_mm", "S_end_mm",
                    "drainage_proxy_mm",
                    "unretained_water_mm"
                ):
                    self.assertAlmostEqual(
                        a[key], b[key], places=9
                    )

    def test_invalid_inputs_rejected(self):
        cases = [
            ("2024-10-20", 120),
            ("2023-02-30", 120),
            ("2023-10-20", -1),
            ("2023-10-20", nan),
            ("2023-10-20", inf),
            ("2023-10-20", True),
            ("2023-10-20", 501),
        ]
        for day, amount in cases:
            with self.assertRaises(ValueError):
                run_s2(day, amount)

    def test_same_forcing_for_two_soils(self):
        for scenario in (
            "Baseline", "S2_synthetic_storm"
        ):
            a = [
                r for r in self.rows
                if r["soil"] == "Soil_A"
                and r["scenario"] == scenario
            ]
            b = [
                r for r in self.rows
                if r["soil"] == "Soil_B"
                and r["scenario"] == scenario
            ]
            for x, y in zip(a, b):
                self.assertEqual(
                    (
                        x["date"], x["P_total_mm"],
                        x["ET0_A10_mm"]
                    ),
                    (
                        y["date"], y["P_total_mm"],
                        y["ET0_A10_mm"]
                    )
                )


if __name__ == "__main__":
    unittest.main()
