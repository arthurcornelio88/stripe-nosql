# 💃 MongoDB + FastAPI + Streamlit Integration Guide (DEV & PROD Modes)

This guide explains how to integrate **MongoDB**, **FastAPI**, and **Streamlit**, supporting both **local development (DEV)** and **production deployment (PROD)** with MongoDB Atlas and Render.

---

## 🥩 Architecture Overview

This stack is designed to support loading and exploring data exported from Supabase:

* **MongoDB** stores Supabase-style JSON data.
* **FastAPI** serves as a backend API to expose collections and query logic.
* **Streamlit** acts as a frontend UI for browsing and visualizing the data.

Data flows as follows:

```
Supabase JSON exports (e.g., in GCS or local dump)
            ↓
         MongoDB
            ↓
        FastAPI (REST API)
            ↓
     Streamlit app (frontend)
```

DEV mode runs everything locally (MongoDB via Docker, FastAPI via Uvicorn, Streamlit via `streamlit run`).
PROD mode deploys FastAPI to Render and uses MongoDB Atlas with secure credentials.

---

## ⚙️ 1. MongoDB Setup

### 🔧 Local (DEV mode)

* Use Docker Compose to start MongoDB locally
* Load Supabase-style JSON into collections using `mongoimport` or a script

### ☁️ Production (PROD mode)

* Create a cluster on MongoDB Atlas
* Create a database user
* Allow Render static outbound IPs in **Network Access**
* Copy the connection URI from "Connect your application"

---

## 🚀 2. FastAPI Backend (DEV/PROD aware)

The FastAPI backend reads from environment variables:

* In **DEV**, it connects to `mongodb://localhost:27017`
* In **PROD**, it reads the Atlas connection string from `MONGO_URI`

It exposes endpoints like:

* `/customers` → List all customers
* `/customers/{customer_id}` → Get one customer
* `/subscriptions/active`, `/charges/fraud`, `/payment_intents/3ds`

Environment variable `ENV` controls the mode (`DEV`, `TEST`, or `PROD`).

---

## 🖥️ 3. Streamlit Frontend (DEV/PROD aware)

Streamlit dynamically adjusts the backend API URL based on `ENV`:

* In **DEV**, it queries `http://localhost:8000`
* In **PROD**, it uses the deployed FastAPI URL via `API_URL`

The frontend fetches customer data from the API and renders interactive dropdowns and tables. It can display:

* Active subscriptions
* 3DS payment intents
* Suspicious or duplicate charges

---

## 📎 4. Environment Configuration

`.env` example for production:

```env
ENV=PROD
MONGO_URI="mongodb+srv://<user>:<password>@your-cluster.mongodb.net/supabase_snapshot?retryWrites=true&w=majority"
API_URL="https://your-api.onrender.com"
```

These should be loaded automatically via `python-dotenv` in local dev, or configured manually in Render and Streamlit Cloud.

---

## ☁️ 5. Deployment

### 🚗 FastAPI on Render

1. Push your FastAPI code to GitLab
2. Create a Web Service on Render:

   * **Build command**: `pip install -r requirements.txt`
   * **Start command**: `uvicorn app.api.main:app --host 0.0.0.0 --port 10000`
   * **Environment variables**:

     * `ENV=PROD`
     * `MONGO_URI=...`
3. Copy Render's **outbound IPs** and add them to MongoDB Atlas Network Access

### 🚀 Streamlit on Streamlit Cloud

1. Push your Streamlit app to GitHub
2. Create an app on [Streamlit Cloud](https://streamlit.io/cloud)
3. Set the following in Streamlit secrets or environment:

   * `ENV=PROD`
   * `API_URL=https://your-api.onrender.com`
4. Ensure `requirements.txt` includes:

   * `streamlit`, `requests`, `python-dotenv`

---

## ✅ Conclusion

| Mode | Mongo                 | API        | Frontend              |
| ---- | --------------------- | ---------- | --------------------- |
| DEV  | Local (Docker)        | Uvicorn    | Streamlit (localhost) |
| PROD | MongoDB Atlas (cloud) | Render API | Streamlit Cloud       |

This full-stack setup is flexible, portable, and works across dev & cloud environments.
