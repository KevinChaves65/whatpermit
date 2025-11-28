import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from zoning_parser import (
    extract_zoning_rules,
    extract_zone_codes,
    detect_job_type,
    classify_permit_type,
    is_valid_permit_text,
    deep_scrape_zoning_pages
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

PERMIT_URL = "https://www.oakville.ca/home-environment/building-renovations/building-permits-inspections/"
ZONING_ENTRY_PAGES = [
    "https://www.oakville.ca/town-hall/by-laws-enforcement/zoning-by-laws/"
]

BASE_URL = "https://www.oakville.ca"


def find_project_subpages(soup):
    keywords = ["permit", "application", "inspection", "form", "project", "submit"]
    links = []

    for link in soup.find_all("a", href=True):
        text = link.get_text(strip=True).lower()
        if any(k in text for k in keywords):
            links.append({
                "title": link.get_text(strip=True),
                "url": urljoin(BASE_URL, link["href"])
            })

    return links


# ---------------- PERMIT SCRAPER ----------------

def scrape_oakville_permits():
    response = requests.get(PERMIT_URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    permits = []
    seen = set()
    blocks = soup.find_all(["p", "li", "div"])
    project_pages = find_project_subpages(soup)

    print(f"🔍 [Oakville] Found {len(blocks)} content blocks")

    for i, block in enumerate(blocks):
        text = block.get_text(" ", strip=True)

        if not text or len(text) < 60:
            continue

        fingerprint = text[:150].lower()
        if fingerprint in seen:
            continue

        if not is_valid_permit_text(text):
            continue

        seen.add(fingerprint)
        print(f"✅ VALID OAKVILLE PERMIT [{i}]: {text[:120]}")

        permits.append({
            "city": "Oakville",
            "type": classify_permit_type(text),
            "jobType": detect_job_type(text),
            "permitName": "Oakville Permit",
            "permitRequired": True,
            "authority": "Town of Oakville",
            "authorityLevel": "Municipal",
            "section": text[:300],
            "zoneCodes": extract_zone_codes(text),
            "zoningRules": extract_zoning_rules(text),
            "projectPages": project_pages,
            "bylawLinks": ZONING_ENTRY_PAGES,
            "url": PERMIT_URL
        })

    print(f"📦 Total Oakville permit records extracted: {len(permits)}")
    return permits


# ---------------- ZONING SCRAPER ----------------

def scrape_oakville_zoning():
    print("🧠 Deep zoning crawl enabled for Oakville...")

    zoning_results = []
    collected_urls = set()

    for entry in ZONING_ENTRY_PAGES:
        print(f"📍 Starting zoning crawl at: {entry}")

        records = deep_scrape_zoning_pages(
            start_url=entry,
            city="Oakville",
            authority="Town of Oakville",
            authority_level="Municipal",
            max_depth=3,
            domain_filter="oakville.ca"
        )

        for record in records:
            if record["url"] not in collected_urls:
                zoning_results.append(record)
                collected_urls.add(record["url"])

    print(f"📦 Total Oakville zoning records extracted: {len(zoning_results)}")
    return zoning_results
