"""
Validates toronto_permit_rules.json structure and content.

Checks:
  - Required top-level keys are present
  - meta block has required fields
  - Every rule entry has required fields with correct types
  - IDs follow expected format (PR-### / PNR-###) and are unique
  - No empty keywords or descriptions
  - URLs are plausible (start with https://)
  - permit_required entries have apply_url
  - Conditions are a list (never a string)
  - Cross-check: PR and PNR items don't share the same project_type
"""

import json
import re
import os
from urllib.parse import urlparse

RULES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "toronto_permit_rules.json"
)

# Required top-level keys
TOP_LEVEL_REQUIRED = {
    "meta", "permit_required", "permit_not_required",
    "always_required_notes", "apply_url", "fees_url"
}

META_REQUIRED = {"source", "source_authority", "jurisdiction", "last_scraped"}

# Required fields per rule entry
RULE_REQUIRED = {"id", "project_type", "description", "keywords"}

PR_ID_PATTERN = re.compile(r"^PR-\d{3}$")
PNR_ID_PATTERN = re.compile(r"^PNR-\d{3}$")


def _is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def validate_meta(meta: dict, errors: list):
    for field in META_REQUIRED:
        if field not in meta or not meta[field]:
            errors.append(f"meta: missing or empty field '{field}'")

    if "source" in meta and not _is_valid_url(meta["source"]):
        errors.append(f"meta.source is not a valid URL: '{meta['source']}'")


def validate_rule(rule: dict, section: str, id_pattern: re.Pattern, seen_ids: set, seen_types: set, errors: list):
    entry_label = f"[{section} / {rule.get('id', '???')}]"

    # Required fields
    for field in RULE_REQUIRED:
        if field not in rule:
            errors.append(f"{entry_label}: missing required field '{field}'")
        elif not rule[field] and field != "conditions":
            errors.append(f"{entry_label}: field '{field}' is empty")

    # ID format
    rule_id = rule.get("id", "")
    if rule_id:
        if not id_pattern.match(rule_id):
            errors.append(f"{entry_label}: ID '{rule_id}' does not match expected pattern")
        if rule_id in seen_ids:
            errors.append(f"{entry_label}: duplicate ID '{rule_id}'")
        seen_ids.add(rule_id)

    # project_type uniqueness across sections
    pt = rule.get("project_type", "").strip().lower()
    if pt in seen_types:
        errors.append(f"{entry_label}: duplicate project_type '{rule.get('project_type')}'")
    if pt:
        seen_types.add(pt)

    # keywords must be a non-empty list
    keywords = rule.get("keywords")
    if keywords is not None:
        if not isinstance(keywords, list):
            errors.append(f"{entry_label}: 'keywords' must be a list, got {type(keywords).__name__}")
        elif len(keywords) == 0:
            errors.append(f"{entry_label}: 'keywords' list is empty")

    # conditions must be a list (never accidentally a string)
    conditions = rule.get("conditions")
    if conditions is not None and not isinstance(conditions, list):
        errors.append(f"{entry_label}: 'conditions' must be a list, got {type(conditions).__name__}")

    # permit_required entries must have apply_url
    if section == "permit_required":
        apply_url = rule.get("apply_url", "")
        if not apply_url:
            errors.append(f"{entry_label}: missing 'apply_url'")
        elif not _is_valid_url(apply_url):
            errors.append(f"{entry_label}: 'apply_url' is not a valid URL: '{apply_url}'")

        # permit_types must be present and non-empty for PR entries
        permit_types = rule.get("permit_types")
        if not permit_types:
            errors.append(f"{entry_label}: missing or empty 'permit_types'")
        elif not isinstance(permit_types, list):
            errors.append(f"{entry_label}: 'permit_types' must be a list")


def validate(path: str = RULES_PATH) -> tuple[bool, list[str], list[str]]:
    """
    Load and validate the rules JSON at path.
    Returns (is_valid, errors, warnings).
    """
    errors = []
    warnings = []

    # Load file
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return False, [f"File not found: {path}"], []
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"], []

    # Top-level keys
    for key in TOP_LEVEL_REQUIRED:
        if key not in data:
            errors.append(f"Top-level key missing: '{key}'")

    # meta block
    meta = data.get("meta", {})
    validate_meta(meta, errors)

    # Top-level URLs
    for url_key in ("apply_url", "fees_url"):
        url = data.get(url_key, "")
        if not _is_valid_url(url):
            errors.append(f"Top-level '{url_key}' is not a valid URL: '{url}'")

    # Sections
    permit_required = data.get("permit_required", [])
    permit_not_required = data.get("permit_not_required", [])

    if not isinstance(permit_required, list) or len(permit_required) == 0:
        errors.append("'permit_required' must be a non-empty list")

    if not isinstance(permit_not_required, list) or len(permit_not_required) == 0:
        errors.append("'permit_not_required' must be a non-empty list")

    seen_ids: set = set()
    seen_types: set = set()

    for rule in permit_required:
        validate_rule(rule, "permit_required", PR_ID_PATTERN, seen_ids, seen_types, errors)

    for rule in permit_not_required:
        validate_rule(rule, "permit_not_required", PNR_ID_PATTERN, seen_ids, seen_types, errors)

    # always_required_notes must be a non-empty list of strings
    notes = data.get("always_required_notes", [])
    if not isinstance(notes, list) or len(notes) == 0:
        errors.append("'always_required_notes' must be a non-empty list")
    else:
        for i, note in enumerate(notes):
            if not isinstance(note, str) or not note.strip():
                errors.append(f"always_required_notes[{i}]: must be a non-empty string")

    # Warnings (non-blocking)
    total = len(permit_required) + len(permit_not_required)
    if total < 10:
        warnings.append(f"Only {total} rules found — seems low. Verify the source page was fully scraped.")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def print_report(is_valid: bool, errors: list[str], warnings: list[str]):
    if is_valid:
        print("✅ toronto_permit_rules.json is valid")
    else:
        print(f"❌ Validation failed — {len(errors)} error(s):")
        for e in errors:
            print(f"   • {e}")

    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"   • {w}")


if __name__ == "__main__":
    is_valid, errors, warnings = validate()
    print_report(is_valid, errors, warnings)
