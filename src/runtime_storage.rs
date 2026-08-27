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

fn unhealthy_pvcs(value: &Value) -> (usize, Vec<String>) {
    let mut total = 0usize;
    let mut unhealthy = Vec::new();

    for pvc in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        total += 1;
        let namespace = pvc
            .pointer("/metadata/namespace")
            .and_then(Value::as_str)
            .unwrap_or("default");
        let name = pvc
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        let phase = pvc
            .pointer("/status/phase")
            .and_then(Value::as_str)
            .unwrap_or("Unknown");
        let volume = pvc
            .pointer("/spec/volumeName")
            .and_then(Value::as_str)
            .unwrap_or("");

        if phase != "Bound" || volume.is_empty() {
            unhealthy.push(format!(
                "{namespace}/{name} phase={phase} volume={} ",
                if volume.is_empty() { "<none>" } else { volume }
            ));
        }
    }

    for item in &mut unhealthy {
        *item = item.trim_end().to_string();
    }
    (total, unhealthy)
}

fn skipped(reason: String) -> Finding {
    Finding {
        rule_id: "RT-011".to_string(),
        category: "Runtime Storage".to_string(),
        title: "PersistentVolumeClaims are healthy and bound".to_string(),
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

    let value = match kubectl_json(context, namespace, &["get", "persistentvolumeclaims"]) {
        Ok(value) => value,
        Err(error) => return skipped(error),
    };
    let (total, unhealthy) = unhealthy_pvcs(&value);
    if total == 0 {
        return skipped("no PersistentVolumeClaims found in assessment scope".to_string());
    }

    Finding {
        rule_id: "RT-011".to_string(),
        category: "Runtime Storage".to_string(),
        title: "PersistentVolumeClaims are healthy and bound".to_string(),
        status: if unhealthy.is_empty() { "PASS" } else { "FAIL" },
        score: if unhealthy.is_empty() { 8.0 } else { 0.0 },
        weight: 8.0,
        evidence: if unhealthy.is_empty() {
            vec![format!("bound_pvcs={total}")]
        } else {
            unhealthy
        },
        remediation: "Investigate Pending/Lost PVCs, StorageClass provisioning, PV availability and CSI/storage backend health."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::unhealthy_pvcs;
    use serde_json::json;

    #[test]
    fn reports_pending_and_unbound_claims() {
        let value = json!({
            "items": [
                {
                    "metadata": {"namespace": "apps", "name": "healthy"},
                    "spec": {"volumeName": "pv-1"},
                    "status": {"phase": "Bound"}
                },
                {
                    "metadata": {"namespace": "apps", "name": "pending"},
                    "spec": {},
                    "status": {"phase": "Pending"}
                }
            ]
        });

        let (total, unhealthy) = unhealthy_pvcs(&value);
        assert_eq!(total, 2);
        assert_eq!(unhealthy.len(), 1);
        assert!(unhealthy[0].contains("apps/pending"));
    }

    #[test]
    fn accepts_bound_claims() {
        let value = json!({
            "items": [{
                "metadata": {"namespace": "apps", "name": "data"},
                "spec": {"volumeName": "pv-data"},
                "status": {"phase": "Bound"}
            }]
        });

        let (total, unhealthy) = unhealthy_pvcs(&value);
        assert_eq!(total, 1);
        assert!(unhealthy.is_empty());
    }
}
