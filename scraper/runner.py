from locations.toronto import scrape_toronto_permits, scrape_toronto_zoning
from mongo import get_collection

collection = get_collection()

def save_records(records):
    for record in records:
        collection.update_one(
            {"city": record["city"], "section": record["section"]},
            {"$set": record},
            upsert=True
        )

if __name__ == "__main__":
    all_records = []
    all_records.extend(scrape_toronto_permits())
    all_records.extend(scrape_toronto_zoning())
    save_records(all_records)

    print(f"✅ {len(all_records)} Toronto records saved")