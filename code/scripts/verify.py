import json
import re
import subprocess

from deploy import MESH, ROOT, guard, kubectl


def trace_layers(logs: str) -> dict[str, set[str]]:
    traces: dict[str, set[str]] = {}
    current = ""
    for line in logs.splitlines():
        trace = re.search(r"Trace ID\s*:\s*([a-f0-9]{32})", line)
        if trace:
            current = trace.group(1)
        name = re.search(r"Name\s*:\s*(api|mcp|policy|repository|service)\.", line)
        if current and name:
            traces.setdefault(current, set()).add(name.group(1))
    return traces


def main() -> None:
    guard()
    subprocess.run(["python3", str(MESH / "scripts/verify.py")], check=True)
    print(
        kubectl(
            "exec",
            "approved-mcp",
            "-n",
            "learning-mesh",
            "-c",
            "client",
            "--",
            "python",
            "/telemetry-scripts/smoke.py",
        )
    )
    print(
        kubectl(
            "exec",
            "unapproved-client",
            "-n",
            "learning-mesh",
            "-c",
            "client",
            "--",
            "python",
            "-c",
            "import httpx; response=httpx.post('http://collector:4318/v1/traces', "
            "json={}, timeout=5, trust_env=False); assert response.status_code==403; "
            "print('Unauthorized telemetry exporter denied')",
        )
    )
    logs = kubectl(
        "logs", "deployment/collector", "-n", "learning-mesh", "-c", "collector", "--tail=5000"
    )
    gateway_logs = kubectl(
        "logs", "deployment/gateway", "-n", "learning-mesh", "-c", "gateway", "--tail=1500"
    )
    if "FAKE-SECRET-OBSERVABILITY-DO-NOT-LOG" in logs + gateway_logs:
        raise ValueError("Secret canary found in telemetry")
    traces = trace_layers(logs)
    complete = [
        trace
        for trace, layers in traces.items()
        if layers >= {"mcp", "api", "service", "policy", "repository"}
    ]
    if not complete:
        raise ValueError("No complete deployed MCP/API/service/policy/repository trace")
    if '"decision":"deny"' not in gateway_logs:
        raise ValueError("Missing deployed authorization denial audit")
    state = json.loads((ROOT / "artifacts/known-good.json").read_text())
    deployment = json.loads(
        kubectl("get", "deployment/gateway", "-n", "learning-mesh", "-o", "json")
    )
    if deployment["spec"]["template"]["spec"]["containers"][0]["image"] != state["image"]:
        raise ValueError("Deployed image differs from verified release")
    state["verified"] = True
    state["revision"] = deployment["metadata"]["annotations"][
        "deployment.kubernetes.io/revision"
    ]
    (ROOT / "artifacts/known-good.json").write_text(json.dumps(state, indent=2) + "\n")
    evidence = {
        "reconstructed_trace_id": complete[-1],
        "layers": sorted(traces[complete[-1]]),
        "canary_occurrences": 0,
        "foreign_denial_audited": True,
        "unauthorized_exporter_denied": True,
    }
    (ROOT / "artifacts/incident-reconstruction.json").write_text(
        json.dumps(evidence, indent=2) + "\n"
    )
    print("Deployed security smoke and incident reconstruction passed: " + complete[-1])


if __name__ == "__main__":
    main()
