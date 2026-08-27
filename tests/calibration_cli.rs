use serde_json::Value;
use std::{
    fs,
    path::PathBuf,
    process::Command,
    time::{SystemTime, UNIX_EPOCH},
};

fn openforge() -> PathBuf {
    PathBuf::from(env!("CARGO_BIN_EXE_openforge"))
}

fn temp(name: &str) -> PathBuf {
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("system clock")
        .as_nanos();
    std::env::temp_dir().join(format!(
        "openforge-calibration-cli-{name}-{}-{nonce}.json",
        std::process::id()
    ))
}

#[test]
fn calibrate_outputs_machine_readable_report() {
    let assessment = temp("assessment");
    let expectations = temp("expectations");

    fs::write(
        &assessment,
        r#"{"schema":"openforge-assessment/v0.17","ruleset":"maturity-v0.1","findings":[{"rule_id":"DOC-001","status":"PASS"},{"rule_id":"CI-002","status":"FAIL"}]}"#,
    )
    .unwrap();
    fs::write(
        &expectations,
        r#"{"project":"fixture","expectations":{"DOC-001":{"classification":"accepted","rationale":"expected pass"},"CI-002":{"classification":"false_positive","rationale":"known detector gap"}}}"#,
    )
    .unwrap();

    let output = Command::new(openforge())
        .arg("calibrate")
        .arg(&assessment)
        .arg(&expectations)
        .arg("--format")
        .arg("json")
        .arg("--require-complete")
        .output()
        .expect("calibrate should run");

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let report: Value = serde_json::from_slice(&output.stdout).expect("valid calibration JSON");
    assert_eq!(report["schema"], "openforge-calibration/v0.2");
    assert_eq!(report["summary"]["classified_rules"], 2);
    assert_eq!(report["summary"]["unclassified_rules"], 0);
    assert_eq!(report["summary"]["inactive_rules"], 0);
    assert_eq!(report["summary"]["false_positives"], 1);
}

#[test]
fn require_complete_returns_exit_two_for_unclassified_active_rules() {
    let assessment = temp("incomplete-assessment");
    let expectations = temp("incomplete-expectations");

    fs::write(
        &assessment,
        r#"{"findings":[{"rule_id":"A","status":"PASS"},{"rule_id":"B","status":"FAIL"},{"rule_id":"R","status":"SKIP"}]}"#,
    )
    .unwrap();
    fs::write(
        &expectations,
        r#"{"project":"fixture","expectations":{"A":{"classification":"accepted"}}}"#,
    )
    .unwrap();

    let output = Command::new(openforge())
        .arg("calibrate")
        .arg(&assessment)
        .arg(&expectations)
        .arg("--require-complete")
        .output()
        .expect("calibrate should run");

    assert_eq!(output.status.code(), Some(2));
}
