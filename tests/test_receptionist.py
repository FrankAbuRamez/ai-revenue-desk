import unittest

from revenue_desk import IntakeError, RevenueDesk


class RevenueDeskTest(unittest.TestCase):
    def setUp(self):
        self.desk = RevenueDesk(business_name="Northstar Home Services")

    def test_normal_request_is_qualified_for_booking(self):
        lead = self.desk.intake(
            {
                "name": "Jamie",
                "phone": "555-0102",
                "service": "HVAC",
                "problem": "The air conditioner is blowing warm air",
                "zip_code": "85001",
                "preferred_time": "Tomorrow morning",
            }
        )
        self.assertEqual(lead["status"], "ready_to_book")
        self.assertEqual(lead["priority"], "normal")
        self.assertFalse(lead["automation"]["binding_price_given"])

    def test_possible_emergency_is_escalated_not_diagnosed(self):
        lead = self.desk.intake(
            {
                "name": "Alex",
                "phone": "555-0188",
                "service": "Plumbing",
                "problem": "A pipe burst and water is flooding the basement",
                "zip_code": "85003",
                "preferred_time": "Now",
            }
        )
        self.assertEqual(lead["status"], "human_escalation")
        self.assertEqual(lead["priority"], "urgent")
        self.assertIn("immediate danger", lead["customer_message"].lower())
        self.assertFalse(lead["automation"]["diagnosis_given"])

    def test_missing_contact_details_are_rejected(self):
        with self.assertRaises(IntakeError):
            self.desk.intake(
                {
                    "name": "Taylor",
                    "phone": "",
                    "service": "Electrical",
                    "problem": "Outlet stopped working",
                    "zip_code": "85004",
                    "preferred_time": "Afternoon",
                }
            )

    def test_summary_counts_real_intake_state(self):
        self.desk.intake(
            {
                "name": "Jamie",
                "phone": "555-0102",
                "service": "HVAC",
                "problem": "AC is warm",
                "zip_code": "85001",
                "preferred_time": "Tomorrow",
            }
        )
        summary = self.desk.summary()
        self.assertEqual(summary["total_leads"], 1)
        self.assertEqual(summary["ready_to_book"], 1)
        self.assertEqual(summary["urgent"], 0)


if __name__ == "__main__":
    unittest.main()
