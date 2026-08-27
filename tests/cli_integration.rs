use serde_json::Value;
use std::{
    fs,
    path::{Path, PathBuf},
    process::{Command, Output},
    time::{SystemTime, UNIX_EPOCH},
};

fn openforge() -> PathBuf {
    PathBuf::from(env!("CARGO_BIN_EXE_openforge"))
}

fn run(args: &[&str]) -> Output {
    Command::new(openforge())
        .args(args)
        .output()
        .expect("openforge command should run")
}

fn temp_dir(name: &str) -> PathBuf {
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("system clock")
        .as_nanos();
    let path = std::env::temp_dir().join(format!(
        "openforge-cli-{name}-{}-{nonce}",
        std::process::id()
    ));
    fs::create_dir_all(&path).expect("temp directory should be created");
    path
}

fn write_assessment(path: &Path, overall: f64, status: &str, score: f64) {
    let document = serde_json::json!({
        "schema": "openforge-assessment/v0.12",
        "ruleset": "maturity-v0.1",
        "root": ".",
        "execution_enabled": false,
        "runtime_enabled": false,
        "runtime_context": null,
        "runtime_namespace": null,
        "post_restore_spec": null,
        "policy": null,
        "overall": overall,
        "grade": if overall >= 80.0 { "B" } else { "C" },
        "level": if overall >= 80.0 { "L4 Resilient" } else { "L3 Production" },
        "categories": {
            "Test": { "score": overall, "earned": score, "max": 10.0 }
        },
        "findings": [{
            "rule_id": "T-001",
            "category": "Test",
            "title": "Fixture rule",
            "status": status,
            "score": score,
            "weight": 10.0,
            "evidence": [],
            "remediation": ""
        }]
    });
    fs::write(path, serde_json::to_string_pretty(&document).unwrap())
        .expect("fixture should be written");
}

#[test]
fn assess_subcommand_outputs_assessment_json() {
    let manifest = env!("CARGO_MANIFEST_DIR");
    let output = run(&["assess", manifest, "--format", "json"]);
    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );

    let report: Value = serde_json::from_slice(&output.stdout).expect("valid assessment JSON");
    assert_eq!(report["schema"], "openforge-assessment/v0.12");
    assert!(report["overall"].as_f64().is_some());
    assert!(
        report["findings"]
            .as_array()
            .is_some_and(|items| !items.is_empty())
    );
}

#[test]
fn legacy_assess_alias_remains_supported() {
    let manifest = env!("CARGO_MANIFEST_DIR");
    let output = run(&[manifest, "--format", "json"]);
    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );

    let report: Value = serde_json::from_slice(&output.stdout).expect("valid assessment JSON");
    assert_eq!(report["schema"], "openforge-assessment/v0.12");
}

#[test]
fn compare_detects_regression_and_returns_exit_two() {
    let dir = temp_dir("compare");
    let before = dir.join("before.json");
    let after = dir.join("after.json");
    write_assessment(&before, 100.0, "PASS", 10.0);
    write_assessment(&after, 70.0, "FAIL", 0.0);

    let output = Command::new(openforge())
        .arg("compare")
        .arg(&before)
        .arg(&after)
        .arg("--format")
        .arg("json")
        .arg("--fail-on-regression")
        .output()
        .expect("compare should run");

    assert_eq!(output.status.code(), Some(2));
    let comparison: Value = serde_json::from_slice(&output.stdout).expect("valid comparison JSON");
    assert_eq!(comparison["schema"], "openforge-comparison/v0.2");
    assert_eq!(comparison["summary"]["regressed"], 1);
}

#[test]
fn baseline_create_and_check_use_unified_cli() {
    let dir = temp_dir("baseline");
    let current = dir.join("current.json");
    let baseline = dir.join("baseline.json");
    write_assessment(&current, 90.0, "PASS", 10.0);

    let create = Command::new(openforge())
        .arg("baseline")
        .arg("create")
        .arg(&current)
        .arg(&baseline)
        .output()
        .expect("baseline create should run");
    assert!(
        create.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&create.stderr)
    );

    let baseline_json: Value =
        serde_json::from_str(&fs::read_to_string(&baseline).expect("baseline should exist"))
            .expect("valid baseline JSON");
    assert_eq!(
        baseline_json["_baseline"]["schema"],
        "openforge-baseline/v0.1"
    );

    let check = Command::new(openforge())
        .arg("baseline")
        .arg("check")
        .arg(&baseline)
        .arg(&current)
        .arg("--fail-on-regression")
        .arg("--require-compatible")
        .output()
        .expect("baseline check should run");
    assert!(
        check.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&check.stderr)
    );
}
