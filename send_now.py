import os
from datetime import datetime, timezone
from supabase import create_client
from scraper import fetch_articles
from mailer import send_newsletter
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def main():
    now = datetime.now(timezone.utc)
    current_time = now.strftime('%H:%M')
    current_hour = now.strftime('%H')
    current_minute = now.strftime('%M')

    print(f'[send_now] Running at {current_time} UTC')

    response = supabase.table('user_profiles').select(
        'id, email, sources, categories, newsletter_time'
    ).execute()

    users = response.data or []
    sent = 0

    for user in users:
        email           = user.get('email')
        sources         = user.get('sources') or []
        categories      = user.get('categories') or []
        newsletter_time = user.get('newsletter_time') or '06:00'

        if not email or not sources or not categories:
            continue

        # Only send if current time matches user's newsletter_time
        if newsletter_time != current_time:
            continue

        print(f'[send_now] Sending to {email}')
        articles = fetch_articles(sources, categories)
        send_newsletter(email, articles)
        sent += 1

    print(f'[send_now] Done. Sent {sent} newsletter(s).')

if __name__ == '__main__':
    main()