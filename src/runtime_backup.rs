use crate::Finding;
use chrono::{DateTime, Utc};
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

fn skipped(reason: String) -> Finding {
    Finding {
        rule_id: "RT-013".to_string(),
        category: "Runtime Recovery".to_string(),
        title: "Recent successful platform backup evidence exists".to_string(),
        status: "SKIP",
        score: 0.0,
        weight: 0.0,
        evidence: vec![reason],
        remediation: String::new(),
    }
}

fn latest_completed_backup(value: &Value) -> Option<(String, DateTime<Utc>)> {
    value
        .get("items")?
        .as_array()?
        .iter()
        .filter(|item| item.pointer("/status/phase").and_then(Value::as_str) == Some("Completed"))
        .filter_map(|item| {
            let namespace = item
                .pointer("/metadata/namespace")
                .and_then(Value::as_str)
                .unwrap_or("default");
            let name = item
                .pointer("/metadata/name")
                .and_then(Value::as_str)
                .unwrap_or("unknown");
            let timestamp = item
                .pointer("/status/completionTimestamp")
                .and_then(Value::as_str)
                .or_else(|| {
                    item.pointer("/metadata/creationTimestamp")
                        .and_then(Value::as_str)
                })?;
            let parsed = DateTime::parse_from_rfc3339(timestamp)
                .ok()?
                .with_timezone(&Utc);
            Some((format!("{namespace}/{name}"), parsed))
        })
        .max_by_key(|(_, timestamp)| *timestamp)
}

pub(crate) fn finding(enabled: bool, context: Option<&str>, namespace: Option<&str>) -> Finding {
    if !enabled {
        return skipped("runtime assessment disabled; use --runtime".to_string());
    }

    let value = match kubectl_json(context, namespace, &["get", "backups.velero.io"]) {
        Ok(value) => value,
        Err(error) => return skipped(format!("Velero Backup API unavailable: {error}")),
    };

    let Some((name, completed_at)) = latest_completed_backup(&value) else {
        let count = value
            .get("items")
            .and_then(Value::as_array)
            .map_or(0, Vec::len);
        return if count == 0 {
            skipped("no Velero Backup resources found".to_string())
        } else {
            Finding {
                rule_id: "RT-013".to_string(),
                category: "Runtime Recovery".to_string(),
                title: "Recent successful platform backup evidence exists".to_string(),
                status: "FAIL",
                score: 0.0,
                weight: 10.0,
                evidence: vec![format!("velero_backups={count} completed_backups=0")],
                remediation: "Investigate failed/incomplete Velero backups and establish a verified successful backup cycle."
                    .to_string(),
            }
        };
    };

    let age_hours = (Utc::now() - completed_at).num_hours();
    let fresh = (0..=168).contains(&age_hours);

    Finding {
        rule_id: "RT-013".to_string(),
        category: "Runtime Recovery".to_string(),
        title: "Recent successful platform backup evidence exists".to_string(),
        status: if fresh { "PASS" } else { "FAIL" },
        score: if fresh { 10.0 } else { 0.0 },
        weight: 10.0,
        evidence: vec![format!(
            "latest_completed_backup={name} age_hours={age_hours} threshold_hours=168"
        )],
        remediation: "Ensure at least one successful platform backup is completed within the defined seven-day evidence window."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::latest_completed_backup;
    use serde_json::json;

    #[test]
    fn chooses_latest_completed_velero_backup() {
        let value = json!({
            "items": [
                {"metadata": {"namespace": "velero", "name": "old"}, "status": {"phase": "Completed", "completionTimestamp": "2026-08-20T00:00:00Z"}},
                {"metadata": {"namespace": "velero", "name": "new"}, "status": {"phase": "Completed", "completionTimestamp": "2026-08-26T00:00:00Z"}},
                {"metadata": {"namespace": "velero", "name": "failed"}, "status": {"phase": "Failed", "completionTimestamp": "2026-08-27T00:00:00Z"}}
            ]
        });
        let (name, _) = latest_completed_backup(&value).expect("completed backup");
        assert_eq!(name, "velero/new");
    }
}
