# 🗃️ MongoDB + FastAPI + Streamlit Integration Guide

This documentation explains how to integrate **MongoDB** with **FastAPI** as a backend API layer and **Streamlit** as the frontend interface for querying and visualizing data. It is based on a real-world implementation handling Supabase exports.

---

## 🧩 Architecture Overview

```mermaid
graph TD
    GCS[Supabase JSON dump on GCS] --> MongoDB
    MongoDB --> FastAPI
    FastAPI --> Streamlit UI
```

* **MongoDB** stores JSON-formatted structured/semi-structured data.
* **FastAPI** serves REST endpoints to query and aggregate data from MongoDB.
* **Streamlit** provides a developer-friendly UI to explore that data.

---

## ⚙️ 1. MongoDB Setup

MongoDB is launched via Docker Compose:

```yaml
services:
  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
volumes:
  mongo_data:
```

Use `mongoimport` or a Python script to load JSON dumps from Supabase into collections such as `customers`, `charges`, `subscriptions`...

---

## 🚀 2. FastAPI Backend

### 📁 Example directory: `app/api/main.py`

```python
from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()
client = MongoClient("mongodb://localhost:27017")
db = client["supabase_snapshot"]

def convert_objectid(doc):
    if doc: doc["_id"] = str(doc["_id"])
    return doc

@app.get("/customers")
def list_customers():
    return list(db.customers.find({}, {"id": 1, "name": 1, "email": 1, "_id": 0}))

@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    return convert_objectid(db.customers.find_one({"id": customer_id}))
```

Additional endpoints serve:

* `/subscriptions/active`
* `/charges/fraud`
* `/payment_intents/3ds`

---

## 🖥️ 3. Streamlit Frontend

### 📁 Example file: `app/ui/streamlit_app.py`

```python
import streamlit as st
import requests

API_URL = "http://localhost:8000"

customers = requests.get(f"{API_URL}/customers").json()
selected = st.selectbox("Choose customer", [f"{c['name']} ({c['email']})" for c in customers])
```

When a customer is selected:

```python
customer_id = [c['id'] for c in customers if f"{c['name']} ({c['email']})" == selected][0]
data = requests.get(f"{API_URL}/customers/{customer_id}").json()
st.write(data)
```

Streamlit provides interactive views:

* Active subscriptions
* 3DS-secured payments
* Potentially fraudulent charges (aggregated in Mongo)

---

## 🧪 Benefits

| Feature   | Benefit                                                           |
| --------- | ----------------------------------------------------------------- |
| MongoDB   | Flexible JSON support, easy import from Supabase dumps            |
| FastAPI   | High-performance, async-compatible, easy to expose REST endpoints |
| Streamlit | Lightweight frontend for data analyst/dev teams                   |

---

## 🧱 Recommended Project Structure

```
project/
├── app/
│   ├── api/
│   │   └── main.py         # FastAPI app
│   └── ui/
│       └── streamlit_app.py # Streamlit dashboard
├── docker-compose.yml      # MongoDB container
├── Makefile                # Dev shortcuts (run, test, load)
└── requirements.txt        # Python dependencies
```

---

## 📎 Requirements

```txt
fastapi
uvicorn
pymongo
streamlit
requests
python-dotenv
```

---

## 🌐 Deployment (optional)

* Run FastAPI using:

  ```bash
  uvicorn app.api.main:app --reload
  ```
* Run Streamlit locally:

  ```bash
  streamlit run app/ui/streamlit_app.py
  ```

To deploy Streamlit on Streamlit Cloud:

* Use `requirements.txt`
* Add `secrets.toml` if needed for MongoDB Atlas

---

## ✅ Conclusion

This stack lets you:

* Load and store Supabase-style JSON dumps into MongoDB
* Query that data efficiently via FastAPI
* Explore, visualize, and validate your pipeline through a lightweight Streamlit UI

A powerful, flexible foundation for any modern data app.
