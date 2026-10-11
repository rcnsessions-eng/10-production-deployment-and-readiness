# Capstone Threat Model

Untrusted goals/model/tool arguments cannot establish identity or tenant authority. Supported bearer validation, server-owned membership/resource metadata, narrow canonical tools, default-deny OPA decisions and transactional scoped repositories remain authoritative. Spoofed headers, foreign records, unknown tools, replay and missing/malformed/unavailable decisions are tested.

Mesh identities restrict API, OPA and collector callers. Wrong accounts and plaintext are denied; approved adapters still cannot bypass application resource checks. Telemetry contains sanitized references/bounded attributes, not tokens/full prompts. Export failure does not silently allow operations.

Signed manifests bind archive, image identity, SBOM/scans and provenance. Verification rejects unsigned/modified artifacts and HIGH/CRITICAL findings before deployment. No exception was needed after Alpine remediation. Local Docker/cluster administrators and the public-key trust decision are trusted; compromised hosts/nodes/build infrastructure are not defended here.

The synthetic IdP uses HTTP/password grants/dev-file. Production identity durability, IdP egress mTLS, audit retention/access controls, secret lifecycle, supply-chain admission and HA remain explicit gaps. Scanning is point-in-time evidence, not a safety guarantee.