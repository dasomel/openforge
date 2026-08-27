use crate::Finding;
use serde_json::Value;
use std::process::Command;

fn kubectl_json(context: Option<&str>, args: &[&str]) -> Result<Value, String> {
    let mut command = Command::new("kubectl");
    if let Some(context) = context {
        command.arg("--context").arg(context);
    }
    command.args(args).arg("-A").arg("-o").arg("json");

    let output = command
        .output()
        .map_err(|error| format!("kubectl unavailable: {error}"))?;
    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).trim().to_string());
    }
    serde_json::from_slice(&output.stdout).map_err(|error| format!("invalid kubectl JSON: {error}"))
}

fn alertmanager_health(value: &Value) -> (usize, Vec<String>) {
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
        let desired = item
            .pointer("/spec/replicas")
            .and_then(Value::as_u64)
            .unwrap_or(1);
        let available = item
            .pointer("/status/availableReplicas")
            .and_then(Value::as_u64)
            .unwrap_or(0);

        if available < desired {
            unhealthy.push(format!(
                "alertmanager={namespace}/{name} desired={desired} available={available}"
            ));
        }
    }

    (total, unhealthy)
}

fn skipped(reason: String) -> Finding {
    Finding {
        rule_id: "RT-018".to_string(),
        category: "Runtime Observability".to_string(),
        title: "Alertmanager control plane is healthy".to_string(),
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

    let value = match kubectl_json(context, &["get", "alertmanagers.monitoring.coreos.com"]) {
        Ok(value) => value,
        Err(error) => {
            return skipped(format!(
                "Prometheus Operator Alertmanager API unavailable; provider not detected or inaccessible: {error}"
            ));
        }
    };

    let (total, unhealthy) = alertmanager_health(&value);
    if total == 0 {
        return skipped("no Prometheus Operator Alertmanager resources found".to_string());
    }

    Finding {
        rule_id: "RT-018".to_string(),
        category: "Runtime Observability".to_string(),
        title: "Alertmanager control plane is healthy".to_string(),
        status: if unhealthy.is_empty() { "PASS" } else { "FAIL" },
        score: if unhealthy.is_empty() { 8.0 } else { 0.0 },
        weight: 8.0,
        evidence: if unhealthy.is_empty() {
            vec![format!("alertmanager_instances_healthy={total}/{total}")]
        } else {
            unhealthy
        },
        remediation: "Restore Alertmanager replica availability and investigate failed scheduling, storage, configuration, or operator reconciliation."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::alertmanager_health;
    use serde_json::json;

    #[test]
    fn reports_unavailable_alertmanager_replicas() {
        let value = json!({
            "items": [
                {"metadata": {"namespace": "monitoring", "name": "main"}, "spec": {"replicas": 3}, "status": {"availableReplicas": 3}},
                {"metadata": {"namespace": "monitoring", "name": "edge"}, "spec": {"replicas": 2}, "status": {"availableReplicas": 1}}
            ]
        });

        let (total, unhealthy) = alertmanager_health(&value);
        assert_eq!(total, 2);
        assert_eq!(unhealthy.len(), 1);
        assert!(unhealthy[0].contains("monitoring/edge"));
    }

    #[test]
    fn defaults_to_one_replica() {
        let value = json!({
            "items": [
                {"metadata": {"namespace": "monitoring", "name": "single"}, "status": {"availableReplicas": 1}}
            ]
        });

        let (total, unhealthy) = alertmanager_health(&value);
        assert_eq!(total, 1);
        assert!(unhealthy.is_empty());
    }
}
