#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash scripts/startup.sh
python3 scripts/fault_check.py
python3 scripts/verify.py