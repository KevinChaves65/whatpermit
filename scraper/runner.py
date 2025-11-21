from mongo import get_collection
from locations.mississauga import scrape_mississauga
from locations.oakville import scrape_oakville
from locations.toronto import scrape_toronto



collection = get_collection()

def save_permits(permits):
    for permit in permits:
        collection.update_one(
            {"city": permit["city"], "permitName": permit["permitName"]},
            {"$set": permit},
            upsert=True
        )

if __name__ == "__main__":
    all_permits = []

    all_permits.extend(scrape_mississauga())
    all_permits.extend(scrape_oakville())
    all_permits.extend(scrape_toronto())

    save_permits(all_permits)

    print(f"✅ {len(all_permits)} permits saved to MongoDB")