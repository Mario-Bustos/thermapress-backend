import resend
import os
from typing import Any

from email_builder import build_email


def _resend_response_id(response: Any) -> str | None:
    if isinstance(response, dict):
        response_id = response.get("id")
        if response_id:
            return str(response_id)

        data = response.get("data")
        if isinstance(data, dict) and data.get("id"):
            return str(data["id"])

    response_id = getattr(response, "id", None)
    if response_id:
        return str(response_id)

    data = getattr(response, "data", None)
    if isinstance(data, dict) and data.get("id"):
        return str(data["id"])

    return None


def send_newsletter(user_email: str, articles: list[dict], subject: str) -> bool:
    resend.api_key = os.getenv('RESEND_API_KEY')
    from_email = os.getenv('FROM_EMAIL', 'newsletter@yourdomain.com')

    html = build_email(user_email, articles)

    try:
        response = resend.Emails.send({
            'from':    from_email,
            'to':      user_email,
            'subject': subject,
            'html':    html,
        })
        print(f'[mailer] Resend response for {user_email}: {response}')

        email_id = _resend_response_id(response)
        if not email_id:
            print(f'[mailer] Resend did not return an email id for {user_email}')
            return False

        print(f'[mailer] Sent to {user_email} from {from_email} with subject "{subject}" (id={email_id})')
        return True
    except Exception as e:
        print(f'[mailer] Failed to send to {user_email}: {e}')
        return False
