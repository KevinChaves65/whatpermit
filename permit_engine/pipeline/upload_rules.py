"""
upload_rules.py — uploads all *_permit_rules.json files from the data/ folder
to MongoDB in two ways:

1. permit_rules collection  — stores the full JSON as a single city-keyed document.
   Used by the change detection pipeline as the DB reference copy.

2. permits collection  — transforms each rule entry into a city+jobType document
   that the Go backend can query via POST /api/permit/check.

Usage:
  python pipeline/upload_rules.py              # uploads all cities
  python pipeline/upload_rules.py toronto      # uploads only Toronto
  python pipeline/upload_rules.py mississauga  # uploads only Mississauga
"""

import sys
import os
import json
import re
import glob

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
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
    """Determine jobType from a rule entry.
    Uses the explicit 'job_type' field if present, otherwise falls back to keyword matching.
    """
    if rule.get("job_type"):
        return rule["job_type"]

    # Fallback: keyword matching (kept for rules without explicit job_type)
    keywords = rule.get("keywords", [])
    project_type = rule.get("project_type", "")
    haystack = (project_type + " " + " ".join(keywords)).lower()

    for terms, job_type in KEYWORD_TO_JOB_TYPE:
        if any(term in haystack for term in terms):
            return job_type

    return _slugify(project_type)


def _resolve_required_forms(rule: dict, common_forms: dict) -> list[dict]:
    """
    Expand required_forms entries by merging form metadata from common_forms.
    Each entry becomes: { formId, name, url, mandatory, notes }
    """
    result = []
    for entry in rule.get("required_forms", []):
        form_id = entry.get("form_id")
        form_meta = common_forms.get(form_id, {})
        result.append({
            "formId": form_id,
            "name": form_meta.get("name", form_id),
            "url": form_meta.get("url", ""),
            "mandatory": entry.get("mandatory", False),
            "notes": entry.get("notes", ""),
        })
    # Sort: mandatory first, then conditional
    result.sort(key=lambda f: (0 if f["mandatory"] else 1))
    return result


def _normalize_fee(fee) -> tuple[dict | None, float, str]:
    """Normalize a fee value into (stored_fee, cost, cost_notes).

    Rules:
    - If fee is None → no fee stored.
    - If fee has numeric 'amount' and 'unit' → store as-is, cost = amount.
    - If fee is a complex dict (Mississauga area-based rates) → store as None,
      build a human-readable cost_notes from the dict keys and values.
    """
    if not isinstance(fee, dict):
        return None, 0, "See fees page for current schedule"

    amount = fee.get("amount")
    unit = fee.get("unit", "")

    # Simple {amount, unit} format — amount is a real number
    if isinstance(amount, (int, float)) and amount > 0 and unit:
        return {"amount": float(amount), "unit": unit}, float(amount), unit

    # Complex dict — build a readable note from meaningful keys
    SKIP_KEYS = {"effective", "incentive", "note", "refundable", "currency"}
    lines = []
    for k, v in fee.items():
        if k in SKIP_KEYS or not v:
            continue
        label = k.replace("_", " ").title()
        lines.append(f"{label}: {v}")
    cost_notes = " | ".join(lines) if lines else "See fees page for current schedule"
    return None, 0, cost_notes


def _transform_rule(rule: dict, permit_required: bool, meta: dict, common_forms: dict) -> dict:
    """Transform a permit_rules.json entry into a permits collection document.
    The 'city' field is overwritten by the caller after this returns."""
    stored_fee, cost, cost_notes = _normalize_fee(rule.get("fee"))

    return {
        "city": "",  # overwritten by caller
        "jobType": _resolve_job_type(rule),
        "ruleId": rule.get("id"),
        "permitRequired": permit_required,
        "permitName": rule.get("project_type", ""),
        "description": rule.get("description", ""),
        "conditions": rule.get("conditions", []),
        "permitTypes": rule.get("permit_types", []),
        "keywords": rule.get("keywords", []),
        "fee": stored_fee,
        "cost": cost,
        "costNotes": cost_notes,
        "documents": rule.get("documents", []),
        "requiredForms": _resolve_required_forms(rule, common_forms),
        "authority": meta.get("source_authority", ""),
        "authorityLevel": "Municipal",
        "section": meta.get("legislation", "Ontario Building Code Act"),
        "bylawReference": meta.get("legislation", "Ontario Building Code Act"),
        "url": rule.get("guide_url", rule.get("apply_url", meta.get("source", ""))),
        "applyOnlineUrl": rule.get("apply_online_url") or "",
        "notes": rule.get("notes", ""),
        "feesUrl": meta.get("fees_source", ""),
    }


def _city_name_from_path(rules_path: str) -> str:
    """Derive a display city name from the filename, e.g. toronto_permit_rules.json → Toronto."""
    basename = os.path.basename(rules_path)               # toronto_permit_rules.json
    slug = basename.replace("_permit_rules.json", "")     # toronto
    return slug.replace("-", " ").title()                 # Toronto


def upload(rules_path: str, client: MongoClient):
    db = client[DB_NAME]

    with open(rules_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("meta", {})
    common_forms = data.get("common_forms", {})
    city = _city_name_from_path(rules_path)

    print(f"\n📂 Uploading: {city} ({os.path.basename(rules_path)})")

    # -------------------------------------------------------
    # 1. Store full JSON in permit_rules collection
    # -------------------------------------------------------
    result = db["permit_rules"].update_one(
        {"city": city},
        {"$set": {
            "city": city,
            "source_url": meta.get("source"),
            "last_scraped": meta.get("last_scraped"),
            "rules": data,
        }},
        upsert=True,
    )
    action = "Updated" if result.matched_count else "Inserted"
    print(f"  📄 permit_rules: {action} {city} document")

    # -------------------------------------------------------
    # 2. Transform rules → permits collection
    # -------------------------------------------------------
    permit_required_rules = data.get("permit_required", [])
    permit_not_required_rules = data.get("permit_not_required", [])

    saved = updated = 0

    for rule in permit_required_rules:
        doc = _transform_rule(rule, permit_required=True, meta=meta, common_forms=common_forms)
        doc["city"] = city  # use derived city name, not hardcoded
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
        doc = _transform_rule(rule, permit_required=False, meta=meta, common_forms=common_forms)
        doc["city"] = city
        res = db["permits"].update_one(
            {"city": doc["city"], "jobType": doc["jobType"], "ruleId": doc["ruleId"]},
            {"$set": doc},
            upsert=True,
        )
        if res.matched_count:
            updated += 1
        else:
            saved += 1

    print(f"  📦 permits: 💾 {saved} new | 🔄 {updated} updated")
    print(f"  ✅ {len(permit_required_rules)} permit-required + {len(permit_not_required_rules)} permit-not-required rules")


def upload_all(filter_city: str = None):
    print("🔌 Connecting to MongoDB...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=30000)
    try:
        client.admin.command("ping")
        print("✅ MongoDB connected")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise

    pattern = os.path.join(DATA_DIR, "*_permit_rules.json")
    all_files = sorted(glob.glob(pattern))

    if not all_files:
        print(f"❌ No *_permit_rules.json files found in {DATA_DIR}")
        return

    if filter_city:
        all_files = [f for f in all_files if filter_city.lower() in os.path.basename(f).lower()]
        if not all_files:
            print(f"❌ No rules file found matching '{filter_city}'")
            return

    for path in all_files:
        upload(path, client)

    print(f"\n🏁 Done — {len(all_files)} city file(s) uploaded.")


if __name__ == "__main__":
    filter_city = sys.argv[1] if len(sys.argv) > 1 else None
    upload_all(filter_city)
