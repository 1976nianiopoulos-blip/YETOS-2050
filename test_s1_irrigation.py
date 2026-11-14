"""Independent S1 regression against SHA-verified 1460-row archive."""
import csv
import math
import unittest
from collections import defaultdict

from s1_irrigation import (
    ARCHIVE, SOILS, SCENARIOS, load_verified_weather,
    run_s1, simulate_step,
)


class TestS1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.weather = load_verified_weather()

    def test_01_regression_all_1460_published_rows(self):
        with ARCHIVE.open(encoding="utf-8-sig", newline="") as handle:
            published = list(csv.DictReader(handle))
        self.assertEqual(len(published), 1460)
        expected = {(r["soil"], r["scenario"], r["date"]): r
                    for r in published}
        self.assertEqual(len(expected), 1460)
        checked = 0
        fields = ("P_mm", "ET0_A10_mm", "Ks_proxy",
                  "ET_ref_stressed_mm", "drainage_proxy_mm",
                  "unretained_water_mm", "S_start_mm", "S_end_mm")
        for soil_id, soil in SOILS.items():
            for scenario in ("Baseline", "S3_drought"):
                storage = soil["FC"]
                for day, baseline_rain, et0 in self.weather:
                    rain = (0. if scenario == "S3_drought" and
                            int(day[5:7]) in (7, 8) else baseline_rain)
                    before = storage
                    v = simulate_step(soil, before, rain, 0., et0)
                    storage = v["S_end"]
                    actual = {"P_mm": rain, "ET0_A10_mm": et0,
                              "Ks_proxy": v["Ks_proxy"],
                              "ET_ref_stressed_mm": v["ET_ref_stressed"],
                              "drainage_proxy_mm": v["drainage_proxy"],
                              "unretained_water_mm": v["unretained_water"],
                              "S_start_mm": before, "S_end_mm": storage}
                    original = expected[(soil_id, scenario, day)]
                    for field in fields:
                        self.assertAlmostEqual(actual[field], float(original[field]),
                                               delta=2e-5, msg=f"{soil_id} {scenario} {day} {field}")
                    checked += 1
        self.assertEqual(checked, 1460)

    def test_02_s1_rows_and_schedule(self):
        rows, summaries = run_s1()
        self.assertEqual(len(rows), 2190)
        self.assertEqual(len(summaries), 6)
        by_key = {(r["soil"], r["scenario"], r["date"]): r for r in rows}
        self.assertEqual(len(by_key), 2190)
        for soil in SOILS:
            for day, rain, et0 in self.weather:
                for scenario in SCENARIOS:
                    row = by_key[(soil, scenario, day)]
                    self.assertEqual(row["P_mm"], rain)
                    self.assertEqual(row["ET0_A10_mm"], et0)
                    expected_i = 4. if int(day[5:7]) in (6, 7, 8) else 0.
                    if scenario == "No_irrigation" or (scenario == "S1_interruption" and
                                                          "2023-07-01" <= day <= "2023-07-31"):
                        expected_i = 0.
                    self.assertEqual(row["I_mm"], expected_i)
            for summary in summaries:
                if summary["soil"] == soil:
                    expected_total = {"No_irrigation": 0.,
                                      "Hypothetical_supply": 368.,
                                      "S1_interruption": 244.}[summary["scenario"]]
                    self.assertAlmostEqual(summary["I_mm"], expected_total)

    def test_03_daily_annual_a08(self):
        rows, summaries = run_s1()
        groups = defaultdict(list)
        for r in rows:
            residual = (r["S_start_mm"] + r["P_mm"] + r["I_mm"]
                        - r["S_end_mm"] - r["ET_ref_stressed_mm"]
                        - r["drainage_proxy_mm"] - r["unretained_water_mm"])
            self.assertLessEqual(abs(residual), 1e-8)
            self.assertTrue(SOILS[r["soil"]]["WP"] - 1e-8 <= r["S_end_mm"]
                            <= SOILS[r["soil"]]["SAT"] + 1e-8)
            groups[(r["soil"], r["scenario"])].append(r)
        for s in summaries:
            g = groups[(s["soil"], s["scenario"])]
            self.assertEqual(len(g), 365)
            self.assertLessEqual(abs(s["annual_residual_mm"]), 1e-6)
            self.assertAlmostEqual(g[0]["S_start_mm"] + sum(x["P_mm"] + x["I_mm"] for x in g),
                                   g[-1]["S_end_mm"] + sum(x["ET_ref_stressed_mm"] +
                                   x["drainage_proxy_mm"] + x["unretained_water_mm"] for x in g),
                                   delta=1e-6)

    def test_04_zero_rate_and_invalid_inputs(self):
        rows, _ = run_s1(rate_mm_day=0.)
        by_key = {(r["soil"], r["scenario"], r["date"]): r for r in rows}
        numeric = ("P_mm", "I_mm", "Ks_proxy", "ET_ref_stressed_mm",
                   "drainage_proxy_mm", "unretained_water_mm", "S_end_mm")
        for soil in SOILS:
            for day, _, _ in self.weather:
                reference = by_key[(soil, "No_irrigation", day)]
                for scenario in SCENARIOS[1:]:
                    candidate = by_key[(soil, scenario, day)]
                    for field in numeric:
                        self.assertAlmostEqual(reference[field], candidate[field], delta=1e-10)
        for bad in (-1., math.nan, math.inf):
            with self.assertRaises(ValueError):
                run_s1(rate_mm_day=bad)
            with self.assertRaises(ValueError):
                simulate_step(SOILS["Soil_A"], 120., 1., bad, 1.)
        with self.assertRaises(ValueError):
            run_s1(outage_start="2023-08-01", outage_end="2023-07-01")
        with self.assertRaises(ValueError):
            run_s1(outage_start="2024-01-01")


if __name__ == "__main__":
    unittest.main()
