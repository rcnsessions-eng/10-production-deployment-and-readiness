# Operations Runbook

Run `python3 scripts/verify.py` after deployment/recovery. It checks workload identity, transport restrictions, real dual-token authentication, official MCP workflows, foreign denial, safe telemetry and trace reconstruction. It updates the known-good revision only after success. Inspect sanitized evidence JSON, not bearer values or private records.

Run `python3 scripts/fault_check.py` to test policy unavailability. It proves an authorized write, rolls out an unavailable endpoint, requires 503/no receipt, restores the known-good revision in `finally`, and proves a write again. Run verification afterward. Rollback failure remains visible; inspect rollout status with the dedicated kubeconfig and recorded revision before retrying.

For incidents, join collector spans using the response trace ID and `artifacts/incident-reconstruction.json`; inspect canonical gateway action/reason/outcome events. Foreign rejection can precede OPA. Missing telemetry is not proof of no operation. The observability-audit workshop documents queries, sampling and collector-outage behavior.

One Docker-backed node is not HA. In-memory data resets on rollout; no durable backup/migration claim exists. Debug logs are not immutable audit storage. Offline JWT revocation is bounded by short expiry. Local signing keys are disposable test credentials; CI OIDC is configured, not executed. Six medium/one low release findings remain visible. Infrastructure images are digest-pinned but not all signed/scanned independently by the application release gate.

Cleanup requires the actual owned cluster name and explicit confirmation; it deletes that cluster and prior mesh fixtures, not Docker stacks or artifact files. It was not run. Production egress/ingress certificates, KMS, admission signature policy, long-term audit retention, disaster recovery and production readiness are not asserted.