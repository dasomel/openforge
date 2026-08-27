use crate::Finding;
use serde_json::Value;
use std::process::Command;

fn kubectl_json(context: Option<&str>, args: &[&str]) -> Result<Value, String> {
    let mut command = Command::new("kubectl");
    if let Some(context) = context {
        command.arg("--context").arg(context);
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

fn is_system_subject(subject: &Value) -> bool {
    let kind = subject.get("kind").and_then(Value::as_str).unwrap_or("");
    let name = subject.get("name").and_then(Value::as_str).unwrap_or("");
    let namespace = subject
        .get("namespace")
        .and_then(Value::as_str)
        .unwrap_or("");

    name.starts_with("system:")
        || (kind == "ServiceAccount" && namespace == "kube-system")
        || (kind == "Group" && name == "system:masters")
}

fn risky_cluster_admin_subjects(value: &Value) -> Vec<String> {
    let mut risky = Vec::new();

    for binding in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let role_name = binding
            .pointer("/roleRef/name")
            .and_then(Value::as_str)
            .unwrap_or("");
        let role_kind = binding
            .pointer("/roleRef/kind")
            .and_then(Value::as_str)
            .unwrap_or("");
        if role_kind != "ClusterRole" || role_name != "cluster-admin" {
            continue;
        }

        let binding_name = binding
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        for subject in binding
            .get("subjects")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
        {
            if is_system_subject(subject) {
                continue;
            }
            let kind = subject.get("kind").and_then(Value::as_str).unwrap_or("Unknown");
            let name = subject.get("name").and_then(Value::as_str).unwrap_or("unknown");
            let namespace = subject
                .get("namespace")
                .and_then(Value::as_str)
                .map(|namespace| format!(" namespace={namespace}"))
                .unwrap_or_default();
            risky.push(format!(
                "binding={binding_name} subject={kind}/{name}{namespace}"
            ));
        }
    }

    risky
}

fn skipped(reason: String) -> Finding {
    Finding {
        rule_id: "RT-008".to_string(),
        category: "Runtime Security".to_string(),
        title: "No non-system subjects are bound to cluster-admin".to_string(),
        status: "SKIP",
        score: 0.0,
        weight: 0.0,
        evidence: vec![reason],
        remediation: String::new(),
    }
}

pub(crate) fn finding(enabled: bool, context: Option<&str>) -> Finding {
    if !enabled {
        return skipped("runtime assessment disabled; use --runtime".to_string());
    }

    let value = match kubectl_json(context, &["get", "clusterrolebindings"]) {
        Ok(value) => value,
        Err(error) => return skipped(error),
    };
    let risky = risky_cluster_admin_subjects(&value);

    Finding {
        rule_id: "RT-008".to_string(),
        category: "Runtime Security".to_string(),
        title: "No non-system subjects are bound to cluster-admin".to_string(),
        status: if risky.is_empty() { "PASS" } else { "FAIL" },
        score: if risky.is_empty() { 10.0 } else { 0.0 },
        weight: 10.0,
        evidence: if risky.is_empty() {
            vec!["non_system_cluster_admin_subjects=0".to_string()]
        } else {
            risky
        },
        remediation: "Replace broad cluster-admin bindings with least-privilege ClusterRoles and scoped bindings."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::risky_cluster_admin_subjects;
    use serde_json::json;

    #[test]
    fn ignores_system_and_reports_non_system_cluster_admin_subjects() {
        let value = json!({
            "items": [
                {
                    "metadata": {"name": "system-binding"},
                    "roleRef": {"kind": "ClusterRole", "name": "cluster-admin"},
                    "subjects": [{"kind": "Group", "name": "system:masters"}]
                },
                {
                    "metadata": {"name": "human-admin"},
                    "roleRef": {"kind": "ClusterRole", "name": "cluster-admin"},
                    "subjects": [{"kind": "User", "name": "alice"}]
                }
            ]
        });

        let risky = risky_cluster_admin_subjects(&value);
        assert_eq!(risky.len(), 1);
        assert!(risky[0].contains("alice"));
    }
}
