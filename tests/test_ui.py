from html.parser import HTMLParser
from pathlib import Path
import unittest


class IdCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.add(values["id"])


class DemoUiTest(unittest.TestCase):
    def test_demo_has_customer_intake_and_owner_queue_controls(self):
        html_path = Path(__file__).parents[1] / "web" / "index.html"
        parser = IdCollector()
        parser.feed(html_path.read_text(encoding="utf-8"))
        expected = {"intake-form", "lead-queue", "customer-reply", "metric-total", "metric-urgent"}
        self.assertTrue(expected.issubset(parser.ids))

    def test_demo_calls_real_local_api(self):
        html = (Path(__file__).parents[1] / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("/api/intake", html)
        self.assertIn("/api/state", html)


if __name__ == "__main__":
    unittest.main()
