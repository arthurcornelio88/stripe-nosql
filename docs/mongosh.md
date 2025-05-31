# 🧪 MongoDB Shell (mongosh) — Guide for Exploration & Debugging

This guide helps you quickly get started with **`mongosh`**, the MongoDB shell, for inspecting and querying your local MongoDB instance loaded with Supabase-style data dumps.

---

## 🐳 1. Installing mongosh with Docker

If `mongosh` is not available on your system or not supported (e.g., Ubuntu 24.04), use the official Docker image:

```bash
docker run -it --rm --network host mongo:7 mongosh "mongodb://localhost:27017"
```

You can alias this for convenience:

```bash
echo "alias mongo-local='docker run -it --rm --network host mongo:7 mongosh \"mongodb://localhost:27017\"'" >> ~/.zshrc
source ~/.zshrc
```

Then use:

```bash
mongo-local
```

---

## ⚙️ 2. Connecting to MongoDB (local)

When using `mongosh` (Docker or native), connect like this:

```bash
mongosh "mongodb://localhost:27017"
```

You should see:

```
Using MongoDB: 7.0.x
Using Mongosh: 2.x
Connecting to: mongodb://localhost:27017/?...
```

Switch to your DB:

```js
use supabase_snapshot
```

---

## 🔍 3. Explore collections

```js
show collections
```

Example:

```
charges
customers
invoices
payment_intents
subscriptions
```

Read one document:

```js
db.customers.findOne()
```

Count:

```js
db.subscriptions.countDocuments()
```

---

## 🧠 4. Example queries for inspection & fraud detection

### 💰 Charges > 1000€

```js
db.charges.find({ amount: { $gt: 1000 } })
```

### 🧮 Group charges by customer

```js
db.charges.aggregate([
  { $group: { _id: "$customer_id", count: { $sum: 1 }, total: { $sum: "$amount" } } },
  { $sort: { total: -1 } }
])
```

### 🔐 3D Secure activated intents

```js
db.payment_intents.find({
  "payment_method_options.card.request_three_d_secure": "automatic"
})
```

### 📦 Active subscriptions

```js
db.subscriptions.find({ status: "active" })
```

---

## 🧪 Alternative: explore with Python (mongo\_queries.py)

If you don’t want to use `mongosh`, you can interact via `pymongo`:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["supabase_snapshot"]

charges = list(db.charges.find({"amount": {"$gt": 1000}}))
for charge in charges:
    print(charge["id"], charge["amount"])
```

---

## 📎 Summary

| Task                 | Method                                    |
| -------------------- | ----------------------------------------- |
| CLI inspection       | `mongosh` or `docker run mongo:7 mongosh` |
| Programmatic queries | Python + `pymongo`                        |
| GUI                  | MongoDB Compass (optional)                |

---

## 🧼 Tip: clear or reload a collection

```js
db.customers.drop()             // deletes the collection
mongoimport --jsonArray ...    // reload from dump
```

---

## ✅ Conclusion

Use `mongosh` as your go-to debugging tool to:

* Inspect collections
* Test aggregation logic
* Understand raw data before modeling it for FastAPI or analytics

Fast, stateless, and always useful in any NoSQL stack 💡
