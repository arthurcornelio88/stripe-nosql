# ----------- Configuration -----------
ENV ?= DEV
PYTHON := .venv/bin/python
export PYTHONPATH := $(shell pwd)

ifeq ($(ENV),PROD)
	IS_PROD := true
else
	IS_PROD := false
endif

# ----------- Main Entry Points -----------

all: check_env
	@echo "🏁 Starting Make (ENV=$(ENV), CI=$(CI))"
ifeq ($(CI),)
ifeq ($(IS_PROD),true)
	@echo "🚀 Running in LOCAL PROD mode"
	$(MAKE) prod_deploy
else
	@echo "🔧 Running in LOCAL DEV mode"
	$(MAKE) up
	$(MAKE) load
	$(MAKE) api &
	$(MAKE) ui
endif
else
	@echo "🏗️  Running in CI/CD (ENV=$(ENV))"
	$(MAKE) load
	$(MAKE) push_to_github 
endif

prod_deploy: check_env ## Run only data load + GitHub push (PROD)
	$(MAKE) load
	$(MAKE) push_to_github

# ----------- Pipeline Components -----------

up: ## Start MongoDB with Docker
	docker-compose up -d

down: ## Stop MongoDB
	docker-compose down

test: ## Run tests
	$(PYTHON) -m pytest -v --tb=short tests/

load: check_env ## Load latest Supabase dump from GCS to MongoDB
	ENV=$(ENV) $(PYTHON) scripts/gcs_to_mongo.py

api: ## Run FastAPI backend (DEV only)
	$(PYTHON) -m uvicorn app.api.main:app --reload

ui: ## Launch Streamlit dashboard (DEV only)
	$(PYTHON) -m streamlit run app/ui/streamlit_app.py

push_to_github: ## Push code to GitHub for Streamlit Cloud
	@echo "📝 Staging all changes..."
	git add .
	@echo "💾 Committing changes..."
	git commit -m "Auto-deploy: Updated NoSQL components $(shell date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
	@echo "🚀 Pushing to GitHub..."
	git remote -v | grep github || git remote add github $(GITHUB_REPO)
	git push github HEAD:main
	@echo "✅ Pushed to GitHub for Streamlit Cloud"

# ----------- Utils -----------

logs: ## View MongoDB container logs
	docker logs -f nosql_mongo

mongosh: ## Open mongosh via Docker container
	docker run -it --rm --network host mongo:7 mongosh "mongodb://localhost:27017"

check_env:
ifndef ENV
	$(error ❌ ENV must be defined (e.g. ENV=DEV or ENV=PROD))
endif

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'
