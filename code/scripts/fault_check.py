import json
import subprocess

from deploy import ROOT, guard, kubectl
from rollback import rollback_revision


def probe(expected: int) -> None:
    print(
        kubectl(
            "exec",
            "-i",
            "approved-mcp",
            "-n",
            "learning-mesh",
            "-c",
            "client",
            "--",
            "python",
            "-",
            str(expected),
            payload=(ROOT / "scripts/fault_probe.py").read_text(),
        )
    )


def main() -> None:
    guard()
    state = json.loads((ROOT / "artifacts/known-good.json").read_text())
    rollback_revision(state)
    probe(200)
    try:
        kubectl(
            "set",
            "env",
            "deployment/gateway",
            "-n",
            "learning-mesh",
            "OPA_URL=http://127.0.0.1:9",
        )
        kubectl(
            "rollout", "status", "deployment/gateway", "-n", "learning-mesh", "--timeout=180s"
        )
        probe(503)
    finally:
        subprocess.run(["python3", str(ROOT / "scripts/rollback.py")], check=True)
    probe(200)
    (ROOT / "artifacts/rollback-evidence.json").write_text(
        json.dumps(
            {
                "known_good_image": state["image"],
                "known_good_revision": state["revision"],
                "unavailable_policy_write_status": 503,
                "restored_write_status": 200,
                "fault": "unavailable policy endpoint configuration",
                "rollback_demonstrated": True,
            },
            indent=2,
        )
        + "\n"
    )
    print("Policy failure remained closed; verified release configuration rollback passed")


if __name__ == "__main__":
    main()
