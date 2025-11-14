"""Simple crawler for United Daily News breaking news feed.

This script fetches the latest articles from United Daily News (聯合報)
using the public JSON endpoint that powers the "breaking news" section.
It collects the article title, link, summary, publish time, and associated
image for a configurable number of pages and outputs the result as JSON.

Example usage:
    python udn_crawler.py --pages 2 --output udn.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, Iterable, List
from urllib import error, parse, request

BASE_URL = "https://udn.com/api/more"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def build_request(
    *, page: int, category_id: int, channel_id: int, news_type: str
) -> request.Request:
    """Create a configured :class:`urllib.request.Request` for the API call."""
    params = {
        "page": str(page),
        "id": str(category_id),
        "channelId": str(channel_id),
        "type": news_type,
    }
    url = f"{BASE_URL}?{parse.urlencode(params)}"
    return request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})


def fetch_page(
    *, page: int, category_id: int, channel_id: int, news_type: str
) -> Dict:
    """Fetch a single page of articles from the United Daily News API."""
    req = build_request(
        page=page, category_id=category_id, channel_id=channel_id, news_type=news_type
    )
    try:
        with request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Unexpected status code: {resp.status}")
            return json.load(resp)
    except (error.HTTPError, error.URLError) as exc:
        raise RuntimeError(f"Failed to fetch page {page}: {exc}") from exc


def normalize_article(article: Dict) -> Dict:
    """Extract the fields we care about from an article payload."""
    link = article.get("titleLink") or ""
    time_field = article.get("time")
    if isinstance(time_field, dict):
        time_value = (
            time_field.get("date")
            or time_field.get("time")
            or time_field.get("datetime")
            or ""
        )
    else:
        time_value = time_field or ""

    normalized = {
        "title": (article.get("title") or "").strip(),
        "link": parse.urljoin("https://udn.com", link),
        "summary": (article.get("paragraph") or "").strip(),
        "time": time_value.strip() if isinstance(time_value, str) else time_value,
        "image": article.get("url") or None,
    }
    # Remove empty strings to keep the output tidy.
    return {key: value for key, value in normalized.items() if value}


def crawl_breaking_news(
    *,
    pages: int,
    delay: float,
    category_id: int,
    channel_id: int,
    news_type: str,
) -> List[Dict]:
    """Crawl the requested number of pages and return normalized articles."""
    articles: List[Dict] = []

    for page in range(pages):
        payload = fetch_page(
            page=page,
            category_id=category_id,
            channel_id=channel_id,
            news_type=news_type,
        )
        for item in payload.get("lists", []):
            articles.append(normalize_article(item))

        if payload.get("end"):
            break

        if delay > 0 and page < pages - 1:
            time.sleep(delay)

    return articles


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl United Daily News articles")
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to crawl (default: 1)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between page requests (default: 1.0)",
    )
    parser.add_argument(
        "--category-id",
        type=int,
        default=1,
        help="Category ID for the feed (default: 1 for breaking news)",
    )
    parser.add_argument(
        "--channel-id",
        type=int,
        default=1,
        help="Channel ID for the feed (default: 1 for breaking news)",
    )
    parser.add_argument(
        "--type",
        dest="news_type",
        default="breaknews",
        help="News type parameter (default: 'breaknews')",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to write the collected articles as JSON",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.pages < 1:
        print("--pages must be at least 1", file=sys.stderr)
        return 1

    try:
        articles = crawl_breaking_news(
            pages=args.pages,
            delay=args.delay,
            category_id=args.category_id,
            channel_id=args.channel_id,
            news_type=args.news_type,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    try:
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fh:
                json.dump(articles, fh, ensure_ascii=False, indent=2)
        else:
            json.dump(articles, sys.stdout, ensure_ascii=False, indent=2)
            print()
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
