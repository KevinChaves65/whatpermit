"""
check_changes.py — entry point for the Toronto permit rule change detection pipeline.

Steps:
  1. Validate toronto_permit_rules.json (abort if invalid)
  2. Load last page hash from MongoDB (skip full diff if page hasn't changed)
  3. Scrape the live Toronto permit rules page
  4. Diff live scrape against stored JSON
  5. Save snapshot + change log to MongoDB
  6. Print report

Usage:
  python pipeline/check_changes.py             # full run
  python pipeline/check_changes.py --validate-only   # only validate JSON, no scraping
  python pipeline/check_changes.py --history         # print change history from DB
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.validate_rules import validate, print_report as print_validation_report
from pipeline.scrape_rules import scrape
from pipeline.diff_rules import diff, load_stored, print_report as print_diff_report
from pipeline.snapshot import get_last_page_hash, save_snapshot, get_change_history

RULES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "toronto_permit_rules.json"
)


def run_validate_only():
    print("\n========== VALIDATING toronto_permit_rules.json ==========\n")
    is_valid, errors, warnings = validate(RULES_PATH)
    print_validation_report(is_valid, errors, warnings)
    return is_valid


def run_history():
    print("\n========== CHANGE HISTORY ==========\n")
    history = get_change_history(limit=20)
    if not history:
        print("No changes recorded yet.")
        return
    for entry in history:
        print(f"  {entry['detected_at']}: {entry['summary']}")
        if entry.get("added"):
            for item in entry["added"]:
                print(f"    🆕 {item['project_type']}")
        if entry.get("removed"):
            for item in entry["removed"]:
                print(f"    🗑️  [{item['id']}] {item['project_type']}")
        if entry.get("modified"):
            for item in entry["modified"]:
                print(f"    ✏️  [{item['id']}] {item['project_type']}")
        print()


def run():
    print("\n========== TORONTO PERMIT RULE CHANGE DETECTION ==========\n")

    # Step 1: Validate stored JSON
    print("--- Step 1: Validate stored JSON ---")
    is_valid, errors, warnings = validate(RULES_PATH)
    print_validation_report(is_valid, errors, warnings)

    if not is_valid:
        print("\n❌ Aborting — fix validation errors in toronto_permit_rules.json before running change detection.")
        sys.exit(1)

    # Step 2: Get last hash
    print("\n--- Step 2: Load last snapshot hash ---")
    last_hash = get_last_page_hash()
    if last_hash:
        print(f"   Last known hash: {last_hash[:16]}...")
    else:
        print("   No previous snapshot found — this will be the baseline run.")

    # Step 3: Scrape live page
    print("\n--- Step 3: Scrape live Toronto permit page ---")
    live_data = scrape()

    if not live_data["ok"]:
        print(f"\n❌ Scrape failed: {live_data['error']}")
        sys.exit(1)

    # Step 4: Diff
    print("\n--- Step 4: Diff live data vs stored JSON ---")
    stored = load_stored()
    report = diff(stored, live_data, last_page_hash=last_hash)
    print_diff_report(report)

    # Step 5: Save snapshot
    print("--- Step 5: Save snapshot to MongoDB ---")
    save_snapshot(live_data, report)

    # Final status
    if report["has_changes"]:
        print("⚠️  ACTION REQUIRED: Review the changes above and update toronto_permit_rules.json accordingly.")
    else:
        print("✅ toronto_permit_rules.json is up to date with the live Toronto page.")

    print("\n========== DONE ==========\n")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--validate-only" in args:
        run_validate_only()
    elif "--history" in args:
        run_history()
    else:
        run()
