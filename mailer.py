import resend
import os
from email_builder import build_email


def send_newsletter(user_email: str, articles: list[dict], subject: str) -> bool:
    resend.api_key = os.getenv('RESEND_API_KEY')

    html = build_email(user_email, articles)

    try:
        resend.Emails.send({
            'from':    os.getenv('FROM_EMAIL', 'newsletter@yourdomain.com'),
            'to':      user_email,
            'subject': subject,
            'html':    html,
        })
        print(f'[mailer] Sent to {user_email} with subject "{subject}"')
        return True
    except Exception as e:
        print(f'[mailer] Failed to send to {user_email}: {e}')
        return False