import unittest
import pandas as pd

from rotation_water_exposure import (
    calculate_sowing_window_exposure,
)


from rotation_water_exposure import compare_s3_sowing_window_exposure


class TestRotationExposure(unittest.TestCase):

    def setUp(self):
        days = pd.date_range("2023-01-01", "2023-12-31")

        self.df = pd.DataFrame([
            {
                "soil": soil,
                "scenario": "Baseline",
                "date": day.strftime("%Y-%m-%d"),
                "Ks_proxy": (
                    0.5 if day.month == 10 and day.day <= n
                    else 1.0
                ),
            }
            for soil, n in [("Soil_A", 4), ("Soil_B", 2)]
            for day in days
        ])

    def test_planning_years_preserved(self):
        result = calculate_sowing_window_exposure(
            self.df, "R1", 2027, "Soil_A"
        )
        self.assertFalse(result.empty)
        self.assertTrue(
            result["Reference month"].str.startswith("2023-").all()
        )

    def test_soils_differ(self):
        for soil, expected in [("Soil_A", 4), ("Soil_B", 2)]:
            result = calculate_sowing_window_exposure(
                self.df, "R1", 2027, soil
            )
            october = result[
                result["Reference month"] == "2023-10"
            ]
            self.assertFalse(october.empty)
            self.assertTrue(
                (
                    october["2023 model low-Ks proxy days"]
                    == expected
                ).all()
            )

    def test_missing_days_rejected(self):
        with self.assertRaises(ValueError):
            calculate_sowing_window_exposure(
                self.df.head(3), "R1", 2027, "Soil_A"
            )

    def test_invalid_ks_rejected(self):
        bad = self.df.copy()
        bad.loc[0, "Ks_proxy"] = -0.1
        with self.assertRaises(ValueError):
            calculate_sowing_window_exposure(
                bad, "R1", 2027, "Soil_A"
            )

    def test_duplicate_dates_rejected(self):
        bad = self.df.copy()
        bad.loc[0, "date"] = bad.loc[1, "date"]
        with self.assertRaises(ValueError):
            calculate_sowing_window_exposure(
                bad, "R1", 2027, "Soil_A"
            )

    def test_missing_scenario_rejected(self):
        with self.assertRaises(ValueError):
            calculate_sowing_window_exposure(
                self.df, "R1", 2027,
                "Soil_A", "S3_drought"
            )



    def test_s3_minus_baseline_comparison(self):
        s3 = self.df.copy()
        s3["scenario"] = "S3_drought"

        dates = pd.to_datetime(s3["date"])

        mask = (
            s3["soil"].eq("Soil_A")
            & dates.dt.month.eq(10)
            & dates.dt.day.le(6)
        )

        s3.loc[mask, "Ks_proxy"] = 0.5

        combined = pd.concat(
            [self.df, s3], ignore_index=True
        )

        result = compare_s3_sowing_window_exposure(
            combined, "R1", 2027, "Soil_A"
        )

        october = result.loc[
            result["Reference month"].eq("2023-10")
        ]

        self.assertFalse(october.empty)
        self.assertTrue(
            (
                october["S3 minus Baseline low-Ks days"]
                == 2
            ).all()
        )

if __name__ == "__main__":
    unittest.main()
