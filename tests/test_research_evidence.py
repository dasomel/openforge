"""Regression coverage for the portable research evidence scripts."""

import ast
import copy
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "templates/scripts"


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "remote", "add", "origin", "https://github.com/example/project.git"], check=True)
    (tmp_path / "README.md").write_text("fixture\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "fixture"], check=True)
    target = tmp_path / "scripts/research"
    target.mkdir(parents=True)
    for name in ("record-evidence.py", "check-research-evidence.py"):
        shutil.copy2(SCRIPTS / name, target / name)
    evidence = tmp_path / "research/evidence"
    evidence.mkdir(parents=True)
    return tmp_path


def run_check(repo):
    return subprocess.run([sys.executable, str(repo / "scripts/research/check-research-evidence.py")],
                          cwd=repo, text=True, capture_output=True)


def good_record(repo):
    revision = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    return {"schema_version": "1.0", "timestamp": "2026-09-30T00:00:00Z", "repository": "example/project",
            "revision": revision, "event_type": "test", "task_or_test": "pytest", "result": "pass",
            "duration_ms": 5, "environment": "local-linux-x64", "attempt": 1,
            "human_interventions": 0, "review_corrections": 0, "ci_retries": 0, "metadata": {}}


def write_record(repo, record):
    path = repo / "research/evidence/2026-09.jsonl"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    return path


def test_embedded_schema_matches_source_of_truth():
    tree = ast.parse((SCRIPTS / "check-research-evidence.py").read_text())
    schema = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == "SCHEMA" for target in node.targets))
    assert schema == json.loads((ROOT / "schemas/research-evidence-v1.schema.json").read_text())


def test_valid_fixture_and_recorder(repo, tmp_path):
    write_record(repo, good_record(repo))
    assert run_check(repo).returncode == 0
    env = os.environ.copy()
    env["RESEARCH_EVIDENCE_DIR"] = str(tmp_path / "separate")
    process = subprocess.run([sys.executable, str(repo / "scripts/research/record-evidence.py"),
                              "--task", "PR #7 / smoke", "--event-type", "test", "--environment", "local/macos:arm64",
                              "--", sys.executable, "-c", "raise SystemExit(7)", "private-command-argument"],
                             cwd=repo, env=env, text=True, capture_output=True)
    assert process.returncode == 7
    lines = next((tmp_path / "separate").glob("*.jsonl")).read_text()
    record = json.loads(lines)
    assert record["result"] == "fail" and record["duration_ms"] >= 0
    assert record["task_or_test"] == "PR 7 - smoke"
    assert record["environment"] == "local-macos-arm64"
    assert "private-command-argument" not in lines


def test_verification_alias_and_secret_redaction(repo, tmp_path):
    env = os.environ.copy()
    env["RESEARCH_EVIDENCE_DIR"] = str(tmp_path / "separate")
    process = subprocess.run([sys.executable, str(repo / "scripts/research/record-evidence.py"),
                              "--task", "verification", "--event-type", "verification",
                              "--failure-stage", "token=abcdefghijklmnop",
                              "--", sys.executable, "-c", "pass"],
                             cwd=repo, env=env, text=True, capture_output=True)
    assert process.returncode == 0
    contents = next((tmp_path / "separate").glob("*.jsonl")).read_text()
    record = json.loads(contents)
    assert record["event_type"] == "test"
    assert record["metadata"]["failure_stage"] == "[REDACTED]"
    assert "abcdefghijklmnop" not in contents


@pytest.mark.parametrize("field,value,reason", [
    ("environment", "github-actions:ubuntu-latest", "environment"),
    ("task_or_test", "PR #7 test", "task_or_test"),
    ("metadata", {"nested": {"status": "pass"}}, "metadata"),
    ("metadata", {"checks": ["pytest"]}, "metadata"),
    ("schema_version", "0.1", "schema_version"),
    ("event_type", "verification", "event_type"),
    ("environment", {"os": "macOS"}, "environment"),
    ("revision", "0" * 40, "revision does not exist"),
    ("timestamp", "not-a-date", "timestamp"),
    ("metadata", {"token": "token=abcdefghijklmnop"}, "secret-pattern"),
    ("metadata", {"token": "abcdefghijklmnop"}, "secret-pattern"),
])
def test_bad_fixture_classes(repo, field, value, reason):
    record = copy.deepcopy(good_record(repo))
    record[field] = value
    write_record(repo, record)
    result = run_check(repo)
    assert result.returncode != 0
    assert reason in result.stderr


def test_invalid_json_and_new_bad_line(repo):
    path = write_record(repo, good_record(repo))
    with path.open("a") as stream:
        stream.write("{bad json}\n")
    result = run_check(repo)
    assert result.returncode != 0 and "invalid JSON" in result.stderr


def test_allowlist_is_hash_pinned(repo):
    bad = good_record(repo)
    bad["environment"] = "local/macos-arm64"
    path = write_record(repo, bad)
    raw = path.read_bytes()
    allowlist = [{"file": path.name, "line": 1, "sha256": hashlib.sha256(raw).hexdigest(),
                  "reason": "legacy environment includes slash"}]
    (path.parent / "known-invalid.json").write_text(json.dumps(allowlist))
    assert run_check(repo).returncode == 0
    path.write_bytes(raw.replace(b"macos", b"linux"))
    result = run_check(repo)
    assert result.returncode != 0 and "hash mismatch" in result.stderr
