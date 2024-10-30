#!/usr/bin/make -f

# Makefile for harambe

ifeq ($(OS),Windows_NT)
    CWD ?= "$(shell echo %CD%)"
    DOCKER ?= docker
else
    CWD ?= "$(shell pwd)"
    DOCKER ?= $(if $(shell docker -v 2>/dev/null),docker,podman)
endif
DOCKER_IMAGE_TAG ?= reworkd/harambe

.DEFAULT_GOAL := help

include Prebuild.mk

help: ## Show this helpful message
	@for ML in $(MAKEFILE_LIST); do \
		grep -E '^[a-zA-Z_-]+:.*?## .*$$' $$ML | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'; \
	done
.PHONY: help

format: ## Format code using Docker
	@$(DOCKER) run -it --rm -v "`pwd`":/src/$(DOCKER_IMAGE_TAG) -e TARGET=$(target) $(DOCKER_IMAGE_TAG) make FORMAT
.PHONY: format

FORMAT: ## Format code
	@echo "Formatting code 🧹"
	@uv run ruff format
.PHONY: FORMAT

format_check: ## Check code formatting using Docker
	@$(DOCKER) run -it --rm -v "`pwd`":/src/$(DOCKER_IMAGE_TAG) -e TARGET=$(target) $(DOCKER_IMAGE_TAG) make LINT
.PHONY: format_check

FORMAT_CHECK: ## Check code formatting
	@echo "Checking code 🧹"
	@uv run ruff format --diff
.PHONY: FORMAT_CHECK

lint: ## Lint code using Docker
	@$(DOCKER) run -it --rm -v "`pwd`":/src/$(DOCKER_IMAGE_TAG) -e TARGET=$(target) $(DOCKER_IMAGE_TAG) make LINT
.PHONY: lint

LINT: ## Lint code
	@uv run ruff check --fix
.PHONY: LINT

lint_check: ## Check code quality using Docker
	@$(DOCKER) run -it --rm -v "`pwd`":/src/$(DOCKER_IMAGE_TAG) -e TARGET=$(target) $(DOCKER_IMAGE_TAG) make LINT_CHECK
.PHONY: lint_check

LINT_CHECK: ## Check code quality
	@uv run ruff check
.PHONY: LINT_CHECK

test: $(HARAMBE) $(OUTPUT_DIR) $(CONFIG_FILE) ## Run tests using Docker
	@$(DOCKER) build -t $(DOCKER_IMAGE_TAG) .
	@$(DOCKER) run -it --rm -v "`pwd`":/src/$(DOCKER_IMAGE_TAG) -e TARGET=$(target) $(DOCKER_IMAGE_TAG)
.PHONY: test

TEST: ## Run tests
	@uv run pytest . -v
.PHONY: TEST

shell: ## Enter Docker container's shell
	@$(DOCKER) run -it --rm -v "`pwd`":/src/$(DOCKER_IMAGE_TAG) $(DOCKER_IMAGE_TAG) bash || true
.PHONY: shell
