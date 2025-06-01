import os
import json
from pymongo import MongoClient
from gcp import configure_gcp_credentials
from nosql_io import load_latest_oltp_json_from_gcs

ENV = os.getenv("ENV", "DEV").upper()

# MongoDB connection
if ENV == "DEV":
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
else:  # TEST or PROD
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")

MONGO_DB = os.getenv("MONGO_DB", "supabase_snapshot")

def insert_collections_into_mongo(data: dict, db_name: str):
    client = MongoClient(MONGO_URI)
    db = client[db_name]

    for collection_name, records in data.items():
        if isinstance(records, list) and records:
            print(f"📥 Inserting {len(records)} docs into MongoDB collection '{collection_name}'")
            db[collection_name].drop()  # Optionnel : purger avant chaque snapshot
            db[collection_name].insert_many(records)
        else:
            print(f"⚠️ Empty or invalid data for '{collection_name}', skipping.")

def main():
    print("🔐 Configuring GCP credentials...")
    configure_gcp_credentials()

    print("☁️ Loading latest Supabase JSON dump from GCS...")
    data = load_latest_oltp_json_from_gcs()

    print("🧬 Inserting data into MongoDB...")
    insert_collections_into_mongo(data, MONGO_DB)

    print("✅ All data loaded into MongoDB successfully.")

if __name__ == "__main__":
    main()
