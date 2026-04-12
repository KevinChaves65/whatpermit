"""
Diffs the live-scraped Toronto permit rule list against the stored JSON.

Three comparison strategies, layered:

1. Hash check  — if page_hash matches last snapshot, nothing changed. Fast exit.
2. Count check — if number of permit_required / permit_not_required items changed,
                 flag it immediately (rule added or removed).
3. Text diff   — fuzzy-match each stored rule's project_type against scraped items.
                 Flag rules whose description has significantly changed.
                 Flag rules present in stored JSON but absent from live page (deleted).
                 Flag scraped items with no match in stored JSON (new rules).

Output is a ChangeReport dict:
{
    "has_changes": bool,
    "page_hash_changed": bool,
    "count_changed": bool,
    "added": [ { project_type, raw_text } ],          # in live page, not in JSON
    "removed": [ { id, project_type } ],              # in JSON, not in live page
    "modified": [ { id, project_type, stored_text, live_text } ],
    "summary": "human-readable one-liner"
}
"""

import json
import os
import re

RULES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "toronto_permit_rules.json"
)

# How similar a live item's text must be to a stored item's description to be
# considered a "match" (0–1). Below this → treated as a modification.
SIMILARITY_THRESHOLD = 0.5


def _normalise(text: str) -> set[str]:
    """Tokenise a string into a set of lowercase words for similarity scoring."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _similarity(a: str, b: str) -> float:
    """Jaccard similarity between two strings' word sets."""
    set_a = _normalise(a)
    set_b = _normalise(b)
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _best_match(stored_type: str, stored_desc: str, scraped_items: list[dict]) -> tuple[dict | None, float]:
    """Find the scraped item most similar to a stored rule's project_type + description."""
    best = None
    best_score = 0.0
    query = f"{stored_type} {stored_desc}"

    for item in scraped_items:
        candidate = f"{item['project_type']} {item['description']}"
        score = _similarity(query, candidate)
        if score > best_score:
            best_score = score
            best = item

    return best, best_score


def diff(stored_data: dict, live_data: dict, last_page_hash: str | None = None) -> dict:
    """
    Compare stored JSON data against live scrape result.

    stored_data  — the parsed toronto_permit_rules.json dict
    live_data    — the dict returned by scrape_rules.scrape()
    last_page_hash — hash stored from the previous run (None if first run)
    """
    report = {
        "has_changes": False,
        "page_hash_changed": False,
        "count_changed": False,
        "added": [],
        "removed": [],
        "modified": [],
        "summary": "",
        "scraped_at": live_data.get("scraped_at"),
        "page_hash": live_data.get("page_hash"),
    }

    # If the scraper failed, we can't diff
    if not live_data.get("ok"):
        report["summary"] = f"⚠️  Scraper failed: {live_data.get('error')}"
        return report

    current_hash = live_data.get("page_hash")

    # 1. Hash check
    if last_page_hash and current_hash == last_page_hash:
        report["summary"] = "✅ No changes detected (page hash identical to last snapshot)"
        return report

    if last_page_hash and current_hash != last_page_hash:
        report["page_hash_changed"] = True

    # 2. Count check
    stored_required = stored_data.get("permit_required", [])
    stored_not_required = stored_data.get("permit_not_required", [])
    live_required = live_data.get("permit_required", [])
    live_not_required = live_data.get("permit_not_required", [])

    if len(stored_required) != len(live_required) or len(stored_not_required) != len(live_not_required):
        report["count_changed"] = True

    # 3. Text diff — permit_required section
    _diff_section(
        stored_rules=stored_required,
        live_items=live_required,
        added_list=report["added"],
        removed_list=report["removed"],
        modified_list=report["modified"],
    )

    # 3b. Text diff — permit_not_required section
    _diff_section(
        stored_rules=stored_not_required,
        live_items=live_not_required,
        added_list=report["added"],
        removed_list=report["removed"],
        modified_list=report["modified"],
    )

    report["has_changes"] = bool(
        report["page_hash_changed"]
        or report["count_changed"]
        or report["added"]
        or report["removed"]
        or report["modified"]
    )

    # Build summary
    parts = []
    if report["added"]:
        parts.append(f"{len(report['added'])} new rule(s)")
    if report["removed"]:
        parts.append(f"{len(report['removed'])} removed rule(s)")
    if report["modified"]:
        parts.append(f"{len(report['modified'])} modified rule(s)")
    if report["page_hash_changed"] and not parts:
        parts.append("page content changed (possible formatting update)")

    report["summary"] = (
        "⚠️  Changes detected: " + ", ".join(parts)
        if parts
        else "✅ No significant rule changes detected"
    )

    return report


def _diff_section(
    stored_rules: list[dict],
    live_items: list[dict],
    added_list: list,
    removed_list: list,
    modified_list: list,
):
    matched_live_indices = set()

    for stored in stored_rules:
        stored_type = stored.get("project_type", "")
        stored_desc = stored.get("description", "")
        rule_id = stored.get("id", "")

        best_item, score = _best_match(stored_type, stored_desc, live_items)

        if best_item is None or score < 0.2:
            # No reasonable match found — rule may have been removed
            removed_list.append({
                "id": rule_id,
                "project_type": stored_type,
                "note": "No matching entry found on live page",
            })
            continue

        live_idx = live_items.index(best_item)
        matched_live_indices.add(live_idx)

        # Check if it looks meaningfully different
        if score < SIMILARITY_THRESHOLD:
            modified_list.append({
                "id": rule_id,
                "project_type": stored_type,
                "stored_description": stored_desc,
                "live_description": best_item.get("description", ""),
                "live_raw_text": best_item.get("raw_text", ""),
                "similarity_score": round(score, 3),
            })

    # Any live items with no match in stored JSON = newly added rules
    for i, item in enumerate(live_items):
        if i not in matched_live_indices:
            added_list.append({
                "project_type": item.get("project_type", ""),
                "raw_text": item.get("raw_text", ""),
                "note": "Found on live page, not in stored JSON",
            })


def load_stored() -> dict:
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def print_report(report: dict):
    print(f"\n{'='*50}")
    print(f"DIFF REPORT — {report.get('scraped_at', 'unknown date')}")
    print(f"{'='*50}")
    print(f"Summary: {report['summary']}")
    print(f"Hash changed: {report['page_hash_changed']} | Count changed: {report['count_changed']}")

    if report["added"]:
        print(f"\n🆕 ADDED ({len(report['added'])}):")
        for item in report["added"]:
            print(f"   + {item['project_type']}")
            print(f"     {item['raw_text'][:120]}")

    if report["removed"]:
        print(f"\n🗑️  REMOVED ({len(report['removed'])}):")
        for item in report["removed"]:
            print(f"   - [{item['id']}] {item['project_type']}")

    if report["modified"]:
        print(f"\n✏️  MODIFIED ({len(report['modified'])}):")
        for item in report["modified"]:
            print(f"   ~ [{item['id']}] {item['project_type']} (similarity: {item['similarity_score']})")
            print(f"     STORED: {item['stored_description'][:100]}")
            print(f"     LIVE:   {item['live_description'][:100]}")

    print()


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from pipeline.scrape_rules import scrape

    stored = load_stored()
    live = scrape()
    report = diff(stored, live)
    print_report(report)
