# Local Release Checklist

- [x] Inherited application/security and Rego gates pass.
- [x] Telemetry privacy/correlation/failure isolation pass.
- [x] Trivy/Syft/Cosign downloads verify their hashes.
- [x] Image/dependency/config scans pass HIGH/CRITICAL thresholds.
- [x] SBOM, immutable identities and provenance are recorded.
- [x] Local signature verifies separately; unsigned/modified inputs fail.
- [x] Verified release deploys only through the dedicated kubeconfig.
- [x] Real mesh/identity/MCP/tenant negative and positive checks pass.
- [x] Incident reconstruction and canary absence pass.
- [x] Policy-fault denial and known-good configuration rollback pass twice.
- [ ] Hosted CI/keyless publication/branch protection verified by repository owner.
- [ ] Production identity/KMS/admission/durable storage/audit/HA assessed.
- [ ] Explicit cleanup requested and executed.

Unchecked production/hosted items are not claims of production approval and do not invalidate the executed local-reference scope.