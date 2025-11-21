import re

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

JOB_KEYWORDS = {
    "deck": ["deck", "platform"],
    "fence": ["fence", "barrier"],
    "garage": ["garage", "carport"],
    "basement": ["basement"],
    "addition": ["addition", "extension"],
    "shed": ["shed", "outbuilding"]
}
ZONE_PATTERN = re.compile(r"\b(R|RM|RS|RD|CR|C|I)-?\d*\b", re.IGNORECASE)

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


def extract_zone_codes(text: str):
    return list(set([z.upper() for z in ZONE_PATTERN.findall(text)]))