#!/usr/bin/make -f


RESOLVE_DEPS: ## Install required dependencies
	@uv run playwright install-deps chromium && uv run playwright install chromium
	@uv run playwright install-deps firefox && uv run playwright install firefox
	@uv run playwright install-deps webkit && uv run playwright install webkit
.PHONY: RESOLVE_DEPS
