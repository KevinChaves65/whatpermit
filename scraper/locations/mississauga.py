import requests
from bs4 import BeautifulSoup
from zoning_parser import extract_zoning_rules, extract_zone_codes, detect_job_type

PERMIT_URL = "https://www.mississauga.ca/services-and-programs/building-and-renovating/building-permits/"
ZONING_URL = "https://www.mississauga.ca/services-and-programs/building-and-renovating/zoning/"


def scrape_mississauga_permits():
    response = requests.get(PERMIT_URL, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    permits = []
    blocks = soup.find_all(["p", "li", "div"])
    seen = set()

    print(f"🔍 [Mississauga] Found {len(blocks)} content blocks")

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
            print(f"✅ VALID MISSISSAUGA PERMIT [{i}]: {text[:120]}")

            zoning_rules = extract_zoning_rules(text)
            zone_codes = extract_zone_codes(text)
            job_type = detect_job_type(text)

            permits.append({
                "city": "Mississauga",
                "type": "permit-info",
                "jobType": job_type,
                "permitName": "Mississauga Permit",
                "permitRequired": True,
                "authority": "City of Mississauga",
                "section": text[:300],
                "zoneCodes": zone_codes,
                "zoningRules": zoning_rules,
                "url": PERMIT_URL
            })

    print(f"📦 Total Mississauga permits extracted: {len(permits)}")
    return permits


def scrape_mississauga_zoning():
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
                "city": "Mississauga",
                "type": "zoning-rule",
                "zoneCodes": zone_codes,
                "zoningRules": zoning_rules,
                "section": text[:300],
                "authority": "City of Mississauga",
                "url": ZONING_URL
            })

    print(f"📦 Total Mississauga zoning records extracted: {len(zoning_records)}")
    return zoning_records
