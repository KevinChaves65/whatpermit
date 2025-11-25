import requests
from bs4 import BeautifulSoup
from zoning_parser import extract_zoning_rules, extract_zone_codes, detect_job_type

PERMIT_URL = "https://www.oakville.ca/home-environment/building-renovations/building-permits-inspections/building-permits/"
ZONING_URL = "https://www.oakville.ca/business-development/planning-services/zoning/"


def scrape_oakville_permits():
    response = requests.get(PERMIT_URL, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    permits = []
    blocks = soup.find_all(["p", "li", "div"])
    seen = set()

    print(f"🔍 [Oakville] Found {len(blocks)} content blocks")

    for i, block in enumerate(blocks):
        text = block.get_text(" ", strip=True).strip()
        lower = text.lower()

        if not text or text in seen:
            continue

        if (
            "permit" in lower
            and "share" not in lower
            and "facebook" not in lower
            and "linkedin" not in lower
            and "twitter" not in lower
            and "translate" not in lower
            and len(text) > 80
        ):
            seen.add(text)
            print(f"✅ VALID OAKVILLE PERMIT [{i}]: {text[:120]}")

            zoning_rules = extract_zoning_rules(text)
            zone_codes = extract_zone_codes(text)
            job_type = detect_job_type(text)

            permits.append({
                "city": "Oakville",
                "type": "permit-info",
                "jobType": job_type,
                "permitName": "Oakville Permit",
                "permitRequired": True,
                "authority": "Town of Oakville",
                "section": text[:300],
                "zoneCodes": zone_codes,
                "zoningRules": zoning_rules,
                "url": PERMIT_URL
            })

    print(f"📦 Total Oakville permits extracted: {len(permits)}")
    return permits


def scrape_oakville_zoning():
    response = requests.get(ZONING_URL, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    zoning_records = []
    blocks = soup.find_all(["p", "li", "div"])
    seen = set()

    for block in blocks:
        text = block.get_text(" ", strip=True).strip()

        if not text or text in seen:
            continue

        zone_codes = extract_zone_codes(text)
        zoning_rules = extract_zoning_rules(text)

        if zone_codes or zoning_rules:
            seen.add(text)

            zoning_records.append({
                "city": "Oakville",
                "type": "zoning-rule",
                "zoneCodes": zone_codes,
                "zoningRules": zoning_rules,
                "section": text[:300],
                "authority": "Town of Oakville",
                "url": ZONING_URL
            })

    print(f"📦 Total Oakville zoning records extracted: {len(zoning_records)}")
    return zoning_records
