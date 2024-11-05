cd "$(dirname "$0")" || exit 1

cd core || exit 1
uv run ruff format .
uv run pytest . || exit 1
cd - || exit 1

cd sdk || exit 1
uv run ruff format .
uv run pytest . || exit 1
cd - || exit 1