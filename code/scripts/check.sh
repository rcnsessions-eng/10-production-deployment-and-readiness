#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash -n scripts/*.sh
docker compose config --quiet
docker compose build checks
docker compose run --rm checks
docker compose run --rm -v "$PWD:/readiness:ro" checks sh -c 'ruff check --config /readiness/pyproject.toml /readiness/scripts /readiness/tests && ruff format --check --config /readiness/pyproject.toml /readiness/scripts /readiness/tests && mypy --config-file /readiness/pyproject.toml /readiness/scripts/*.py'