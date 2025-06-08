# 🗃️ MongoDB + FastAPI + Streamlit Integration Guide (DEV & PROD Modes)

This guide explains how to integrate **MongoDB**, **FastAPI**, and **Streamlit**, supporting both **local development (DEV)** and **production deployment (PROD)** with MongoDB Atlas and Render.

---

## 🧩 Architecture Overview

```mermaid
graph TD
    GCS[Supabase JSON dump on GCS] --> MongoDB
    MongoDB --> FastAPI
    FastAPI --> Streamlit UI
```

* MongoDB stores Supabase-style JSON exports.
* FastAPI exposes REST endpoints over HTTP.
* Streamlit interacts with those endpoints to explore the data.

---

## ⚙️ 1. MongoDB Setup

### 🔧 Local (DEV mode)

Use Docker Compose:

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

Import your Supabase exports into collections (`customers`, `charges`, `subscriptions`, etc.).

### ☁️ Production (PROD mode)

Use MongoDB Atlas:

1. Create a free cluster on [cloud.mongodb.com](https://cloud.mongodb.com)
2. Add a database user (username/password)
3. Under **Network Access**, allow static IPs from Render
4. Copy your connection URI from "Connect your application"

---

## 🚀 2. FastAPI Backend (DEV/PROD aware)

### 📁 `app/api/main.py`

```python
from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId
import os, certifi

app = FastAPI()
ENV = os.getenv("ENV", "DEV").upper()

if ENV == "DEV":
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
elif ENV == "PROD":
    MONGO_URI = os.getenv("MONGO_URI")
else:
    raise ValueError("Invalid ENV variable. Must be DEV or PROD")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
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

---

## 🖥️ 3. Streamlit Frontend (DEV/PROD aware)

### 📁 `app/ui/streamlit_app.py`

```python
import streamlit as st
import requests
import os

ENV = os.getenv("ENV", "DEV").upper()
if ENV == "DEV":
    API_URL = "http://localhost:8000"
elif ENV in ["TEST", "PROD"]:
    API_URL = os.getenv("API_URL")
else:
    raise ValueError("Invalid ENV variable. Must be DEV, TEST, or PROD")

customers = requests.get(f"{API_URL}/customers").json()
selected = st.selectbox("Choose customer", [f"{c['name']} ({c['email']})" for c in customers])

customer_id = [c['id'] for c in customers if f"{c['name']} ({c['email']})" == selected][0]
data = requests.get(f"{API_URL}/customers/{customer_id}").json()
st.write(data)
```

---

## 📎 Environment Configuration

### `.env`

```env
ENV=PROD
MONGO_URI="mongodb+srv://<user>:<password>@your-cluster.mongodb.net/supabase_snapshot?retryWrites=true&w=majority"
API_URL="https://your-api.onrender.com"
```

Load it using `python-dotenv` or Render's environment tab.

---

## ☁️ 4. Render Deployment (for PROD)

1. Push your FastAPI repo to GitLab
2. Create a new **Web Service** on [Render.com](https://render.com)

   * Build Command: `pip install -r requirements.txt`
   * Start Command: `uvicorn app.api.main:app --host 0.0.0.0 --port 10000`
3. Add environment variables in Render:

   * `ENV=PROD`
   * `MONGO_URI=...`
4. Get Render's **outbound IPs** (e.g. `18.156.158.53`) and whitelist them in MongoDB Atlas

---

## ✅ Conclusion

| Mode | Mongo                 | API        | Frontend              |
| ---- | --------------------- | ---------- | --------------------- |
| DEV  | Local (Docker)        | Uvicorn    | Streamlit (localhost) |
| PROD | MongoDB Atlas (cloud) | Render API | Streamlit Cloud       |

This setup gives you a secure, modular pipeline from raw Supabase exports to a hosted Streamlit UI that works in both development and production contexts.
