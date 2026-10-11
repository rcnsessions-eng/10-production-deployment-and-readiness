#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash ../../09-supply-chain-and-ci/code/scripts/build_dependencies.sh
if [[ ! -x ../../09-supply-chain-and-ci/code/.tools/cosign ]]; then
  bash ../../09-supply-chain-and-ci/code/scripts/install_tools.sh
fi
bash scripts/check.sh
if [[ ! -x ../../06-istio-workload-security/code/.tools/kind ]]; then
  bash ../../06-istio-workload-security/code/scripts/install_tools.sh
fi
bash ../../06-istio-workload-security/code/scripts/create_cluster.sh
bash ../../09-supply-chain-and-ci/code/scripts/run.sh
python3 scripts/deploy.py
python3 scripts/verify.py