import os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from supabase import create_client
from scraper import fetch_articles
from mailer import send_newsletter
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

scheduler = BlockingScheduler(timezone='UTC')


def load_and_schedule_users():
    print(f'[scheduler] Loading users at {datetime.utcnow()}')

    response = supabase.table('user_profiles').select(
        'id, email, sources, categories, newsletter_time'
    ).execute()

    users = response.data or []
    print(f'[scheduler] Found {len(users)} users')

    # Remove all existing user jobs before rescheduling
    for job in scheduler.get_jobs():
        if job.id.startswith('user_'):
            job.remove()

    for user in users:
        email           = user.get('email')
        sources         = user.get('sources') or []
        categories      = user.get('categories') or []
        newsletter_time = user.get('newsletter_time') or '06:00'

        if not email or not sources or not categories:
            continue

        try:
            hour, minute = newsletter_time.split(':')
        except ValueError:
            hour, minute = '6', '0'

        scheduler.add_job(
            send_to_user,
            trigger=CronTrigger(hour=int(hour), minute=int(minute), timezone='UTC'),
            args=[email, sources, categories],
            id=f'user_{user["id"]}',
            replace_existing=True
        )
        print(f'[scheduler] Scheduled {email} at {newsletter_time} UTC')


def send_to_user(email: str, sources: list, categories: list):
    print(f'[scheduler] Sending newsletter to {email}')
    articles = fetch_articles(sources, categories)
    send_newsletter(email, articles)


if __name__ == '__main__':
    # Initial load
    load_and_schedule_users()

    # Reload user schedules every hour to pick up changes
    scheduler.add_job(
        load_and_schedule_users,
        trigger=CronTrigger(minute=0),
        id='reload_users',
        replace_existing=True
    )

    print('[scheduler] Starting...')
    scheduler.start()