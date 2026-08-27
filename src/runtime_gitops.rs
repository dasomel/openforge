use crate::Finding;
use serde_json::Value;
use std::process::Command;

fn kubectl_json(context: Option<&str>, resource: &str) -> Result<Value, String> {
    let mut command = Command::new("kubectl");
    if let Some(context) = context {
        command.arg("--context").arg(context);
    }
    command
        .args(["get", resource])
        .arg("-A")
        .arg("-o")
        .arg("json");

    let output = command
        .output()
        .map_err(|error| format!("kubectl unavailable: {error}"))?;
    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).trim().to_string());
    }
    serde_json::from_slice(&output.stdout).map_err(|error| format!("invalid kubectl JSON: {error}"))
}

fn argo_findings(value: &Value) -> (usize, Vec<String>) {
    let mut total = 0usize;
    let mut unhealthy = Vec::new();

    for item in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        total += 1;
        let namespace = item
            .pointer("/metadata/namespace")
            .and_then(Value::as_str)
            .unwrap_or("default");
        let name = item
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        let sync = item
            .pointer("/status/sync/status")
            .and_then(Value::as_str)
            .unwrap_or("Unknown");
        let health = item
            .pointer("/status/health/status")
            .and_then(Value::as_str)
            .unwrap_or("Unknown");

        if sync != "Synced" || health != "Healthy" {
            unhealthy.push(format!(
                "argocd_application={namespace}/{name} sync={sync} health={health}"
            ));
        }
    }

    (total, unhealthy)
}

fn flux_ready(value: &Value, kind: &str) -> (usize, Vec<String>) {
    let mut total = 0usize;
    let mut unhealthy = Vec::new();

    for item in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        total += 1;
        let namespace = item
            .pointer("/metadata/namespace")
            .and_then(Value::as_str)
            .unwrap_or("default");
        let name = item
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        let ready = item
            .pointer("/status/conditions")
            .and_then(Value::as_array)
            .and_then(|conditions| {
                conditions.iter().find(|condition| {
                    condition.get("type").and_then(Value::as_str) == Some("Ready")
                })
            });
        let status = ready
            .and_then(|condition| condition.get("status"))
            .and_then(Value::as_str)
            .unwrap_or("Unknown");
        let reason = ready
            .and_then(|condition| condition.get("reason"))
            .and_then(Value::as_str)
            .unwrap_or("Unknown");

        if status != "True" {
            unhealthy.push(format!(
                "flux_{kind}={namespace}/{name} ready={status} reason={reason}"
            ));
        }
    }

    (total, unhealthy)
}

fn skipped(reason: String) -> Finding {
    Finding {
        rule_id: "RT-015".to_string(),
        category: "Runtime GitOps".to_string(),
        title: "GitOps resources are reconciled and healthy".to_string(),
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

    let mut detected = 0usize;
    let mut unhealthy = Vec::new();
    let mut providers = Vec::new();

    if let Ok(value) = kubectl_json(context, "applications.argoproj.io") {
        let (total, findings) = argo_findings(&value);
        if total > 0 {
            detected += total;
            providers.push(format!("argocd={total}"));
            unhealthy.extend(findings);
        }
    }

    if let Ok(value) = kubectl_json(context, "kustomizations.kustomize.toolkit.fluxcd.io") {
        let (total, findings) = flux_ready(&value, "kustomization");
        if total > 0 {
            detected += total;
            providers.push(format!("flux_kustomizations={total}"));
            unhealthy.extend(findings);
        }
    }

    if let Ok(value) = kubectl_json(context, "helmreleases.helm.toolkit.fluxcd.io") {
        let (total, findings) = flux_ready(&value, "helmrelease");
        if total > 0 {
            detected += total;
            providers.push(format!("flux_helmreleases={total}"));
            unhealthy.extend(findings);
        }
    }

    if detected == 0 {
        return skipped("no supported Argo CD or Flux GitOps resources detected".to_string());
    }

    if unhealthy.is_empty() {
        providers.push(format!("gitops_resources_healthy={detected}/{detected}"));
    }

    Finding {
        rule_id: "RT-015".to_string(),
        category: "Runtime GitOps".to_string(),
        title: "GitOps resources are reconciled and healthy".to_string(),
        status: if unhealthy.is_empty() { "PASS" } else { "FAIL" },
        score: if unhealthy.is_empty() { 10.0 } else { 0.0 },
        weight: 10.0,
        evidence: if unhealthy.is_empty() { providers } else { unhealthy },
        remediation: "Reconcile out-of-sync or unhealthy GitOps resources and resolve controller, source, manifest, dependency, or cluster drift errors."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::{argo_findings, flux_ready};
    use serde_json::json;

    #[test]
    fn detects_argocd_drift_or_unhealthy_application() {
        let value = json!({
            "items": [
                {"metadata": {"namespace": "argocd", "name": "healthy"}, "status": {"sync": {"status": "Synced"}, "health": {"status": "Healthy"}}},
                {"metadata": {"namespace": "argocd", "name": "drifted"}, "status": {"sync": {"status": "OutOfSync"}, "health": {"status": "Healthy"}}}
            ]
        });
        let (total, unhealthy) = argo_findings(&value);
        assert_eq!(total, 2);
        assert_eq!(unhealthy.len(), 1);
        assert!(unhealthy[0].contains("OutOfSync"));
    }

    #[test]
    fn detects_flux_not_ready_condition() {
        let value = json!({
            "items": [{
                "metadata": {"namespace": "flux-system", "name": "apps"},
                "status": {"conditions": [{"type": "Ready", "status": "False", "reason": "ReconciliationFailed"}]}
            }]
        });
        let (total, unhealthy) = flux_ready(&value, "kustomization");
        assert_eq!(total, 1);
        assert_eq!(unhealthy.len(), 1);
        assert!(unhealthy[0].contains("ReconciliationFailed"));
    }
}
