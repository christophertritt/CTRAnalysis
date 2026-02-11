# Bellevue CTR Dashboard - Makefile
# Quick commands for common development tasks

.PHONY: help install run clean test lint format

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	python -m pip install --upgrade pip
	pip install -r requirements.txt

run:  ## Run the Streamlit dashboard
	streamlit run bellevue_ctr_dashboard_official_v3.py

clean:  ## Clean up Python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

lint:  ## Run linting checks
	@which flake8 > /dev/null 2>&1 && flake8 bellevue_ctr_dashboard_official_v3.py || echo "flake8 not installed. Run: pip install flake8"

format:  ## Format code with black
	@which black > /dev/null 2>&1 && black bellevue_ctr_dashboard_official_v3.py || echo "black not installed. Run: pip install black"

test:  ## Run tests (if any)
	@echo "No tests configured yet"

dev:  ## Setup development environment
	python -m venv .venv
	@echo "Virtual environment created. Activate with: source .venv/bin/activate"
