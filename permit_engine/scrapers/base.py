"""
Shared HTTP and HTML utilities for all city scrapers.
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = 15


def fetch_html(url: str) -> BeautifulSoup | None:
    """GET a URL and return a BeautifulSoup object, or None on failure."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"⚠️  fetch_html failed [{url}]: {e}")
        return None


def fetch_text(url: str) -> str | None:
    """GET a URL and return the raw response text, or None on failure."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"⚠️  fetch_text failed [{url}]: {e}")
        return None


def fetch_bytes(url: str) -> bytes | None:
    """GET a URL and return raw bytes (for PDFs), or None on failure."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"⚠️  fetch_bytes failed [{url}]: {e}")
        return None


def extract_links(soup: BeautifulSoup, base_url: str, keywords: list[str]) -> list[dict]:
    """
    Find all <a> tags in soup whose href or link text contains any of the keywords.
    Returns a list of {"title": ..., "url": ...} dicts.
    """
    from urllib.parse import urljoin
    results = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        text = a.get_text(strip=True)
        combined = (href + " " + text).lower()

        if href in seen:
            continue

        if any(kw.lower() in combined for kw in keywords):
            seen.add(href)
            results.append({"title": text, "url": href})

    return results
