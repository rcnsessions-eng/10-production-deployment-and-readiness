import json
from typing import Any

from deploy import ROOT, guard, kubectl


def rollback_revision(state: dict[str, Any]) -> str:
    if state.get("verified") is not True or not str(state.get("revision", "")).isdigit():
        raise ValueError("A smoke-verified known-good revision is required")
    if not state.get("image", "").startswith(
        "zero-trust-deployment-readiness-gateway:release-"
    ):
        raise ValueError("Known-good image must be a verified release tag")
    return str(state["revision"])


def main() -> None:
    guard()
    state = json.loads((ROOT / "artifacts/known-good.json").read_text())
    revision = rollback_revision(state)
    print(
        kubectl(
            "rollout",
            "undo",
            "deployment/gateway",
            "-n",
            "learning-mesh",
            "--to-revision=" + revision,
        )
    )
    print(
        kubectl(
            "rollout", "status", "deployment/gateway", "-n", "learning-mesh", "--timeout=180s"
        )
    )


if __name__ == "__main__":
    main()
