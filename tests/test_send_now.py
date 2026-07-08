import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from send_now import process_user


class FakeResponse:
    def __init__(self, data=None, status_code=200):
        self.data = data
        self.status_code = status_code


class FakeTable:
    def __init__(self):
        self.inserted_payloads = []
        self.updated_payloads = []
        self.eq_filter = None

    def insert(self, payload):
        self.inserted_payloads.append(payload)
        return self

    def update(self, payload):
        self.updated_payloads.append(payload)
        return self

    def eq(self, column, value):
        self.eq_filter = (column, value)
        return self

    def execute(self):
        return FakeResponse(data={"ok": True})


class FakeSupabase:
    def __init__(self):
        self.tables = {}

    def table(self, name):
        if name not in self.tables:
            self.tables[name] = FakeTable()
        return self.tables[name]


class ProcessUserTests(unittest.TestCase):
    def test_process_user_persists_newsletter_record_when_email_fails(self):
        supabase = FakeSupabase()
        user = {
            "id": "user-1",
            "email": "user@example.com",
            "sources": ["bbc"],
            "categories": ["world"],
        }

        result = process_user(
            user,
            datetime(2026, 7, 7, 12, 0, tzinfo=timezone.utc),
            supabase,
            send_email_fn=lambda email, articles: False,
            force_send=True,
        )

        self.assertFalse(result["sent"])
        self.assertEqual(result["reason"], "email_failed")
        self.assertEqual(len(supabase.tables["newsletters"].inserted_payloads), 1)
        newsletter_payload = supabase.tables["newsletters"].inserted_payloads[0]
        self.assertEqual(newsletter_payload["delivery_status"], "failed")
        self.assertEqual(newsletter_payload["user_id"], "user-1")


if __name__ == "__main__":
    unittest.main()
