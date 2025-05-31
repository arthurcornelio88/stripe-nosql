# 📦 Supabase Snapshot — FastAPI + MongoDB + Streamlit

This repository connects OLTP and OLAP flows with a NoSQL (MongoDB) intermediary, offering a local and visual interface for Supabase-style JSON data dumps.

---

## 🚀 Getting Started

### 🔁 Clone the repo
```bash
git clone https://gitlab.com/stripe_b2/nosql.git
cd nosql
```

### 🐍 Create and activate virtual environment
We use [`uv`](https://github.com/astral-sh/uv) for speed:

```bash
uv venv
source .venv/bin/activate
uv sync
```

---

## 🛠️ Run Everything

### Use the Makefile:
```bash
make help
```
Key commands:
- `make up` → Launch MongoDB container
- `make load` → Load Supabase JSON dump into MongoDB
- `make api` → Start FastAPI backend
- `make ui` → Launch Streamlit dashboard
- `make mongosh` → Open the Mongo shell

You can also run everything in one go:
```bash
make all
```

---

## 📜 Main Script — `gcs_to_mongo.py`

This script:
- Loads latest `db_dump_prod_*.json` from GCS
- Parses and inserts data into MongoDB (by entity/collection)

Launch manually:
```bash
ENV=PROD python scripts/gcs_to_mongo.py
```

---

## 🧪 Testing

```bash
make test
```
- Uses `mongomock` for in-memory testing
- Validates structure and ingestion logic

---

## 🔌 Backend API (FastAPI)

Main file: `app/api/main.py`
- `/customers`, `/customers/{id}`
- `/subscriptions/active`
- `/payment_intents/3ds`
- `/charges/fraud`

Launch locally:
```bash
make api
```

More details in [📄 MongoDB + FastAPI + Streamlit](docs/mongodb_fastapi_streamlit.md)

---

## 📊 UI (Streamlit)

Main file: `app/ui/streamlit_app.py`
- Query backend API
- Explore customer info, subscriptions, charges visually

Launch with:
```bash
make ui
```

---

## 🧠 Mongo Shell (`mongosh`)

Explore your MongoDB data manually:
```bash
make mongosh
```
This launches `mongosh` via Docker, connected to your local DB.

For advanced queries, aggregation, and inspection examples, see:
[📄 Mongosh Guide](docs/mongosh_guide.md)

---

## ✅ Recap

| Task            | Tool     | Command         |
|------------------|----------|------------------|
| Load JSON data   | Python   | `make load`      |
| Backend API      | FastAPI  | `make api`       |
| Frontend UI      | Streamlit| `make ui`        |
| Query DB Shell   | mongosh  | `make mongosh`   |
| Run all          | Make     | `make all`       |
| Tests            | Pytest   | `make test`      |
