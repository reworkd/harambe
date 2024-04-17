#!/bin/sh
cd "$(dirname "$0")" || exit 1

echo "Formatting code 🧹"
poetry run ruff format

echo "Checking code 🧹"
poetry run ruff check
