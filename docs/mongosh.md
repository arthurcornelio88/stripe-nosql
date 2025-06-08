# 🧪 MongoDB Shell (mongosh) — Local & Prod Guide

This guide helps you inspect and query your MongoDB database — whether you're working locally or in production (MongoDB Atlas via FastAPI or Streamlit).

---

## 📍 Overview

| Context | Mongo URI                         | Usage                   |
| ------- | --------------------------------- | ----------------------- |
| Local   | `mongodb://localhost:27017`       | Docker/Dev/CI           |
| Prod    | `mongodb+srv://...` (Mongo Atlas) | Deployed API, Streamlit |

---

## 💻 1. Local MongoDB with Docker (mongosh)

If `mongosh` isn't installed or not supported (e.g., Ubuntu 24.04), use:

```bash
docker run -it --rm --network host mongo:7 mongosh "mongodb://localhost:27017"
```

Alias for convenience:

```bash
echo "alias mongo-local='docker run -it --rm --network host mongo:7 mongosh \"mongodb://localhost:27017\"'" >> ~/.zshrc
source ~/.zshrc
```

Then simply:

```bash
mongo-local
```

---

## ☁️ 2. Production MongoDB with Atlas

Your production deployments (Render, Streamlit Cloud) must use a remote MongoDB instance — typically **MongoDB Atlas**.

### ✍️ How to get your Mongo URI (`MONGO_URI`)

1. Go to [https://cloud.mongodb.com](https://cloud.mongodb.com)
2. Create a **free cluster**
3. Under “Database Access” → Add a database user (username/password)
4. Under “Network Access” → Allow IPs (`0.0.0.0/0` or restrict to Render)
5. Click “Connect” → “Connect your application”
6. Copy the URI:

```
mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/supabase_snapshot?retryWrites=true&w=majority
```

Use this as the value for `MONGO_URI` in:

* Render env vars
* Streamlit `secrets.toml`
* Local `.env.prod` if needed

---

## ⚙️ 3. Connecting to MongoDB (Local or Atlas)

### Local:

```bash
mongosh "mongodb://localhost:27017"
```

### Atlas:

```bash
mongosh "mongodb+srv://<user>:<pass>@cluster.mongodb.net/supabase_snapshot"
```

Then:

```js
use supabase_snapshot
```

---

## 🔍 4. Explore Collections

```js
show collections
db.customers.findOne()
db.subscriptions.countDocuments()
```

---

## 🧠 5. Example Queries

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

## 🐍 6. Python Alternative (`mongo_queries.py`)

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")  # or MONGO_URI from Atlas
db = client["supabase_snapshot"]

for c in db.charges.find({"amount": {"$gt": 1000}}):
    print(c["id"], c["amount"])
```

---

## 🧼 7. Wipe or reload a collection

```js
db.customers.drop()
mongoimport --jsonArray ...
```

---

## ✅ Conclusion

Use `mongosh` locally or connect to Atlas in prod:

* ⚙️ Debug and inspect real data
* 🔁 Query before embedding into API logic
* 🔍 Validate fraud logic, aggregations, filters

Stateless, powerful, and works across local and cloud.