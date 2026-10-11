import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEQUENCE = ROOT.parent.parent
MESH = SEQUENCE / "06-istio-workload-security/code"
SUPPLY = SEQUENCE / "09-supply-chain-and-ci/code"
KUBECONFIG = MESH / "artifacts/kubeconfig"


def kubectl(*args: str, payload: str | None = None) -> str:
    result = subprocess.run(
        ["kubectl", "--kubeconfig", str(KUBECONFIG), *args],
        input=payload,
        text=True,
        check=True,
        capture_output=True,
    )
    return result.stdout


def guard() -> str:
    context = kubectl("config", "current-context").strip()
    if context not in {"kind-zero-trust-workload-security", "kind-zero-trust-prd06"}:
        raise ValueError("Only the owned disposable kind cluster is supported")
    return context.removeprefix("kind-")


def mcp_manifest(manifests: str, image: str) -> str:
    decoder = json.JSONDecoder()
    remaining = manifests.strip()
    while remaining:
        manifest, consumed = decoder.raw_decode(remaining)
        remaining = remaining[consumed:].strip()
        if (
            manifest.get("kind") == "Pod"
            and manifest.get("metadata", {}).get("name") == "approved-mcp"
        ):
            for container in manifest["spec"]["containers"]:
                if container["name"] == "client":
                    container["image"] = image
                    return json.dumps(manifest)
            raise ValueError("Approved MCP manifest has no client container")
    raise ValueError("Approved MCP manifest is missing")


def main() -> None:
    cluster = guard()
    subprocess.run(
        [
            "bash",
            str(SUPPLY / "scripts/verify.sh"),
            str(SUPPLY / "artifacts"),
            str(SUPPLY / ".tools/local-signing.pub"),
        ],
        check=True,
    )
    release = json.loads((SUPPLY / "artifacts/release.json").read_text())
    image = (
        "zero-trust-deployment-readiness-gateway:release-"
        + release["files"]["image.tar"].removeprefix("sha256:")[:16]
    )
    subprocess.run(
        ["docker", "tag", "zero-trust-supply-chain-security-gateway:0.1.0", image], check=True
    )
    subprocess.run(
        [str(MESH / ".tools/kind"), "load", "docker-image", image, "--name", cluster],
        check=True,
    )
    subprocess.run(["bash", str(MESH / "scripts/deploy.sh")], check=True)
    configuration = (
        SEQUENCE / "08-observability-audit/code/observability/collector.yaml"
    ).read_text()
    kubectl(
        "apply",
        "-f",
        "-",
        payload=json.dumps(
            {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {"name": "learning-telemetry", "namespace": "learning-mesh"},
                "data": {"config.yaml": configuration},
            }
        ),
    )
    kubectl("apply", "-f", str(ROOT / "deploy/telemetry.yaml"))
    kubectl("set", "image", "deployment/gateway", "gateway=" + image, "-n", "learning-mesh")
    manifests = kubectl(
        "create",
        "--dry-run=client",
        "-f",
        str(MESH / "deploy/kubernetes/workloads.yaml"),
        "-o",
        "json",
    )
    kubectl("replace", "--force", "-f", "-", payload=mcp_manifest(manifests, image))
    for name in ["gateway", "collector"]:
        kubectl(
            "rollout", "status", "deployment/" + name, "-n", "learning-mesh", "--timeout=180s"
        )
    kubectl(
        "wait",
        "--for=condition=Ready",
        "pod/approved-mcp",
        "-n",
        "learning-mesh",
        "--timeout=180s",
    )
    deployment = json.loads(
        kubectl("get", "deployment/gateway", "-n", "learning-mesh", "-o", "json")
    )
    state = {
        "image": image,
        "revision": deployment["metadata"]["annotations"]["deployment.kubernetes.io/revision"],
        "release_archive": release["files"]["image.tar"],
    }
    (ROOT / "artifacts").mkdir(exist_ok=True)
    (ROOT / "artifacts/known-good.json").write_text(json.dumps(state, indent=2) + "\n")
    print("Verified release deployed to the owned mesh; known-good revision recorded")


if __name__ == "__main__":
    main()
