#!/usr/bin/make -f


RESOLVE_DEPS: ## Install required dependencies
	@pip install poetry==1.6.1
	@poetry config virtualenvs.create false
	@poetry install --no-root
	@playwright install-deps chromium && playwright install chromium
.PHONY: RESOLVE_DEPS
