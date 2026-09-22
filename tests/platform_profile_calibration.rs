use serde_json::Value;
use std::{
    fs,
    path::{Path, PathBuf},
    process::Command,
    time::{SystemTime, UNIX_EPOCH},
};

fn openforge() -> PathBuf {
    PathBuf::from(env!("CARGO_BIN_EXE_openforge"))
}

fn temp_dir(name: &str) -> PathBuf {
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("system clock")
        .as_nanos();
    let root = std::env::temp_dir().join(format!(
        "openforge-platform-calibration-{name}-{}-{nonce}",
        std::process::id()
    ));
    fs::create_dir_all(&root).expect("fixture directory");
    root
}

fn write(root: &Path, relative: &str, content: &str) {
    let path = root.join(relative);
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).expect("fixture parent");
    }
    fs::write(path, content).expect("fixture file");
}

fn finding<'a>(report: &'a Value, rule_id: &str) -> &'a Value {
    report["findings"]
        .as_array()
        .expect("findings array")
        .iter()
        .find(|finding| finding["rule_id"] == rule_id)
        .unwrap_or_else(|| panic!("missing finding {rule_id}"))
}

#[test]
fn kubernetes_platform_recognizes_gitops_and_shell_regression_evidence() {
    let root = temp_dir("gitops");
    write(&root, "README.md", "# Fixture\n");
    write(&root, "CONTRIBUTING.md", "# Contributing\n");
    write(&root, "CHANGELOG.md", "# Changelog\n");
    write(
        &root,
        ".github/workflows/ci.yml",
        "jobs:\n  regression:\n    steps:\n      - run: ./scripts/test/regression-check.sh --static\n",
    );
    write(
        &root,
        "gitops/workloads/app.yaml",
        r#"apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
        - name: app
          resources:
            requests:
              cpu: 100m
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app
spec:
  podSelector: {}
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app
spec:
  minAvailable: 1
"#,
    );
    write(&root, "docs/screenshot.md", "![dashboard](image.png)\n");

    let output = Command::new(openforge())
        .arg("assess")
        .arg(&root)
        .arg("--profile")
        .arg("kubernetes-platform")
        .arg("--format")
        .arg("json")
        .output()
        .expect("assessment should run");

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let report: Value = serde_json::from_slice(&output.stdout).expect("valid assessment JSON");

    for rule_id in ["CI-002", "PLT-002", "PLT-003", "PLT-004", "PLT-005"] {
        assert_eq!(finding(&report, rule_id)["status"], "PASS", "{rule_id}");
    }
    for rule_id in [
        "WEB-001", "WEB-002", "WEB-003", "WEB-004", "WEB-005", "WEB-006", "WEB-007", "WEB-008",
        "WEB-009",
    ] {
        assert_eq!(
            finding(&report, rule_id)["status"],
            "NOT_APPLICABLE",
            "{rule_id}"
        );
    }
}
