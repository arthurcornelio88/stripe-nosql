# 🥪 MongoDB Shell & Query Cheatsheet (Local & Prod)

This quick-reference guide helps you inspect and query your MongoDB database from the command line or Python, whether you're working locally or in production.

---

## 📍 Overview

| Context | Mongo URI                         | Usage              |
| ------- | --------------------------------- | ------------------ |
| Local   | `mongodb://localhost:27017`       | Docker/Dev/CI      |
| Prod    | `mongodb+srv://...` (Mongo Atlas) | FastAPI, Streamlit |

> ✉️ For full setup instructions and deployment logic, see the [Integration Guide](./mongodb_fastapi_streamlit.md).

---

## 💻 1. Local MongoDB with Docker + mongosh

If `mongosh` isn't installed:

```bash
docker run -it --rm --network host mongo:7 mongosh "mongodb://localhost:27017"
```

Optional alias:

```bash
echo "alias mongo-local='docker run -it --rm --network host mongo:7 mongosh \"mongodb://localhost:27017\"'" >> ~/.zshrc
source ~/.zshrc
```

Then run:

```bash
mongo-local
```

---

## ☁️ 2. Production Atlas Connection

To connect from your terminal:

```bash
mongosh "mongodb+srv://<user>:<pass>@cluster.mongodb.net/supabase_snapshot"
```

Then switch DB:

```js
use supabase_snapshot
```

---

## 🔍 3. Explore Collections

```js
show collections
db.customers.findOne()
db.subscriptions.countDocuments()
```

---

## 🧠 4. Example Queries

### 💰 Charges > 1000€

```js
db.charges.find({ amount: { $gt: 1000 } })
```

### 🧰 Group charges by customer

```js
db.charges.aggregate([
  { $group: { _id: "$customer_id", count: { $sum: 1 }, total: { $sum: "$amount" } } },
  { $sort: { total: -1 } }
])
```

### 🔐 3D Secure intents

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

## 🐍 5. Python CLI Alternative

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")  # or MONGO_URI from Atlas
db = client["supabase_snapshot"]

for c in db.charges.find({"amount": {"$gt": 1000}}):
    print(c["id"], c["amount"])
```

---

## 🧼 6. Reset or Reload Collections

```js
db.customers.drop()
mongoimport --jsonArray --db supabase_snapshot --collection customers --file ./dump.json
```

---

## ✅ Conclusion

Use this cheat sheet to:

* ⚙️ Debug and inspect real MongoDB data
* 🔄 Run aggregation queries before embedding them into your app
* 🔍 Validate fraud filters, 3DS logic, and subscription statuses

For deployment, API design, and Streamlit integration, refer to the [full guide](/docs/streamlit.md).
