#!/usr/bin/make -f

# Makefile for harambe

.DEFAULT_GOAL := help

help: ## Show this helpful message
	@for ML in $(MAKEFILE_LIST); do \
		grep -E '^[a-zA-Z_-]+:.*?## .*$$' $$ML | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'; \
	done
.PHONY: help

format: ## Format code
	@echo "Formatting code 🧹"
	@poetry run ruff format
.PHONY: format

format_check: ## Check code formatting
	@echo "Checking code 🧹"
	@poetry run ruff format --diff
.PHONY: format_check

lint: ## Lint code
	@poetry run ruff check --fix
.PHONY: lint

lint_check: ## Check code quality
	@poetry run ruff check
.PHONY: lint_check

resolve_deps: ## Install required dependencies
	@poetry install
.PHONY: resolve_deps

test: ## Run tests
	@poetry run pytest . -v
.PHONY: test
