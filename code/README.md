# Verified Non-Production Deployment

PRD 10 capstone only. Compose project `zero-trust-deployment-readiness` supplies offline operational checks; Kubernetes runs the integrated API, official stdio MCP adapter, OPA, IdP fixture and private collector. Earlier business code is inherited, never rewritten here.

## Run

From the sequence root:

```bash
bash 10-production-deployment-and-readiness/code/scripts/run.sh
```

Supported test environment: macOS ARM64, Docker Engine 29.1.3/Compose 2.40.3, host Python 3.12+, kubectl, kind 0.33.0/Kubernetes 1.35.8 and Istio 1.31.1. Release runtime: Python 3.12.15/Alpine 3.24.2 with exact constraints. OPA 1.21.1, Keycloak 26.0.7 and collector 0.162.0 images are digest-pinned. Linux AMD64 tool installation is supported; the full capstone was tested on macOS ARM64.

Startup builds prior dependencies, retains or initializes ignored synthetic secrets, tests tooling, creates/reuses only the owned disposable cluster, runs scans/SBOM/signing/verification, deploys the verified release and runs real smoke. The gate makes OPA unavailable, proves writes return 503/no receipt, rolls back the smoke-verified release configuration and reruns security/incident reconstruction.

Dedicated kubeconfig: PRD 06's ignored artifacts directory. New cluster name `zero-trust-workload-security`; historical `zero-trust-prd06` is explicitly supported without recreation. User context `lcp-development-1.33` stays untouched. No unrelated cleanup/pruning was performed.

## Operations

From this code directory:

```bash
bash scripts/check.sh
python3 scripts/deploy.py
python3 scripts/verify.py
python3 scripts/fault_check.py
python3 scripts/verify.py
python3 scripts/rollback.py
```

Checks cover allowed progress, foreign denial, spoofed/wrong/missing tokens, four actual MCP tools, duplicate writes, wrong-account RBAC denial, plaintext rejection, direct OPA denial, unauthorized collector exporter denial, safe audit data and one MCP/API/service/policy/repository trace. MCP starts as a stdio subprocess inside its dedicated pod for each workflow, not an unrestricted public endpoint.

Cleanup deletes the whole owned disposable cluster, including prior mesh fixtures. It was not executed and requires confirmation matching the actual name:

```bash
CONFIRM_CLUSTER_DELETE=zero-trust-prd06 bash scripts/cleanup.sh
```

Use `zero-trust-workload-security` for a new descriptive-name cluster. Retain evidence before deliberate cleanup; this does not authorize deleting any other cluster.

## Evidence and Limits

Seven tests cover guards, verified rollback, trace grouping and clean MCP manifest replacement; Ruff/format and strict types cover five scripts. Admission/Istio validation, verified release rollout, real identity/MCP/mesh/telemetry and incident reconstruction passed. Policy fault returned 503/no receipt; rollback restored 200/receipt twice. This tests configuration rollback on the same verified image, not a malicious binary. The first single-command replay exposed stale pod readiness after image mutation; clean standalone-pod replacement fixed it and live smoke passed. Final single-command results are recorded in shared implementation status.

Ignored `artifacts/known-good.json`, `incident-reconstruction.json` and `rollback-evidence.json` record release/revision, sanitized trace/layers and fault/recovery. Signed archive/SBOM/scans/provenance are in PRD 09 artifacts. Hosted CI/keyless signing, a second fresh capstone cluster and cleanup were not executed. Original PRD 06 cluster bootstrap was executed earlier.

This is a verified non-production reference, not production-ready infrastructure. See [deployment guide](docs/deployment-guide.md), [operations runbook](docs/operations-runbook.md), [threat model](docs/threat-model.md) and [release checklist](docs/release-checklist.md).