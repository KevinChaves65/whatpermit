import requests
from bs4 import BeautifulSoup
from zoning_parser import (
    extract_zoning_rules,
    extract_zone_codes,
    detect_job_type,
    find_project_subpages,
    is_valid_permit_text,
    classify_permit_type
)

PERMIT_URL = "https://www.toronto.ca/services-payments/building-construction/apply-for-a-building-permit/"
ZONING_URL = "https://www.toronto.ca/zoning/bylaw/"


def extract_links(soup):
    bylaw_links = []
    application_links = []

    for link in soup.find_all("a", href=True):
        url = link["href"].strip()
        text = link.get_text(strip=True).lower()

        if not url.startswith("http"):
            continue

        if "by-law" in text or "bylaw" in text or "regulation" in text:
            bylaw_links.append({
                "title": link.get_text(strip=True),
                "url": url
            })

        if "apply" in text or "application" in text or "permit form" in text:
            application_links.append({
                "title": link.get_text(strip=True),
                "url": url
            })

    return bylaw_links, application_links


def scrape_toronto_permits():
    response = requests.get(PERMIT_URL, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    permits = []
    blocks = soup.find_all(["p", "li", "div"])
    seen = set()

    bylaw_links, application_links = extract_links(soup)
    project_pages = find_project_subpages(soup)

    print(f"🔍 [Toronto] Found {len(blocks)} content blocks")

    for i, block in enumerate(blocks):
        text = block.get_text(" ", strip=True).strip()

        if not text:
            continue

        normalized = text[:150].lower()

        if normalized in seen:
            continue

        if not is_valid_permit_text(text):
            continue

        zoning_rules = extract_zoning_rules(text)
        zone_codes = extract_zone_codes(text)
        job_type = detect_job_type(text)
        permit_class = classify_permit_type(text)

        # 🚫 Skip informational junk completely
        if permit_class == "informational":
            continue

        seen.add(normalized)

        print(f"✅ VALID TORONTO PERMIT [{i}]: {text[:120]}")

        permits.append({
            "city": "Toronto",
            "type": permit_class,
            "jobType": job_type,
            "permitName": "Toronto Permit",
            "permitRequired": True,
            "authority": "City of Toronto",
            "authorityLevel": "Municipal",
            "section": text[:300],
            "zoneCodes": zone_codes,
            "zoningRules": zoning_rules,
            "bylawLinks": bylaw_links,
            "applicationLinks": application_links,
            "projectPages": project_pages,
            "url": PERMIT_URL
        })

    print(f"📦 Total Toronto permits extracted: {len(permits)}")
    return permits


def scrape_toronto_zoning():
    response = requests.get(ZONING_URL, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    zoning_records = []
    blocks = soup.find_all(["p", "li", "div"])
    seen = set()

    for block in blocks:
        text = block.get_text(" ", strip=True).strip()

        if not text:
            continue

        normalized = text[:150].lower()

        if normalized in seen:
            continue

        zone_codes = extract_zone_codes(text)
        zoning_rules = extract_zoning_rules(text)

        if zone_codes or zoning_rules:
            seen.add(normalized)

            zoning_records.append({
                "city": "Toronto",
                "type": "zoning-rule",
                "zoneCodes": zone_codes,
                "zoningRules": zoning_rules,
                "section": text[:300],
                "authority": "City of Toronto",
                "authorityLevel": "Municipal",
                "url": ZONING_URL
            })

    print(f"📦 Total Toronto zoning records extracted: {len(zoning_records)}")
    return zoning_records


if __name__ == "__main__":
    print("--- TORONTO PERMITS ---")
    scrape_toronto_permits()

    print("--- TORONTO ZONING ---")
    scrape_toronto_zoning()
