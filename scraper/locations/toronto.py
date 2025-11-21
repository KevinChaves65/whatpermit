import requests
from bs4 import BeautifulSoup
from zoning_parser import extract_zoning_rules, extract_zone_codes

PERMIT_URL = "https://www.toronto.ca/services-payments/building-construction/apply-for-a-building-permit/"
ZONING_URL = "https://www.toronto.ca/zoning/bylaw/"


def scrape_toronto_permits():
    response = requests.get(PERMIT_URL, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    permits = []
    blocks = soup.find_all(["p", "li", "div"])
    seen = set()

    print(f"🔍 Found {len(blocks)} content blocks")

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
            print(f"✅ VALID PERMIT [{i}]: {text[:120]}")

            zoning_rules = extract_zoning_rules(text)
            zone_codes = extract_zone_codes(text)

            permit = {
                "city": "Toronto",
                "type": "permit-info",
                "permitName": "Toronto Permit",
                "permitRequired": True,
                "authority": "City of Toronto",
                "section": text[:300],
                "zoneCodes": zone_codes,
                "zoningRules": zoning_rules,
                "url": PERMIT_URL
            }

            permits.append(permit)

    print(f"📦 Total clean permits extracted: {len(permits)}")
    return permits


def scrape_toronto_zoning():
    response = requests.get(ZONING_URL, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    zoning_records = []
    blocks = soup.find_all(["p", "li", "div"])
    seen = set()

    for block in blocks:
        text = block.get_text(" ", strip=True)

        if not text or text in seen:
            continue

        zone_codes = extract_zone_codes(text)
        zoning_rules = extract_zoning_rules(text)

        if zone_codes or zoning_rules:
            seen.add(text)

            zoning_records.append({
                "city": "Toronto",
                "type": "zoning-rule",
                "zoneCodes": zone_codes,
                "zoningRules": zoning_rules,
                "section": text[:300],
                "authority": "City of Toronto",
                "url": ZONING_URL
            })

    print(f"📦 Total zoning rules extracted: {len(zoning_records)}")
    return zoning_records


if __name__ == "__main__":
    print("--- TORONTO PERMITS ---")
    scrape_toronto_permits()
    print("--- TORONTO ZONING ---")
    scrape_toronto_zoning()
