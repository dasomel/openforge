use crate::Finding;
use serde_json::Value;
use std::{collections::BTreeSet, process::Command};

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
            let kind = subject
                .get("kind")
                .and_then(Value::as_str)
                .unwrap_or("Unknown");
            let name = subject
                .get("name")
                .and_then(Value::as_str)
                .unwrap_or("unknown");
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

fn non_system_bound_cluster_roles(bindings: &Value) -> BTreeSet<String> {
    let mut roles = BTreeSet::new();
    for binding in bindings
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        if binding.pointer("/roleRef/kind").and_then(Value::as_str) != Some("ClusterRole") {
            continue;
        }
        let has_non_system_subject = binding
            .get("subjects")
            .and_then(Value::as_array)
            .is_some_and(|subjects| subjects.iter().any(|subject| !is_system_subject(subject)));
        if !has_non_system_subject {
            continue;
        }
        if let Some(name) = binding.pointer("/roleRef/name").and_then(Value::as_str) {
            roles.insert(name.to_string());
        }
    }
    roles
}

fn risky_bound_role_rules(bindings: &Value, roles: &Value) -> Vec<String> {
    let bound_roles = non_system_bound_cluster_roles(bindings);
    let mut risky = Vec::new();

    for role in roles
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let role_name = role
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        if !bound_roles.contains(role_name) || role_name == "cluster-admin" {
            continue;
        }

        for (index, rule) in role
            .get("rules")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
            .enumerate()
        {
            let verbs: Vec<&str> = rule
                .get("verbs")
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
                .filter_map(Value::as_str)
                .collect();
            let resources: Vec<&str> = rule
                .get("resources")
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
                .filter_map(Value::as_str)
                .collect();
            let api_groups: Vec<&str> = rule
                .get("apiGroups")
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
                .filter_map(Value::as_str)
                .collect();

            let privileged_verb = verbs
                .iter()
                .any(|verb| matches!(*verb, "escalate" | "bind" | "impersonate"));
            let wildcard =
                verbs.contains(&"*") || resources.contains(&"*") || api_groups.contains(&"*");

            if privileged_verb || wildcard {
                risky.push(format!(
                    "clusterrole={role_name} rule={index} verbs={} resources={} apiGroups={}",
                    verbs.join(","),
                    resources.join(","),
                    api_groups.join(",")
                ));
            }
        }
    }

    risky
}

fn skipped(id: &str, title: &str, reason: String) -> Finding {
    Finding {
        rule_id: id.to_string(),
        category: "Runtime Security".to_string(),
        title: title.to_string(),
        status: "SKIP",
        score: 0.0,
        weight: 0.0,
        evidence: vec![reason],
        remediation: String::new(),
    }
}

fn cluster_admin_finding(bindings: &Value) -> Finding {
    let risky = risky_cluster_admin_subjects(bindings);
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

fn risky_privilege_finding(bindings: &Value, roles: &Value) -> Finding {
    let risky = risky_bound_role_rules(bindings, roles);
    Finding {
        rule_id: "RT-009".to_string(),
        category: "Runtime Security".to_string(),
        title: "No high-risk wildcard or RBAC escalation privileges are bound to non-system subjects"
            .to_string(),
        status: if risky.is_empty() { "PASS" } else { "FAIL" },
        score: if risky.is_empty() { 10.0 } else { 0.0 },
        weight: 10.0,
        evidence: if risky.is_empty() {
            vec!["high_risk_bound_clusterrole_rules=0".to_string()]
        } else {
            risky
        },
        remediation: "Replace wildcard, escalate, bind, or impersonate permissions with explicit least-privilege rules."
            .to_string(),
    }
}

pub(crate) fn findings(enabled: bool, context: Option<&str>) -> Vec<Finding> {
    if !enabled {
        let reason = "runtime assessment disabled; use --runtime".to_string();
        return vec![
            skipped(
                "RT-008",
                "No non-system subjects are bound to cluster-admin",
                reason.clone(),
            ),
            skipped(
                "RT-009",
                "No high-risk wildcard or RBAC escalation privileges are bound to non-system subjects",
                reason,
            ),
        ];
    }

    let bindings = match kubectl_json(context, &["get", "clusterrolebindings"]) {
        Ok(value) => value,
        Err(error) => {
            return vec![
                skipped(
                    "RT-008",
                    "No non-system subjects are bound to cluster-admin",
                    error.clone(),
                ),
                skipped(
                    "RT-009",
                    "No high-risk wildcard or RBAC escalation privileges are bound to non-system subjects",
                    error,
                ),
            ];
        }
    };
    let roles = match kubectl_json(context, &["get", "clusterroles"]) {
        Ok(value) => value,
        Err(error) => {
            return vec![
                cluster_admin_finding(&bindings),
                skipped(
                    "RT-009",
                    "No high-risk wildcard or RBAC escalation privileges are bound to non-system subjects",
                    error,
                ),
            ];
        }
    };

    vec![
        cluster_admin_finding(&bindings),
        risky_privilege_finding(&bindings, &roles),
    ]
}

#[cfg(test)]
mod tests {
    use super::{risky_bound_role_rules, risky_cluster_admin_subjects};
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

    #[test]
    fn reports_wildcard_rules_only_when_role_is_bound_to_non_system_subject() {
        let bindings = json!({
            "items": [{
                "roleRef": {"kind": "ClusterRole", "name": "dangerous"},
                "subjects": [{"kind": "User", "name": "alice"}]
            }]
        });
        let roles = json!({
            "items": [
                {
                    "metadata": {"name": "dangerous"},
                    "rules": [{"apiGroups": ["*"], "resources": ["*"], "verbs": ["*"]}]
                },
                {
                    "metadata": {"name": "unused-dangerous"},
                    "rules": [{"apiGroups": ["*"], "resources": ["*"], "verbs": ["*"]}]
                }
            ]
        });

        let risky = risky_bound_role_rules(&bindings, &roles);
        assert_eq!(risky.len(), 1);
        assert!(risky[0].contains("dangerous"));
    }

    #[test]
    fn reports_escalation_verbs() {
        let bindings = json!({
            "items": [{
                "roleRef": {"kind": "ClusterRole", "name": "rbac-manager"},
                "subjects": [{"kind": "ServiceAccount", "name": "manager", "namespace": "apps"}]
            }]
        });
        let roles = json!({
            "items": [{
                "metadata": {"name": "rbac-manager"},
                "rules": [{"apiGroups": ["rbac.authorization.k8s.io"], "resources": ["clusterroles"], "verbs": ["bind"]}]
            }]
        });

        let risky = risky_bound_role_rules(&bindings, &roles);
        assert_eq!(risky.len(), 1);
        assert!(risky[0].contains("bind"));
    }
}
