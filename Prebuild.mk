#!/usr/bin/make -f

RESOLVE_DEPS: ## Install required dependencies
	@pip3 install poetry
	@poetry install --no-root
.PHONY: RESOLVE_DEPS
