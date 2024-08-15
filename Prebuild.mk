#!/usr/bin/make -f


RESOLVE_DEPS: ## Install required dependencies
	@pip install poetry==1.6.1
	@poetry config virtualenvs.create false
	@poetry install --no-root
	@poetry run playwright install-deps chromium && poetry run playwright install chromium
	@poetry run playwright install-deps firefox && poetry run playwright install firefox
	@poetry run playwright install-deps webkit && poetry run playwright install webkit
.PHONY: RESOLVE_DEPS
