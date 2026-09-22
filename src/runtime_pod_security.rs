use crate::Finding;
use serde_json::Value;
use std::process::Command;

fn kubectl_json(
    context: Option<&str>,
    namespace: Option<&str>,
    args: &[&str],
) -> Result<Value, String> {
    let mut command = Command::new("kubectl");
    if let Some(context) = context {
        command.arg("--context").arg(context);
    }
    if let Some(namespace) = namespace {
        command.arg("-n").arg(namespace);
    } else {
        command.arg("-A");
    }
    command.args(args).arg("-o").arg("json");

    let output = command
        .output()
        .map_err(|error| format!("kubectl unavailable: {error}"))?;
    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).trim().to_string());
    }
    serde_json::from_slice(&output.stdout).map_err(|error| format!("invalid kubectl JSON: {error}"))
}

fn object_name(item: &Value) -> String {
    let namespace = item
        .pointer("/metadata/namespace")
        .and_then(Value::as_str)
        .unwrap_or("default");
    let kind = item
        .get("kind")
        .and_then(Value::as_str)
        .unwrap_or("Workload");
    let name = item
        .pointer("/metadata/name")
        .and_then(Value::as_str)
        .unwrap_or("unknown");
    format!("{namespace}/{kind}/{name}")
}

fn risky_workloads(value: &Value) -> Vec<String> {
    let mut evidence = Vec::new();

    for item in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let workload = object_name(item);
        let pod_spec = item.pointer("/spec/template/spec").unwrap_or(&Value::Null);

        for field in ["hostNetwork", "hostPID", "hostIPC"] {
            if pod_spec.get(field).and_then(Value::as_bool) == Some(true) {
                evidence.push(format!("{workload} {field}=true"));
            }
        }

        if let Some(volumes) = pod_spec.get("volumes").and_then(Value::as_array) {
            for volume in volumes {
                if volume.get("hostPath").is_some() {
                    let name = volume
                        .get("name")
                        .and_then(Value::as_str)
                        .unwrap_or("unknown");
                    evidence.push(format!("{workload} hostPath_volume={name}"));
                }
            }
        }

        for containers_field in ["containers", "initContainers"] {
            for container in pod_spec
                .get(containers_field)
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
            {
                let name = container
                    .get("name")
                    .and_then(Value::as_str)
                    .unwrap_or("unknown");
                let security = container.get("securityContext").unwrap_or(&Value::Null);

                if security.get("privileged").and_then(Value::as_bool) == Some(true) {
                    evidence.push(format!("{workload}:{name} privileged=true"));
                }
                if security
                    .get("allowPrivilegeEscalation")
                    .and_then(Value::as_bool)
                    == Some(true)
                {
                    evidence.push(format!("{workload}:{name} allowPrivilegeEscalation=true"));
                }
                if security.get("runAsUser").and_then(Value::as_u64) == Some(0) {
                    evidence.push(format!("{workload}:{name} runAsUser=0"));
                }

                if let Some(capabilities) = security
                    .pointer("/capabilities/add")
                    .and_then(Value::as_array)
                {
                    for capability in capabilities.iter().filter_map(Value::as_str) {
                        if matches!(
                            capability,
                            "SYS_ADMIN"
                                | "NET_ADMIN"
                                | "SYS_PTRACE"
                                | "SYS_MODULE"
                                | "DAC_READ_SEARCH"
                        ) {
                            evidence.push(format!("{workload}:{name} capability_add={capability}"));
                        }
                    }
                }
            }
        }
    }

    evidence.sort();
    evidence.dedup();
    evidence
}

fn skipped(reason: String) -> Finding {
    Finding {
        rule_id: "RT-010".to_string(),
        category: "Runtime Security".to_string(),
        title: "No explicitly high-risk Pod security settings are configured".to_string(),
        status: "SKIP",
        score: 0.0,
        weight: 0.0,
        evidence: vec![reason],
        remediation: String::new(),
    }
}

pub(crate) fn finding(enabled: bool, context: Option<&str>, namespace: Option<&str>) -> Finding {
    if !enabled {
        return skipped("runtime assessment disabled; use --runtime".to_string());
    }

    let value = match kubectl_json(
        context,
        namespace,
        &["get", "deployments,statefulsets,daemonsets"],
    ) {
        Ok(value) => value,
        Err(error) => return skipped(error),
    };
    let risky = risky_workloads(&value);

    Finding {
        rule_id: "RT-010".to_string(),
        category: "Runtime Security".to_string(),
        title: "No explicitly high-risk Pod security settings are configured".to_string(),
        status: if risky.is_empty() { "PASS" } else { "FAIL" },
        score: if risky.is_empty() { 10.0 } else { 0.0 },
        weight: 10.0,
        evidence: if risky.is_empty() {
            vec!["explicit_high_risk_pod_security_settings=0".to_string()]
        } else {
            risky
        },
        remediation: "Remove privileged/root/host namespace settings, dangerous Linux capabilities and hostPath unless explicitly required and reviewed."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::risky_workloads;
    use serde_json::json;

    #[test]
    fn reports_explicit_high_risk_settings() {
        let value = json!({
            "items": [{
                "kind": "Deployment",
                "metadata": {"namespace": "apps", "name": "api"},
                "spec": {"template": {"spec": {
                    "hostNetwork": true,
                    "volumes": [{"name": "host", "hostPath": {"path": "/"}}],
                    "containers": [{
                        "name": "api",
                        "securityContext": {
                            "privileged": true,
                            "allowPrivilegeEscalation": true,
                            "runAsUser": 0,
                            "capabilities": {"add": ["SYS_ADMIN"]}
                        }
                    }]
                }}}
            }]
        });

        let risky = risky_workloads(&value);
        assert!(risky.iter().any(|item| item.contains("hostNetwork=true")));
        assert!(risky.iter().any(|item| item.contains("privileged=true")));
        assert!(risky.iter().any(|item| item.contains("hostPath_volume")));
        assert!(risky.iter().any(|item| item.contains("SYS_ADMIN")));
    }

    #[test]
    fn does_not_fail_on_missing_hardening_fields() {
        let value = json!({
            "items": [{
                "kind": "Deployment",
                "metadata": {"namespace": "apps", "name": "api"},
                "spec": {"template": {"spec": {
                    "containers": [{"name": "api"}]
                }}}
            }]
        });

        assert!(risky_workloads(&value).is_empty());
    }
}
