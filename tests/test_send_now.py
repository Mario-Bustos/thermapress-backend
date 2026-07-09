import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

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
    @patch("send_now.fetch_articles", return_value=[{"title": "Story", "summary": "Summary", "link": "https://example.com", "source": "BBC"}])
    def test_process_user_does_not_persist_or_update_when_email_fails(self, _fetch_articles):
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
            send_email_fn=lambda email, articles, subject: False,
            force_send=True,
        )

        self.assertFalse(result["sent"])
        self.assertEqual(result["reason"], "email_failed")
        self.assertNotIn("newsletters", supabase.tables)
        self.assertNotIn("user_profiles", supabase.tables)

    @patch("send_now.fetch_articles", return_value=[{"title": "Story", "summary": "Summary", "link": "https://example.com", "source": "BBC"}])
    def test_process_user_persists_newsletter_and_updates_last_sent_when_email_succeeds(self, _fetch_articles):
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
            send_email_fn=lambda email, articles, subject: True,
            force_send=True,
        )

        self.assertTrue(result["sent"])
        self.assertEqual(result["reason"], "sent")
        self.assertEqual(len(supabase.tables["newsletters"].inserted_payloads), 1)
        newsletter_payload = supabase.tables["newsletters"].inserted_payloads[0]
        self.assertEqual(newsletter_payload["user_id"], "user-1")
        self.assertEqual(newsletter_payload["subject"], "Your ThermaPress Newsletter - July 7.")
        self.assertEqual(newsletter_payload["articles"], [{"title": "Story", "summary": "Summary", "link": "https://example.com", "source": "BBC"}])
        self.assertEqual(newsletter_payload["sent_at"], "2026-07-07T12:00:00+00:00")

        self.assertIn("user_profiles", supabase.tables)
        self.assertEqual(supabase.tables["user_profiles"].updated_payloads, [{"last_sent": "2026-07-07"}])
        self.assertEqual(supabase.tables["user_profiles"].eq_filter, ("id", "user-1"))

    @patch("send_now.fetch_articles", return_value=[])
    def test_process_user_uses_newsletter_timezone_date_for_subject_and_last_sent(self, _fetch_articles):
        supabase = FakeSupabase()
        user = {
            "id": "user-1",
            "email": "user@example.com",
            "sources": ["bbc"],
            "categories": ["world"],
        }

        result = process_user(
            user,
            datetime.fromisoformat("2026-07-08T23:30:00-05:00"),
            supabase,
            send_email_fn=lambda email, articles, subject: True,
            force_send=True,
        )

        self.assertTrue(result["sent"])
        newsletter_payload = supabase.tables["newsletters"].inserted_payloads[0]
        self.assertEqual(newsletter_payload["subject"], "Your ThermaPress Newsletter - July 8.")
        self.assertEqual(newsletter_payload["sent_at"], "2026-07-08T23:30:00-05:00")
        self.assertEqual(supabase.tables["user_profiles"].updated_payloads, [{"last_sent": "2026-07-08"}])


if __name__ == "__main__":
    unittest.main()