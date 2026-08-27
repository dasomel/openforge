use crate::Finding;
use serde::Deserialize;
use std::{fs, path::Path, process::Command};

#[derive(Debug, Deserialize)]
pub(crate) struct VerificationSpec {
    #[serde(default)]
    probes: Vec<ServiceProbe>,
}

#[derive(Debug, Deserialize)]
struct ServiceProbe {
    name: String,
    namespace: String,
    service: String,
    port: u16,
    path: String,
    #[serde(default)]
    expect_contains: Option<String>,
}

fn normalize_path(path: &str) -> String {
    if path.starts_with('/') {
        path.to_string()
    } else {
        format!("/{path}")
    }
}

fn service_proxy_path(probe: &ServiceProbe) -> String {
    format!(
        "/api/v1/namespaces/{}/services/http:{}:{}/proxy{}",
        probe.namespace,
        probe.service,
        probe.port,
        normalize_path(&probe.path)
    )
}

fn kubectl_raw(context: Option<&str>, path: &str) -> Result<String, String> {
    let mut command = Command::new("kubectl");
    if let Some(context) = context {
        command.arg("--context").arg(context);
    }
    command.arg("get").arg("--raw").arg(path);

    let output = command
        .output()
        .map_err(|error| format!("kubectl unavailable: {error}"))?;
    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).trim().to_string());
    }
    String::from_utf8(output.stdout).map_err(|error| format!("non-UTF8 probe response: {error}"))
}

fn skipped(reason: String) -> Finding {
    Finding {
        rule_id: "RT-021".to_string(),
        category: "Runtime Recovery".to_string(),
        title: "Declared post-restore functional probes succeed".to_string(),
        status: "SKIP",
        score: 0.0,
        weight: 0.0,
        evidence: vec![reason],
        remediation: String::new(),
    }
}

pub(crate) fn finding(enabled: bool, context: Option<&str>, spec_path: Option<&Path>) -> Finding {
    if !enabled {
        return skipped("runtime assessment disabled; use --runtime".to_string());
    }
    let Some(spec_path) = spec_path else {
        return skipped("no post-restore verification spec supplied".to_string());
    };

    let text = match fs::read_to_string(spec_path) {
        Ok(text) => text,
        Err(error) => return skipped(format!("cannot read verification spec: {error}")),
    };
    let spec: VerificationSpec = match serde_json::from_str(&text) {
        Ok(spec) => spec,
        Err(error) => return skipped(format!("invalid verification spec JSON: {error}")),
    };
    if spec.probes.is_empty() {
        return skipped("verification spec contains no probes".to_string());
    }

    let mut passed = 0usize;
    let mut evidence = Vec::new();

    for probe in &spec.probes {
        let raw_path = service_proxy_path(probe);
        match kubectl_raw(context, &raw_path) {
            Ok(body) => {
                let content_ok = probe
                    .expect_contains
                    .as_deref()
                    .is_none_or(|needle| body.contains(needle));
                if content_ok {
                    passed += 1;
                    evidence.push(format!("probe={} status=pass", probe.name));
                } else {
                    evidence.push(format!(
                        "probe={} status=fail reason=expected_content_missing",
                        probe.name
                    ));
                }
            }
            Err(error) => evidence.push(format!(
                "probe={} status=fail request_error={error}",
                probe.name
            )),
        }
    }

    let total = spec.probes.len();
    let ratio = passed as f64 / total as f64;
    evidence.insert(
        0,
        format!(
            "post_restore_probes_passed={passed}/{total} coverage_percent={:.1}",
            ratio * 100.0
        ),
    );

    Finding {
        rule_id: "RT-021".to_string(),
        category: "Runtime Recovery".to_string(),
        title: "Declared post-restore functional probes succeed".to_string(),
        status: if passed == total { "PASS" } else { "FAIL" },
        score: (ratio * 10.0 * 10.0).round() / 10.0,
        weight: 10.0,
        evidence,
        remediation: "Repair the restored application's service path or data dependencies and rerun the declared read-only functional probes."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::{ServiceProbe, service_proxy_path};

    #[test]
    fn builds_namespaced_service_proxy_path() {
        let probe = ServiceProbe {
            name: "health".to_string(),
            namespace: "prod".to_string(),
            service: "api".to_string(),
            port: 8080,
            path: "healthz".to_string(),
            expect_contains: Some("ok".to_string()),
        };
        assert_eq!(
            service_proxy_path(&probe),
            "/api/v1/namespaces/prod/services/http:api:8080/proxy/healthz"
        );
    }
}
