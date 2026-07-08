import os
from datetime import datetime, timezone
from typing import Any, Callable

from dotenv import load_dotenv
from supabase import create_client

from scraper import fetch_articles
from mailer import send_newsletter

load_dotenv()

CHECK_WINDOW_MINUTES = 5
DEFAULT_NEWSLETTER_TIME = "06:00"
DEFAULT_SUBJECT = "Your Daily ThermaPress Newsletter"

supabase_client: Any | None = None


def create_supabase_client() -> Any:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

    return create_client(url, key)


def get_supabase_client() -> Any:
    global supabase_client
    if supabase_client is None:
        supabase_client = create_supabase_client()
    return supabase_client


def within_send_window(now: datetime, newsletter_time: str) -> bool:
    """Returns True if now is within the configured window of newsletter_time."""
    try:
        hour, minute = map(int, newsletter_time.split(":"))
    except ValueError:
        return False

    scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    diff = abs((now - scheduled).total_seconds())

    return diff <= CHECK_WINDOW_MINUTES * 60


def should_send_newsletter(
    now: datetime,
    newsletter_time: str | None,
    last_sent: str | None,
    today: Any,
    force_send: bool = False,
) -> bool:
    if last_sent == str(today):
        return False

    if force_send:
        return True

    return within_send_window(now, newsletter_time or DEFAULT_NEWSLETTER_TIME)


def persist_newsletter_record(
    supabase: Any,
    user_id: Any,
    recipient_email: str,
    subject: str,
    articles: list[dict],
    delivery_status: str,
) -> None:
    payloads = [
        {
            "user_id": user_id,
            "recipient_email": recipient_email,
            "subject": subject,
            "articles": articles,
            "delivery_status": delivery_status,
        },
        {
            "user_id": user_id,
            "email": recipient_email,
            "subject": subject,
            "content": articles,
            "status": delivery_status,
        },
    ]

    last_error: Exception | None = None
    for payload in payloads:
        try:
            response = supabase.table("newsletters").insert(payload).execute()
            if getattr(response, "data", None) is not None or getattr(response, "status_code", None) in {200, 201, 204}:
                return
        except Exception as exc:  # pragma: no cover - exercised in runtime
            last_error = exc

    if last_error is not None:
        raise RuntimeError(f"Unable to persist newsletter for {user_id}: {last_error}") from last_error

    raise RuntimeError(f"Unable to persist newsletter for {user_id}")


def process_user(
    user: dict[str, Any],
    now: datetime,
    supabase: Any,
    send_email_fn: Callable[[str, list[dict]], bool] = send_newsletter,
    force_send: bool = False,
) -> dict[str, Any]:
    user_id = user["id"]
    email = user.get("email")
    sources = user.get("sources") or []
    categories = user.get("categories") or []
    newsletter_time = user.get("newsletter_time")
    last_sent = user.get("last_sent")
    today = now.date()

    if not email:
        return {"sent": False, "reason": "no_email"}

    if not sources:
        return {"sent": False, "reason": "no_sources"}

    if not categories:
        return {"sent": False, "reason": "no_categories"}

    if not should_send_newsletter(now, newsletter_time, last_sent, today, force_send=force_send):
        return {"sent": False, "reason": "not_due"}

    print(f"Sending newsletter to {email}")
    articles = fetch_articles(sources, categories)

    try:
        email_sent = bool(send_email_fn(email, articles))
    except Exception as exc:
        print(f"Email delivery failed for {email}: {exc}")
        email_sent = False

    try:
        persist_newsletter_record(
            supabase,
            user_id,
            email,
            DEFAULT_SUBJECT,
            articles,
            "sent" if email_sent else "failed",
        )
    except Exception as exc:
        print(f"Newsletter persistence failed for {email}: {exc}")

    if email_sent:
        supabase.table("user_profiles").update({"last_sent": str(today)}).eq("id", user_id).execute()
        return {"sent": True, "reason": "sent", "articles": articles}

    return {"sent": False, "reason": "email_failed", "articles": articles}


def main() -> int:
    now = datetime.now(timezone.utc)
    today = now.date()
    force_send = os.getenv("FORCE_SEND", "").strip().lower() in {"1", "true", "yes", "on"}

    print(f"[send_now] Started at {now.isoformat()} (force_send={force_send})")

    try:
        supabase = get_supabase_client()
    except Exception as exc:
        print(f"[send_now] Failed to initialize Supabase client: {exc}")
        return 1

    response = (
        supabase.table("user_profiles")
        .select("id, email, sources, categories, newsletter_time, last_sent")
        .execute()
    )

    users = response.data or []

    sent = 0
    for user in users:
        result = process_user(user, now, supabase, force_send=force_send)
        if result.get("sent"):
            sent += 1

    print(f"[send_now] Finished. Sent {sent} newsletter(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())