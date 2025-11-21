from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "whatpermit"
COLLECTION_NAME = "permits"

if not MONGO_URI:
    raise Exception("❌ MONGO_URI not found. Check your .env file")