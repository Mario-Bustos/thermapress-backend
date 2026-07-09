import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mailer import _resend_response_id


class ResendResponseTests(unittest.TestCase):
    def test_resend_response_id_reads_top_level_dict_id(self):
        self.assertEqual(_resend_response_id({"id": "email-123"}), "email-123")

    def test_resend_response_id_reads_nested_data_dict_id(self):
        self.assertEqual(_resend_response_id({"data": {"id": "email-456"}}), "email-456")

    def test_resend_response_id_returns_none_without_id(self):
        self.assertIsNone(_resend_response_id({"data": {}}))


if __name__ == "__main__":
    unittest.main()
