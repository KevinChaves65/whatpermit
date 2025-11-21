from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME


def get_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print("Mongo URI Loaded:", MONGO_URI)
    return db[COLLECTION_NAME]