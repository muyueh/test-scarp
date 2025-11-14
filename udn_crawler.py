"""Utilities for crawling UDN breaking news."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urljoin

import requests

BASE_URL = "https://udn.com/api/more"
DEFAULT_PARAMS = {
    "id": "1",
    "channelId": "1",
    "cate_id": "0",
    "type": "breaknews",
}


class CrawlerError(RuntimeError):
    """Raised when the crawler encounters an unrecoverable error."""


def fetch_page(
    session: requests.Session,
    *,
    page: int,
    base_url: str = BASE_URL,
    params: Optional[dict] = None,
    timeout: float = 10.0,
) -> dict:
    """Fetch a single page of UDN breaking news.

    Args:
        session: A shared :class:`requests.Session` instance.
        page: The one-based page index to request.
        base_url: The endpoint to query.
        params: Additional query parameters to merge with defaults.
        timeout: Network timeout in seconds.

    Returns:
        The parsed JSON payload.
    """

    if page < 1:
        raise ValueError("page must be a positive integer")

    merged_params = {**DEFAULT_PARAMS, **(params or {}), "page": str(page)}
    response = session.get(base_url, params=merged_params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("state", False):
        raise CrawlerError("UDN API returned an unsuccessful state")
    return payload


def _normalise_item(item: dict) -> dict:
    """Convert a UDN API entry into a simplified structure."""

    link = item.get("titleLink") or ""
    absolute_link = urljoin("https://udn.com", link)
    return {
        "title": item.get("title"),
        "summary": item.get("paragraph"),
        "link": absolute_link,
        "image": item.get("url"),
        "published_at": item.get("time", {}).get("date"),
    }


def crawl_breaking_news(
    *,
    pages: int,
    delay: float = 0.0,
    session: Optional[requests.Session] = None,
) -> List[dict]:
    """Fetch multiple pages of UDN breaking news."""

    if pages < 1:
        raise ValueError("pages must be at least 1")

    owns_session = session is None
    session = session or requests.Session()
    collected: List[dict] = []
    try:
        for index in range(pages):
            page_number = index + 1
            payload = fetch_page(session, page=page_number)
            collected.extend(_normalise_item(item) for item in payload.get("lists", []))
            if delay > 0 and page_number < pages:
                time.sleep(delay)
    finally:
        if owns_session:
            session.close()
    return collected


def _parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to fetch (default: 1)")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay between requests in seconds")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional file path to write JSON results",
    )
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation level (default: 2)")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = _parse_args(argv)
    articles = crawl_breaking_news(pages=args.pages, delay=args.delay)
    serialised = json.dumps(articles, ensure_ascii=False, indent=args.indent)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialised, encoding="utf-8")
    else:
        print(serialised)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
