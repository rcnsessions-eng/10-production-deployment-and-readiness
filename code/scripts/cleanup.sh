#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
cluster_name="$(python3 -c 'import sys;sys.path.insert(0,"scripts");from deploy import guard;print(guard())')"
test "${CONFIRM_CLUSTER_DELETE:-}" = "$cluster_name"
CONFIRM_PRD06_DELETE="$cluster_name" bash ../../06-istio-workload-security/code/scripts/cleanup.sh