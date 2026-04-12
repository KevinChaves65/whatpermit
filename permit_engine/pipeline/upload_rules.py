"""
upload_rules.py — uploads toronto_permit_rules.json to MongoDB in two ways:

1. permit_rules collection  — stores the full JSON as a single city-keyed document.
   Used by the change detection pipeline as the DB reference copy.

2. permits collection  — transforms each rule entry into a city+jobType document
   that the Go backend can query via POST /api/permit/check.

Usage:
  python pipeline/upload_rules.py
"""

import sys
import os
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

RULES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "toronto_permit_rules.json"
)

# Maps keywords found in a rule's project_type/keywords to a canonical jobType.
# Checked in order — first match wins.
KEYWORD_TO_JOB_TYPE = [
    (["deck", "porch", "platform"],             "deck"),
    (["fence"],                                 "fence"),
    (["basement", "second suite", "underpinning",
      "basement apartment", "secondary suite"],  "basement"),
    (["addition", "second storey", "third storey",
      "second floor", "third floor", "sunroom",
      "solarium"],                               "addition"),
    (["garage", "carport", "cabana",
      "pool house", "accessory structure",
      "detached garage"],                        "garage"),
    (["demolition", "tear down", "knock down"],  "demolition"),
    (["renovation", "interior", "alteration",
      "structural", "remove wall", "add wall"],  "renovation"),
    (["shed"],                                   "shed"),
    (["chimney", "fireplace", "wood stove"],     "chimney-fireplace"),
    (["solar", "photovoltaic", "pv system"],     "solar"),
    (["wind turbine", "wind generator"],         "wind-turbine"),
    (["green roof", "rooftop stormwater"],       "green-roof"),
    (["retaining wall"],                         "retaining-wall"),
    (["heating", "hvac", "plumbing", "furnace",
      "boiler", "mechanical"],                   "mechanical-plumbing"),
    (["backwater valve"],                        "backwater-valve"),
    (["backflow prevention"],                    "backflow-prevention"),
    (["change of use"],                          "change-of-use"),
    (["skylight"],                               "skylight"),
    (["insulation"],                             "insulation"),
    (["window", "door replacement"],             "window-door"),
    (["roof replacement", "re-roof", "shingles"],"roof"),
    (["waterproofing"],                          "waterproofing"),
    (["sump pump"],                              "sump-pump"),
    (["tent", "canopy"],                         "temporary-structure"),
    (["cladding", "siding"],                     "cladding"),
    (["cabinetry", "millwork", "cabinets"],      "cabinetry"),
]


def _slugify(text: str) -> str:
    """Convert project_type to a slug for use as a fallback jobType."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _resolve_job_type(rule: dict) -> str:
    """Determine jobType from a rule entry using keyword matching."""
    # Build a combined string from project_type + keywords to match against
    keywords = rule.get("keywords", [])
    project_type = rule.get("project_type", "")
    haystack = (project_type + " " + " ".join(keywords)).lower()

    for terms, job_type in KEYWORD_TO_JOB_TYPE:
        if any(term in haystack for term in terms):
            return job_type

    # Fallback: slugify the project_type
    return _slugify(project_type)


def _transform_rule(rule: dict, permit_required: bool, meta: dict) -> dict:
    """Transform a toronto_permit_rules.json entry into a permits collection document."""
    return {
        "city": "Toronto",
        "jobType": _resolve_job_type(rule),
        "ruleId": rule.get("id"),
        "permitRequired": permit_required,
        "permitName": rule.get("project_type", ""),
        "description": rule.get("description", ""),
        "conditions": rule.get("conditions", []),
        "permitTypes": rule.get("permit_types", []),
        "keywords": rule.get("keywords", []),
        "cost": 0,
        "costNotes": "See fees_url for current fee schedule",
        "documents": [],
        "authority": meta.get("source_authority", "City of Toronto – Toronto Building"),
        "authorityLevel": "Municipal",
        "section": meta.get("legislation", "Ontario Building Code Act"),
        "bylawReference": "Ontario Building Code Act",
        "url": rule.get("apply_url", meta.get("source", "")),
        "notes": rule.get("notes", ""),
        "feesUrl": "",
    }


def upload(rules_path: str = RULES_PATH):
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]

    with open(rules_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("meta", {})

    # -------------------------------------------------------
    # 1. Store full JSON in permit_rules collection
    # -------------------------------------------------------
    result = db["permit_rules"].update_one(
        {"city": "Toronto"},
        {"$set": {
            "city": "Toronto",
            "source_url": meta.get("source"),
            "last_scraped": meta.get("last_scraped"),
            "rules": data,
        }},
        upsert=True,
    )
    action = "Updated" if result.matched_count else "Inserted"
    print(f"📄 permit_rules collection: {action} Toronto document")

    # -------------------------------------------------------
    # 2. Transform rules → permits collection
    # -------------------------------------------------------
    permit_required_rules = data.get("permit_required", [])
    permit_not_required_rules = data.get("permit_not_required", [])

    saved = updated = 0

    for rule in permit_required_rules:
        doc = _transform_rule(rule, permit_required=True, meta=meta)
        res = db["permits"].update_one(
            {"city": doc["city"], "jobType": doc["jobType"], "ruleId": doc["ruleId"]},
            {"$set": doc},
            upsert=True,
        )
        if res.matched_count:
            updated += 1
        else:
            saved += 1

    for rule in permit_not_required_rules:
        doc = _transform_rule(rule, permit_required=False, meta=meta)
        res = db["permits"].update_one(
            {"city": doc["city"], "jobType": doc["jobType"], "ruleId": doc["ruleId"]},
            {"$set": doc},
            upsert=True,
        )
        if res.matched_count:
            updated += 1
        else:
            saved += 1

    print(f"📦 permits collection: 💾 {saved} new | 🔄 {updated} updated")
    print(f"\n✅ Upload complete — {len(permit_required_rules)} permit-required + {len(permit_not_required_rules)} permit-not-required rules loaded")


if __name__ == "__main__":
    upload()
