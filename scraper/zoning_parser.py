# zoning_parser.py
# Shared intelligence utilities for WhatPermit scrapers

import re



NON_PERMIT_PHRASES = [
    "before you apply",
    "after you apply",
    "everything you need to know",
    "forms, documents",
    "additional resources",
    "share this page",
    "translation",
    "print this page",
    "terms and conditions"
]


def is_valid_permit_text(text: str) -> bool:
    lower = text.lower()

    # Reject filler / navigation content
    for phrase in NON_PERMIT_PHRASES:
        if phrase in lower:
            return False

    # Must include strong permit indicators
    return any(keyword in lower for keyword in [
        "permit is required",
        "required under the building code",
        "must obtain a permit",
        "building permit",
        "zoning permit"
    ])



ZONING_KEYWORDS = [
    "setback",
    "height",
    "lot coverage",
    "minimum distance",
    "residential zone",
    "zoning by-law",
    "rear yard",
    "side yard"
]


def extract_zoning_rules(text: str):
    rules = []
    for sentence in text.split('.'):
        sentence = sentence.strip()

        if not sentence:
            continue

        for keyword in ZONING_KEYWORDS:
            if keyword.lower() in sentence.lower() and len(sentence) > 15:
                rules.append(sentence)
                break

    return rules



ZONE_PATTERN = re.compile(r"\b(R|RM|RS|RD|CR|C|I)-?\d*\b", re.IGNORECASE)


def extract_zone_codes(text: str):
    return list(set([z.upper() for z in ZONE_PATTERN.findall(text)]))



JOB_KEYWORDS = {
    "deck-construction": ["deck"],
    "fence-installation": ["fence"],
    "garage-construction": ["garage", "carport"],
    "basement-renovation": ["basement"],
    "home-addition": ["addition", "extension"],
    "shed-construction": ["shed"],
    "demolition": ["demolition"],
}


def detect_job_type(text: str):
    lower = text.lower()

    for job, keywords in JOB_KEYWORDS.items():
        for word in keywords:
            if word in lower:
                return job

    return "general-construction"



PROJECT_KEYWORDS = [
    "deck", "shed", "garage", "pool",
    "fence", "renovation", "addition",
    "basement", "driveway", "porch"
]


def find_project_subpages(soup):
    projects = []

    for link in soup.find_all("a", href=True):
        title = link.get_text(strip=True)
        lower = title.lower()
        url = link["href"]

        if not url.startswith("http"):
            continue

        if any(keyword in lower for keyword in PROJECT_KEYWORDS):
            projects.append({
                "title": title,
                "url": url
            })

    return projects


def classify_permit_type(text: str) -> str:
    lower = text.lower()

    strong_core_phrases = [
        "permit is required under the building code act",
        "a building permit is required",
        "must obtain a building permit",
        "you need a building permit",
    ]

    if any(p in lower for p in strong_core_phrases):
        return "core-permit"

    # If it mentions specific project keywords, treat as project-specific
    if any(word in lower for word in PROJECT_KEYWORDS):
        return "project-permit"

    return "informational"