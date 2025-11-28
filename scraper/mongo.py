from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME


def get_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print("Mongo URI Loaded:", MONGO_URI)
    return db[COLLECTION_NAME]


def save_records(records):
    collection = get_collection()

    saved = 0
    updated = 0

    for record in records:
        city = record.get("city")
        section = record.get("section")

        if not city or not section:
            print("⚠️ Skipping malformed record (missing city or section)")
            continue

        result = collection.update_one(
            {"city": city, "section": section}, 
            {"$set": record},
            upsert=True
        )

        if result.matched_count:
            updated += 1
        else:
            saved += 1

    print(f"💾 Saved {saved} new records | 🔄 Updated {updated} existing records")
