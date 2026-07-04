import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client

from scraper import fetch_articles
from mailer import send_newsletter

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"]
)

CHECK_WINDOW_MINUTES = 5


def within_send_window(now: datetime, newsletter_time: str) -> bool:
    """Returns True if now is within the configured window of newsletter_time."""
    try:
        hour, minute = map(int, newsletter_time.split(":"))
    except ValueError:
        return False

    scheduled = now.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    diff = abs((now - scheduled).total_seconds())

    return diff <= CHECK_WINDOW_MINUTES * 60


def main():
    now = datetime.now(timezone.utc)
    today = now.date()

    print(f"[send_now] Started at {now.isoformat()}")

    response = (
        supabase
        .table("user_profiles")
        .select(
            "id, email, sources, categories, newsletter_time, last_sent"
        )
        .execute()
    )

    users = response.data or []

    sent = 0

    for user in users:
        user_id = user["id"]
        email = user.get("email")
        sources = user.get("sources") or []
        categories = user.get("categories") or []
        newsletter_time = user.get("newsletter_time") or "06:00"
        last_sent = user.get("last_sent")

        if not email:
            print(f"Skipping {user_id}: no email")
            continue

        if not sources:
            print(f"Skipping {email}: no sources")
            continue

        if not categories:
            print(f"Skipping {email}: no categories")
            continue

        if last_sent == str(today):
            print(f"Skipping {email}: already sent today")
            continue

        if not within_send_window(now, newsletter_time):
            continue

        try:
            print(f"Sending newsletter to {email}")

            articles = fetch_articles(sources, categories)
            send_newsletter(email, articles)

            supabase.table("newsletters").insert({
                "user_id": user_id,
                "subject": "Your Daily ThermaPress Newsletter",
                "articles": articles
            }).execute()

            (
                supabase
                .table("user_profiles")
                .update({"last_sent": str(today)})
                .eq("id", user_id)
                .execute()
            )

            sent += 1

        except Exception as e:
            print(f"Failed sending to {email}: {e}")

    print(f"[send_now] Finished. Sent {sent} newsletter(s).")


if __name__ == "__main__":
    main()