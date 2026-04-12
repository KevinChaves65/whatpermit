"""
Snapshot — stores and retrieves Toronto permit rule snapshots in MongoDB.

Collection: rule_snapshots
  Each document:
  {
    "source_url": "https://...",
    "scraped_at": "YYYY-MM-DD",
    "page_hash": "sha256...",
    "permit_required_count": 19,
    "permit_not_required_count": 17,
    "scrape_data": { ... full live scrape result ... },
    "has_changes": bool,
    "diff_report": { ... full diff report ... }
  }

Collection: rule_change_log
  Each document records a detected change event for auditing:
  {
    "detected_at": "YYYY-MM-DD",
    "summary": "...",
    "added": [...],
    "removed": [...],
    "modified": [...]
  }
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient, DESCENDING
from config import MONGO_URI, DB_NAME


def _get_db():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[DB_NAME]


def get_last_snapshot() -> dict | None:
    """Return the most recent snapshot document, or None if no snapshots exist."""
    db = _get_db()
    doc = db["rule_snapshots"].find_one(
        {"source_url": {"$exists": True}},
        sort=[("scraped_at", DESCENDING)]
    )
    return doc


def get_last_page_hash() -> str | None:
    """Return the page_hash from the most recent snapshot, or None."""
    snapshot = get_last_snapshot()
    if snapshot:
        return snapshot.get("page_hash")
    return None


def save_snapshot(live_data: dict, diff_report: dict):
    """
    Save a scrape result + diff report as a new snapshot document.
    Also writes to the change log if changes were detected.
    """
    db = _get_db()

    snapshot_doc = {
        "source_url": live_data.get("source_url"),
        "scraped_at": live_data.get("scraped_at"),
        "page_hash": live_data.get("page_hash"),
        "permit_required_count": len(live_data.get("permit_required", [])),
        "permit_not_required_count": len(live_data.get("permit_not_required", [])),
        "scrape_data": live_data,
        "has_changes": diff_report.get("has_changes", False),
        "diff_report": diff_report,
    }

    db["rule_snapshots"].insert_one(snapshot_doc)
    print(f"💾 Snapshot saved for {live_data.get('scraped_at')} (hash: {live_data.get('page_hash', '')[:12]}...)")

    # Write to change log if anything changed
    if diff_report.get("has_changes"):
        change_doc = {
            "detected_at": live_data.get("scraped_at"),
            "summary": diff_report.get("summary"),
            "page_hash": live_data.get("page_hash"),
            "added": diff_report.get("added", []),
            "removed": diff_report.get("removed", []),
            "modified": diff_report.get("modified", []),
        }
        db["rule_change_log"].insert_one(change_doc)
        print(f"⚠️  Change logged to rule_change_log")


def get_change_history(limit: int = 10) -> list[dict]:
    """Return the last N change log entries."""
    db = _get_db()
    cursor = db["rule_change_log"].find(
        {},
        {"_id": 0},
        sort=[("detected_at", DESCENDING)],
        limit=limit
    )
    return list(cursor)


if __name__ == "__main__":
    # Quick diagnostic: print last snapshot info
    snap = get_last_snapshot()
    if snap:
        print(f"Last snapshot: {snap.get('scraped_at')} | hash: {snap.get('page_hash', '')[:16]}...")
        print(f"  permit_required: {snap.get('permit_required_count')} items")
        print(f"  permit_not_required: {snap.get('permit_not_required_count')} items")
        print(f"  had changes: {snap.get('has_changes')}")
    else:
        print("No snapshots found in database.")

    history = get_change_history()
    if history:
        print(f"\nChange log ({len(history)} entries):")
        for entry in history:
            print(f"  {entry['detected_at']}: {entry['summary']}")
