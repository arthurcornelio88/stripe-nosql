from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["supabase_snapshot"]

# Charges suspectes
print("Charges > 1000€ :")
for doc in db["charges"].find({"amount": {"$gt": 1000}}):
    print(doc)

# Clients avec plusieurs paiements
pipeline = [
    {"$group": {"_id": "$customer_id", "count": {"$sum": 1}}},
    {"$match": {"count": {"$gt": 1}}}
]
print("Clients multi-paiements :")
for doc in db["charges"].aggregate(pipeline):
    print(doc)
