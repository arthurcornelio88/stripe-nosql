# 📦 NoSQL - Supabase Snapshot + MongoDB + FastAPI + Streamlit

This repository bridges OLTP and OLAP workflows using **MongoDB** as a NoSQL intermediary, offering a clean local + cloud interface to load and explore Supabase-style JSON exports.

It supports full-stack deployment across **DEV** (local) and **PROD** (Render + Streamlit Cloud) environments using a `Makefile`-based pipeline and environment-driven logic.

---

## 🚀 Getting Started

### 🌀 Clone the repository

```bash
git clone https://gitlab.com/stripe_b2/nosql.git
cd nosql
````

### 🐍 Set up your virtual environment

We recommend [`uv`](https://github.com/astral-sh/uv) for fast dependency installs:

```bash
uv venv
source .venv/bin/activate
uv sync
```

---

## 🛠️ Project Pipeline via Makefile

Run `make help` to list all available targets.

### 🔧 DEV Mode (local development)

```bash
make all ENV=DEV
```

This starts:

* MongoDB via Docker
* A data load from GCS (or local)
* FastAPI backend via Uvicorn
* Streamlit dashboard in a new tab

### 🚀 PROD Mode (CI/CD & cloud deployments)

```bash
make prod_deploy ENV=PROD
```

This runs:

* Supabase → MongoDB data ingestion
* Git push to GitHub (for Streamlit Cloud triggers)

---

## 🧠 MongoDB Shell (Local & Atlas)

Explore your database manually:

```bash
make mongosh
```

To learn manual connection URIs, example aggregation queries, and how to debug your collections:

👉 Read [📄 MongoDB Shell & Query Cheatsheet](docs/mongosh.md)

---

## 🔌 Backend API — FastAPI

The backend is environment-aware (`ENV=DEV|PROD`) and connects to either local Mongo or Atlas. It exposes:

* `/customers`, `/customers/{id}`
* `/subscriptions/active`
* `/charges/fraud`
* `/payment_intents/3ds`

Run locally:

```bash
make api
```

---

## 📊 Frontend UI — Streamlit

The Streamlit app reads from your backend API and lets you:

* Inspect customers, subscriptions, payment intents, and fraud patterns
* Query by endpoint
* Visualize 3DS usage and suspicious charges

Run locally:

```bash
make ui
```

---

## 📜 Data Loader — `gcs_to_mongo.py`

The primary data ingestion script:

* Downloads the latest Supabase-style `db_dump_prod_*.json` from GCS
* Parses JSON by collection
* Writes to MongoDB

Run standalone:

```bash
ENV=PROD python scripts/gcs_to_mongo.py
```

---

## ✅ Command Recap

| Task                 | Tool      | Command                     |
| -------------------- | --------- | --------------------------- |
| Start MongoDB        | Docker    | `make up`                   |
| Load JSON to MongoDB | Python    | `make load`                 |
| Launch API (DEV)     | FastAPI   | `make api`                  |
| Launch UI (DEV)      | Streamlit | `make ui`                   |
| Query DB manually    | mongosh   | `make mongosh`              |
| Full local pipeline  | Makefile  | `make all ENV=DEV`          |
| Deploy to cloud      | Makefile  | `make prod_deploy ENV=PROD` |
| Run tests            | pytest    | `make test`                 |

---

## 🔐 `.env` Configuration & GitLab → GitHub SSH Deploy

### 🧪 Local `.env` setup

At the root of the repo, create a file named `.env` with:

```env
ENV=DEV
MONGO_URI=mongodb://localhost:27017
GCP_CREDS_FILE=your-raw-json-credentials-content-here
```

If you're using **MongoDB Atlas** in production:

```env
ENV=PROD
MONGO_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/supabase_snapshot
```

> 🧬 These variables are loaded automatically by `python-dotenv` and are used across scripts and Streamlit/FastAPI.

---

### 🚀 GitLab CI/CD SSH access to GitHub (for push-to-deploy)

To enable **CI/CD pipelines on GitLab to push to GitHub** (for example to trigger Streamlit Cloud redeploys), follow these steps:

#### 1. Generate a deploy key (RSA recommended)

Run locally:

```bash
ssh-keygen -t rsa -b 4096 -C "gitlab-ci@nosql" -f deploy_key_gitlab_to_github_rsa
```

This creates two files:

* `deploy_key_gitlab_to_github_rsa` (private key)
* `deploy_key_gitlab_to_github_rsa.pub` (public key)

#### 2. Add the **public key** to GitHub

* Go to **GitHub → Your repo → Settings → Deploy Keys**
* Click **"Add deploy key"**
* Title: `GitLab CI deploy`
* Paste the **contents of `deploy_key_gitlab_to_github_rsa.pub`**
* ✅ Enable **“Allow write access”**

#### 3. Add the **private key** to GitLab CI/CD

* Go to **GitLab → Settings → CI/CD → Variables**
* Add a new variable:

| Key              | Value                                         | Type        |
| ---------------- | --------------------------------------------- | ----------- |
| `GITHUB_SSH_KEY` | Contents of `deploy_key_gitlab_to_github_rsa` | 📄 **File** |

> ❗ Must be a **file-type** variable for it to work with `ssh-agent`.

#### 4. SSH activation in `.gitlab-ci.yml`

Your pipeline should include:

```yaml
before_script:
  - eval "$(ssh-agent -s)"
  - mkdir -p ~/.ssh
  - echo "$GITHUB_SSH_KEY" > ~/.ssh/id_rsa
  - chmod 600 ~/.ssh/id_rsa
  - ssh-keyscan github.com >> ~/.ssh/known_hosts
```

#### 5. Git push inside your Makefile

In your `Makefile`, ensure the push command uses:

```makefile
git push github HEAD:main
```

> 🛡️ SSH setup is only required if you're triggering GitHub deploys from GitLab CI via `make all ENV=PROD`.

---

## 📚 Documentation

* [🥪 MongoDB Shell & Query Cheatsheet](docs/mongosh_guide.md) — manual queries & shell usage
* [💃 Integration Guide (Mongo + FastAPI + Streamlit)](docs/streamlit.md) — fullstack architecture, local & cloud setup

---

## 🌐 Architecture

```
Supabase JSON (GCS/local)
         ↓
      MongoDB
         ↓
    FastAPI Backend
         ↓
   Streamlit Frontend
```

---

## ☁️ Deployment Matrix

| Mode | MongoDB          | API     | UI                  |
| ---- | ---------------- | ------- | ------------------- |
| DEV  | Local via Docker | Uvicorn | Streamlit localhost |
| PROD | MongoDB Atlas    | Render  | Streamlit Cloud     |

---

Want to contribute or adapt this setup to your own OLAP/OLTP bridge? PRs welcome ✨
