ENV ?= DEV
PYTHON := .venv/bin/python
export PYTHONPATH := $(shell pwd)

all: ## Run full pipeline: DB load, (API/UI in dev), GitHub push in prod
ifndef CI
	@echo "🔧 Running in LOCAL (ENV=$(ENV))"
	$(MAKE) up
	$(MAKE) load
	$(MAKE) api &
	$(MAKE) ui
else
	@echo "🏗️  Running in CI/CD (ENV=$(ENV))"
	$(MAKE) load
	$(MAKE) push_to_github
endif

up: ## Start MongoDB with Docker
	docker-compose up -d

down: ## Stop MongoDB
	docker-compose down

load: ## Load latest Supabase dump from GCS to MongoDB
	ENV=$(ENV) $(PYTHON) scripts/gcs_to_mongo.py

api: ## Run FastAPI backend (DEV only)
	$(PYTHON) -m uvicorn app.api.main:app --reload

ui: ## Launch Streamlit dashboard (DEV only)
	$(PYTHON) -m streamlit run app/ui/streamlit_app.py

push_to_github: ## Push code to GitHub for Streamlit Cloud
	git remote -v | grep github || git remote add github git@github.com:your-org/your-repo.git
	git push github main
	@echo "✅ Pushed to GitHub for Streamlit Cloud"

logs: ## View MongoDB container logs
	docker logs -f nosql_mongo

mongosh: ## Open mongosh via Docker container
	docker run -it --rm --network host mongo:7 mongosh "mongodb://localhost:27017"

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'
