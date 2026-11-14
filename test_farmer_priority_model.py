import unittest

from farmer_priority_model import PRIORITIES, priority_fields


class FarmerPriorityTests(unittest.TestCase):

    def test_three_approved_priorities(self):
        self.assertEqual(PRIORITIES, (
            "Flood protection",
            "Drought resilience",
            "Water efficiency",
        ))

    def test_distinct_source_fields(self):
        selected = [priority_fields(p) for p in PRIORITIES]
        self.assertEqual(len(set(selected)), 3)
        self.assertEqual(
            selected[0][0], "unretained_water_mm"
        )
        self.assertEqual(
            selected[1][1], "n_ref_stress_days"
        )
        self.assertEqual(selected[2][0], "I_mm")

    def test_unknown_priority_rejected(self):
        with self.assertRaises(ValueError):
            priority_fields("best crop")

    def test_only_existing_field_names(self):
        for priority in PRIORITIES:
            fields = priority_fields(priority)
            self.assertEqual(len(fields), 3)
            self.assertTrue(all(
                isinstance(key, str) for key in fields
            ))
