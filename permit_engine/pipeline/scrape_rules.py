"""
Scrapes the live Toronto "When do I need a building permit?" page and extracts
a normalized list of rule entries that can be diffed against toronto_permit_rules.json.

Source: https://www.toronto.ca/services-payments/building-construction/building-permit/
        before-you-apply-for-a-building-permit/when-do-i-need-a-building-permit/

The page organises rules into two accordion/list sections:
  - "A building permit IS required when you want to..."
  - "A building permit IS NOT required when you want to..."

We extract each bullet point as a { project_type, description, conditions, raw_text }
dict — enough to diff against the stored JSON without needing a full parse.
"""

import hashlib
import re
from datetime import date

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base import fetch_html

SOURCE_URL = (
    "https://www.toronto.ca/services-payments/building-construction/building-permit/"
    "before-you-apply-for-a-building-permit/when-do-i-need-a-building-permit/"
)

# Phrases that signal the start of the two sections in the page HTML
REQUIRED_SIGNALS = [
    "permit is required",
    "a building permit is required",
    "when you need a building permit",
    "do need a permit",
]

NOT_REQUIRED_SIGNALS = [
    "permit is not required",
    "a building permit is not required",
    "do not need a permit",
    "when you don't need",
]


def _content_hash(text: str) -> str:
    """SHA-256 of the normalised page text — used to detect any change at all."""
    normalised = re.sub(r"\s+", " ", text).strip().lower()
    return hashlib.sha256(normalised.encode()).hexdigest()


def _extract_list_items(soup, section_signals: list[str]) -> list[str]:
    """
    Find the heading/paragraph that contains one of the section_signals,
    then collect all <li> text items that follow it until the next major heading.
    Returns a list of raw text strings.
    """
    from bs4 import NavigableString, Tag

    # Find the section anchor — look for any element whose text contains a signal
    anchor = None
    for tag in soup.find_all(["h2", "h3", "h4", "p", "strong", "b"]):
        text = tag.get_text(" ", strip=True).lower()
        if any(signal in text for signal in section_signals):
            anchor = tag
            break

    if anchor is None:
        return []

    items = []
    # Walk siblings forward until we hit another heading of equal/higher level
    for sibling in anchor.find_all_next():
        if sibling.name in ("h2", "h3", "h4") and sibling != anchor:
            break
        if sibling.name == "li":
            text = sibling.get_text(" ", strip=True)
            if text and len(text) > 10:
                items.append(text)

    return items


def _normalise_item(raw: str) -> dict:
    """
    Convert a raw list item string into a minimal structured dict.
    Splits off parenthetical conditions where possible.
    """
    # Try to split "Title – description" or "Title: description"
    title = raw
    description = ""

    for sep in (" – ", " - ", ": "):
        if sep in raw:
            parts = raw.split(sep, 1)
            title = parts[0].strip()
            description = parts[1].strip()
            break

    # Extract parenthetical conditions like (if X) or (when Y)
    conditions = re.findall(r"\(([^)]{10,})\)", raw)

    return {
        "project_type": title,
        "description": description or raw,
        "conditions": conditions,
        "raw_text": raw,
    }


def scrape() -> dict:
    """
    Fetch the live Toronto permit page and return a structured dict:
    {
        "source_url": ...,
        "scraped_at": "YYYY-MM-DD",
        "page_hash": "sha256...",
        "permit_required": [ { project_type, description, conditions, raw_text }, ... ],
        "permit_not_required": [ ... ],
        "raw_text_preview": "first 500 chars of page text",
        "ok": True/False,
        "error": None or error string
    }
    """
    soup = fetch_html(SOURCE_URL)

    if soup is None:
        return {
            "source_url": SOURCE_URL,
            "scraped_at": str(date.today()),
            "page_hash": None,
            "permit_required": [],
            "permit_not_required": [],
            "raw_text_preview": "",
            "ok": False,
            "error": "Failed to fetch page",
        }

    full_text = soup.get_text(" ", strip=True)

    required_items = _extract_list_items(soup, REQUIRED_SIGNALS)
    not_required_items = _extract_list_items(soup, NOT_REQUIRED_SIGNALS)

    print(f"🌐 [Scraper] Fetched {SOURCE_URL}")
    print(f"   permit_required items found:     {len(required_items)}")
    print(f"   permit_not_required items found: {len(not_required_items)}")

    return {
        "source_url": SOURCE_URL,
        "scraped_at": str(date.today()),
        "page_hash": _content_hash(full_text),
        "permit_required": [_normalise_item(r) for r in required_items],
        "permit_not_required": [_normalise_item(r) for r in not_required_items],
        "raw_text_preview": full_text[:500],
        "ok": True,
        "error": None,
    }


if __name__ == "__main__":
    import json
    result = scrape()
    print(json.dumps(result, indent=2))
