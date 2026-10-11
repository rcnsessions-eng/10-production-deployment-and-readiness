import importlib.util
import json

import pytest
from rollback import rollback_revision
from verify import trace_layers

spec = importlib.util.spec_from_file_location("deploy", "/readiness-scripts/deploy.py")
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


def test_unrelated_context_is_rejected(monkeypatch):
    monkeypatch.setattr(deploy, "kubectl", lambda *args: "lcp-development-1.33")
    with pytest.raises(ValueError):
        deploy.guard()


@pytest.mark.parametrize("name", ["zero-trust-prd06", "zero-trust-workload-security"])
def test_only_owned_cluster_names_are_supported(monkeypatch, name):
    monkeypatch.setattr(deploy, "kubectl", lambda *args: "kind-" + name)
    assert deploy.guard() == name


def test_rollback_requires_verified_release():
    with pytest.raises(ValueError):
        rollback_revision({"revision": "2", "verified": False})
    assert (
        rollback_revision(
            {
                "revision": "2",
                "verified": True,
                "image": "zero-trust-deployment-readiness-gateway:release-test",
            }
        )
        == "2"
    )


def test_incident_reconstruction_groups_by_trace():
    trace = "a" * 32
    logs = "\n".join(
        "Trace ID : " + trace + "\nName : " + layer + ".evidence.record"
        for layer in ["mcp", "api", "service", "policy", "repository"]
    )
    assert trace_layers(logs)[trace] == {"mcp", "api", "service", "policy", "repository"}


def test_mcp_replacement_uses_clean_baseline_and_verified_image():
    baseline = {
        "kind": "Pod",
        "metadata": {"name": "approved-mcp", "labels": {"app": "approved-mcp"}},
        "spec": {"containers": [{"name": "client", "image": "old"}]},
    }
    stream = json.dumps({"kind": "Service"}) + "\n" + json.dumps(baseline)
    replacement = json.loads(deploy.mcp_manifest(stream, "verified-release"))
    assert replacement["spec"]["containers"][0]["image"] == "verified-release"
    assert replacement["metadata"] == baseline["metadata"]
    assert "status" not in replacement
    assert baseline["spec"]["containers"][0]["image"] == "old"


def test_mcp_replacement_rejects_missing_manifest_or_client():
    with pytest.raises(ValueError):
        deploy.mcp_manifest(json.dumps({"kind": "Service"}), "verified-release")
    with pytest.raises(ValueError):
        deploy.mcp_manifest(
            json.dumps(
                {
                    "kind": "Pod",
                    "metadata": {"name": "approved-mcp"},
                    "spec": {"containers": []},
                }
            ),
            "verified-release",
        )
