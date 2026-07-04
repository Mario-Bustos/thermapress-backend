import feedparser
import trafilatura
import httpx
from sources import RSS_FEEDS, CATEGORY_KEYWORDS


def fetch_articles(sources: list[str], categories: list[str], max_per_source: int = 10) -> list[dict]:
    all_articles = []

    for source in sources:
        url = RSS_FEEDS.get(source)
        if not url:
            continue

        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_source]:
                title   = entry.get('title', '')
                summary = entry.get('summary', entry.get('description', ''))
                link    = entry.get('link', '')

                if not title or not link:
                    continue

                if _matches_categories(title + ' ' + summary, categories):
                    all_articles.append({
                        'title':   title,
                        'summary': _clean_summary(summary),
                        'link':    link,
                        'source':  source.upper(),
                    })
        except Exception as e:
            print(f'[scraper] Error fetching {source}: {e}')

    return all_articles[:20]  # cap at 20 articles per newsletter


def _matches_categories(text: str, categories: list[str]) -> bool:
    text_lower = text.lower()
    for category in categories:
        keywords = CATEGORY_KEYWORDS.get(category, [])
        if any(kw in text_lower for kw in keywords):
            return True
    return False


def _clean_summary(text: str) -> str:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(text, 'lxml')
    clean = soup.get_text(separator=' ').strip()
    return clean[:300] + '...' if len(clean) > 300 else clean