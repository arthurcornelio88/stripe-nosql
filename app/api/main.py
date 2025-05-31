from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId
import os

app = FastAPI()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["supabase_snapshot"]

def convert_objectid(doc):
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])
    return doc

@app.get("/charges/fraud")
def get_fraudulent_charges():
    pipeline = [
        {"$match": {"amount": {"$gt": 1000}, "paid": True}},
        {"$group": {"_id": "$payment_method", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$sort": {"total": -1}}
    ]
    return [convert_objectid(doc) for doc in db.charges.aggregate(pipeline)]

@app.get("/subscriptions/active")
def get_active_subscriptions():
    return [convert_objectid(doc) for doc in db.subscriptions.find({"status": "active"})]

@app.get("/payment_intents/3ds")
def get_3ds_payment_intents():
    return [convert_objectid(doc) for doc in db.payment_intents.find({
        "payment_method_options.card.request_three_d_secure": "automatic"
    })]

@app.get("/customers")
def list_customers():
    cursor = db.customers.find({}, {"id": 1, "name": 1, "email": 1, "_id": 0})
    return list(cursor)

@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    result = db.customers.find_one({"id": customer_id})
    return convert_objectid(result)
