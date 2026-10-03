import json
import unittest

from app import handle_api
from revenue_desk import RevenueDesk


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.desk = RevenueDesk("Northstar Home Services")

    def test_post_intake_returns_created_lead(self):
        body = json.dumps(
            {
                "name": "Morgan",
                "phone": "555-0120",
                "service": "HVAC",
                "problem": "AC is blowing warm air",
                "zip_code": "85001",
                "preferred_time": "Tomorrow morning",
            }
        ).encode()
        status, payload = handle_api("POST", "/api/intake", body, self.desk)
        self.assertEqual(status, 201)
        self.assertEqual(payload["lead"]["status"], "ready_to_book")
        self.assertEqual(payload["summary"]["total_leads"], 1)

    def test_state_endpoint_returns_real_lead_queue(self):
        self.desk.intake(
            {
                "name": "Morgan",
                "phone": "555-0120",
                "service": "HVAC",
                "problem": "AC is warm",
                "zip_code": "85001",
                "preferred_time": "Tomorrow",
            }
        )
        status, payload = handle_api("GET", "/api/state", b"", self.desk)
        self.assertEqual(status, 200)
        self.assertEqual(len(payload["leads"]), 1)

    def test_invalid_json_returns_400(self):
        status, payload = handle_api("POST", "/api/intake", b"not-json", self.desk)
        self.assertEqual(status, 400)
        self.assertIn("error", payload)


if __name__ == "__main__":
    unittest.main()
