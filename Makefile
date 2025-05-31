# Makefile — Supabase Snapshot Project

ENV ?= DEV

.PHONY: help up down test load logs api ui mongosh all

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start MongoDB with Docker
	docker-compose up -d

down: ## Stop MongoDB
	docker-compose down

test: ## Run Pytest with mongomock
	pytest -v tests/test_gcs_to_mongo.py

load: ## Load latest Supabase dump from GCS to MongoDB
	ENV=$(ENV) python scripts/gcs_to_mongo.py

logs: ## View MongoDB container logs
	docker logs -f nosql_mongo

api: ## Run FastAPI backend
	uvicorn app.api.main:app --reload

ui: ## Launch Streamlit dashboard
	streamlit run app/ui/streamlit_app.py

mongosh: ## Open mongosh via Docker container
	docker run -it --rm --network host mongo:7 mongosh "mongodb://localhost:27017"

all: ## Run up, load, api and ui in one command
	$(MAKE) up
	$(MAKE) load
	$(MAKE) api &
	$(MAKE) ui
