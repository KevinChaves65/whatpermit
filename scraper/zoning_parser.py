# zoning_parser.py

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# ==================================================
# CONFIGURATION & CONSTANTS
# ==================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

DISALLOWED_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".pdf",
    ".doc", ".docx", ".xls", ".xlsx", ".zip",
    ".rar", ".7z", ".mp4", ".mp3", ".avi"
)

LEGAL_PATTERNS = [
    "shall", "must", "shall not", "is not permitted",
    "may not", "maximum", "minimum", "setback",
    "height", "density", "coverage", "variance required",
    "prohibited"
]

JUNK_TERMS = [
    "share", "navigation", "increase text", "decrease text",
    "contact us", "search", "click here", "menu",
    "facebook", "twitter", "linkedin"
]

ZONING_KEYWORDS = [
    "zoning", "bylaw", "by-law", "official plan",
    "development standards", "land use", "setback",
    "height", "density", "floor space", "fsi",
    "zone", "front yard", "rear yard", "lot width"
]

URL_ZONING_FILTER = [
    "zoning", "bylaw", "planning", "official-plan",
    "land-use", "development"
]

CONTENT_ZONING_FILTER = [
    "setback", "zone", "density", "height limit",
    "lot width", "rear yard", "front yard",
    "floor space", "fsi", "permitted use"
]

ZONE_CODE_PATTERN = re.compile(r"\b(R|C|E|D|A|G|OS|H|RM|RA|IC|M|R[0-9]+|C[0-9]+|RM[0-9]+)[- ]?[A-Z0-9]*\b")


# ==================================================
# TEXT FILTERING HELPERS
# ==================================================

def is_junk_text(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in JUNK_TERMS)


def is_legal_rule(text: str) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in LEGAL_PATTERNS)


# ==================================================
# ZONING EXTRACTION
# ==================================================

def extract_zoning_rules(text: str):
    rules = []
    sentences = re.split(r'[.!?]', text)

    for sentence in sentences:
        clean = sentence.strip()
        if len(clean) < 40:
            continue
        if is_junk_text(clean):
            continue
        if is_legal_rule(clean):
            rules.append(clean)

    return rules


def extract_zone_codes(text: str):
    matches = ZONE_CODE_PATTERN.findall(text)
    return list(set(matches))


# ==================================================
# PERMIT CLASSIFICATION HELPERS
# ==================================================

def detect_job_type(text: str):
    lower = text.lower()

    if "deck" in lower:
        return "deck-construction"
    if "fence" in lower:
        return "fence"
    if "demolition" in lower:
        return "demolition"
    if "addition" in lower:
        return "home-addition"
    if "basement" in lower:
        return "basement-finish"
    if "garage" in lower:
        return "garage"
    if "renovation" in lower:
        return "renovation"

    return "general-construction"


CLASSIFICATION_PATTERNS = {
    "core-permit": ["required", "permit is required", "must obtain"],
    "project-permit": ["before applying", "application process", "project"],
    "informational": ["find out more", "learn more", "how to"]
}


def classify_permit_type(text: str):
    lower = text.lower()
    for permit_type, patterns in CLASSIFICATION_PATTERNS.items():
        if any(p in lower for p in patterns):
            return permit_type
    return "informational"


# ==================================================
# VALID PERMIT DETECTOR
# ==================================================

def is_valid_permit_text(text: str) -> bool:
    lower = text.lower()

    if is_junk_text(lower):
        return False
    if "permit" not in lower:
        return False
    if len(text) < 50:
        return False

    return True


# ==================================================
# DEEP ZONING CRAWLER
# ==================================================

def deep_scrape_zoning_pages(
    start_url,
    city,
    authority,
    authority_level="Municipal",
    visited=None,
    max_depth=3,
    domain_filter=None
):
    if visited is None:
        visited = set()

    results = []

    ALLOWED_ZONING_PATHS = [
        "zoning",
        "zoning-by-law",
        "zoning-by-laws",
        "official-plan/zoning",
        "planning/zoning"
    ]

    BLOCKED_PATHS = [
        "bylaw-enforcement",
        "noise", "garbage", "dogs", "litter",
        "parking", "taxes", "permits-licences",
        "election", "social", "share", "facebook",
        "twitter", "linkedin"
    ]

    def normalize_url(url):
        return url.split("#")[0].split("?")[0]

    def is_valid_zoning_url(url):
        url = normalize_url(url).lower()

        if not url.startswith("http"):
            return False

        if domain_filter and domain_filter not in url:
            return False

        if any(block in url for block in BLOCKED_PATHS):
            return False

        return any(path in url for path in ALLOWED_ZONING_PATHS)

    def crawl(url, depth):
        url = normalize_url(url)

        if depth > max_depth:
            return

        if url in visited:
            return

        if not is_valid_zoning_url(url):
            return

        visited.add(url)

        try:
            print(f"🔎 Crawling zoning page: {url}")

            response = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            lower_text = text.lower()

            # Content quality gate
            if not any(term in lower_text for term in [
                "setback", "zone", "density", "height",
                "floor space", "fsi", "rear yard",
                "front yard", "lot width"
            ]):
                return

            zone_codes = extract_zone_codes(text)
            zoning_rules = extract_zoning_rules(text)

            if not zone_codes and not zoning_rules:
                return

            results.append({
                "city": city,
                "type": "zoning-rule",
                "authority": authority,
                "authorityLevel": authority_level,
                "section": text[:500],
                "zoneCodes": zone_codes,
                "zoningRules": zoning_rules,
                "url": url
            })

            for link in soup.find_all("a", href=True):
                next_url = urljoin(url, link["href"])
                next_url = normalize_url(next_url)

                if any(ext in next_url.lower() for ext in DISALLOWED_EXTENSIONS):
                    continue

                crawl(next_url, depth + 1)

        except Exception as e:
            print(f"⚠️ Error crawling zoning page: {url} → {e}")

    crawl(start_url, 0)
    return results


# ==================================================
# RULE CLASSIFIER
# ==================================================

def classify_rule_type(rule: str):
    lower = rule.lower()

    if "height" in lower:
        return "height-restriction"
    if "setback" in lower:
        return "setback-requirement"
    if "coverage" in lower:
        return "lot-coverage"
    if "density" in lower:
        return "density-limit"
    if "prohibited" in lower:
        return "prohibition"

    return "general"
