import mongomock
import pytest
from scripts.nosql_io import load_latest_oltp_json_from_gcs
from scripts.gcp import configure_gcp_credentials
import os
from dotenv import load_dotenv


# Code à tester
def insert_into_mock_mongo(data: dict, db):
    for name, records in data.items():
        if isinstance(records, list) and records:
            db[name].insert_many(records)

@pytest.fixture(scope="module")
def mock_mongo_db():
    client = mongomock.MongoClient()
    return client["test_db"]

def test_load_and_insert_oltp_json(mock_mongo_db):
    load_dotenv(override=False)
    ENV = os.getenv("ENV", "DEV").upper()
    configure_gcp_credentials()
    data = load_latest_oltp_json_from_gcs()

    assert isinstance(data, dict), "Dump should return a dict of collections"
    assert "customers" in data, "Expected 'customers' in JSON keys"

    insert_into_mock_mongo(data, mock_mongo_db)

    # Vérifie que des documents sont insérés
    assert mock_mongo_db["customers"].count_documents({}) > 0
    assert mock_mongo_db["invoices"].count_documents({}) > 0

    print("✅ JSON loaded and inserted into MongoDB (mock) successfully.")
