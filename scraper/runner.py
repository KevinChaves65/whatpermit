from locations.toronto import scrape_toronto_permits, scrape_toronto_zoning
from locations.mississauga import scrape_mississauga_permits, scrape_mississauga_zoning
from locations.oakville import scrape_oakville_permits, scrape_oakville_zoning
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
    #all_records.extend(scrape_mississauga_permits())
    #all_records.extend(scrape_mississauga_zoning())
    #all_records.extend(scrape_oakville_permits())
    #all_records.extend(scrape_oakville_zoning())

    save_records(all_records)
    print(f"✅ {len(all_records)} records saved")