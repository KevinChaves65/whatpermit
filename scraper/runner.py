from mongo import save_records
from locations.toronto import scrape_toronto_permits, scrape_toronto_zoning
from locations.mississauga import scrape_mississauga_permits, scrape_mississauga_zoning
from locations.oakville import scrape_oakville_permits, scrape_oakville_zoning


def normalize_record(record):
    """
    Ensures every record has required base fields
    Prevents KeyError crashes on save
    """
    base = {
        "city": record.get("city", "Unknown"),
        "type": record.get("type", "unknown"),
        "section": record.get("section", record.get("permitName", "No section provided")),
        "url": record.get("url", ""),
        "authority": record.get("authority", ""),
        "authorityLevel": record.get("authorityLevel", ""),
        "jobType": record.get("jobType", "general"),
        "permitName": record.get("permitName", ""),
        "permitRequired": record.get("permitRequired", False),
        "zoneCodes": record.get("zoneCodes", []),
        "zoningRules": record.get("zoningRules", []),
        "projectPages": record.get("projectPages", []),
        "bylawLinks": record.get("bylawLinks", [])
    }

    # Merge with original to preserve extra fields
    return {**base, **record}


def run_all_scrapers():
    all_records = []

    print("\n========== RUNNING SCRAPERS ==========\n")

    # --- Toronto ---
    toronto_permits = scrape_toronto_permits()
    toronto_zoning = scrape_toronto_zoning()

    # --- Mississauga ---
    miss_permits = scrape_mississauga_permits()
    miss_zoning = scrape_mississauga_zoning()

    # --- Oakville ---
    oakville_permits = scrape_oakville_permits()
    oakville_zoning = scrape_oakville_zoning()

    raw_records = (
        toronto_permits
        + toronto_zoning
        + miss_permits
        + miss_zoning
        + oakville_permits
        + oakville_zoning
    )

    for record in raw_records:
        all_records.append(normalize_record(record))

    print(f"\n✅ TOTAL RECORDS READY TO SAVE: {len(all_records)}\n")
    save_records(all_records)


if __name__ == "__main__":
    run_all_scrapers()
