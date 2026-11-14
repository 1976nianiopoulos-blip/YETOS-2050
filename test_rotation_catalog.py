import unittest
from rotation_catalog import (
    CROPS, ROTATIONS, HISTORY_CHOICES,
    timeline, crop_history_gate,
)


class RotationTests(unittest.TestCase):
    def test_frozen_rotations(self):
        self.assertEqual(
            ROTATIONS["R1"],
            ("BARLEY_W", "OSR_W", "WHEAT_W"),
        )
        self.assertEqual(
            ROTATIONS["R2"],
            ("FABA_S", "WHEAT_W", "BARLEY_S"),
        )
        self.assertEqual(
            ROTATIONS["R3"],
            ("BARLEY_S", "OATS_W", "FABA_S"),
        )

    def test_36_months(self):
        for code in ROTATIONS:
            rows = timeline(code)
            self.assertEqual(len(rows), 36)
            self.assertEqual(rows[0]["Planning month"], "2027-01")
            self.assertEqual(rows[-1]["Planning month"], "2029-12")
            self.assertEqual(
                len({r["Planning month"] for r in rows}), 36
            )

    def test_winter_sowing_precedes_harvest_year(self):
        rows = {
            r["Planning month"]: r
            for r in timeline("R1")
        }
        self.assertIn(
            "Winter oilseed rape",
            rows["2027-08"]["Indicative sowing window (NOT scheduled)"],
        )
        self.assertIn(
            "Winter wheat",
            rows["2028-10"]["Indicative sowing window (NOT scheduled)"],
        )

    def test_spring_sowing_same_year(self):
        rows = {
            r["Planning month"]: r
            for r in timeline("R2")
        }
        self.assertIn(
            "Spring faba beans",
            rows["2027-02"]["Indicative sowing window (NOT scheduled)"],
        )
        self.assertIn(
            "Spring barley",
            rows["2029-03"]["Indicative sowing window (NOT scheduled)"],
        )

    def test_no_fabricated_harvest(self):
        for code in ROTATIONS:
            for row in timeline(code):
                self.assertIn(
                    "Not established", row["Harvest date"]
                )

    def test_empty_sowing_window_label(self):
        rows = timeline("R1")
        self.assertEqual(
            rows[0]["Indicative sowing window (NOT scheduled)"],
            "No listed sowing window",
        )

    def test_history_prechecks(self):
        self.assertEqual(
            crop_history_gate(
                "R1", HISTORY_CHOICES[0], HISTORY_CHOICES[0]
            )[0],
            "EVIDENCE REQUIRED",
        )
        self.assertEqual(
            crop_history_gate(
                "R1", HISTORY_CHOICES[2], HISTORY_CHOICES[0]
            )[0],
            "PROJECT PRECONDITION NOT MET",
        )
        self.assertEqual(
            crop_history_gate(
                "R3", HISTORY_CHOICES[0], HISTORY_CHOICES[1]
            )[0],
            "HISTORY DECLARED ? NOT VERIFIED",
        )

    def test_teagasc_provenance(self):
        for crop in CROPS.values():
            self.assertTrue(
                crop["source"].startswith("https://teagasc.ie/")
            )
            self.assertTrue(crop["months"])


if __name__ == "__main__":
    unittest.main()
