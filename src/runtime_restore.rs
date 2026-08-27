use crate::Finding;
use chrono::{DateTime, Utc};
use serde_json::Value;
use std::{env, process::Command};

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

fn assessment_now() -> DateTime<Utc> {
    env::var("OPENFORGE_NOW")
        .ok()
        .and_then(|value| DateTime::parse_from_rfc3339(&value).ok())
        .map(|value| value.with_timezone(&Utc))
        .unwrap_or_else(Utc::now)
}

fn latest_completed_restore(value: &Value) -> Option<(String, DateTime<Utc>)> {
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

fn skipped(reason: String) -> Finding {
    Finding {
        rule_id: "RT-016".to_string(),
        category: "Runtime Recovery".to_string(),
        title: "Recent successful restore verification evidence exists".to_string(),
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

    let value = match kubectl_json(context, &["get", "restores.velero.io"]) {
        Ok(value) => value,
        Err(error) => {
            return skipped(format!(
                "Velero Restore API unavailable; provider not detected or inaccessible: {error}"
            ));
        }
    };

    let count = value
        .get("items")
        .and_then(Value::as_array)
        .map_or(0, Vec::len);
    let Some((name, completed_at)) = latest_completed_restore(&value) else {
        return Finding {
            rule_id: "RT-016".to_string(),
            category: "Runtime Recovery".to_string(),
            title: "Recent successful restore verification evidence exists".to_string(),
            status: "FAIL",
            score: 0.0,
            weight: 10.0,
            evidence: vec![format!(
                "velero_restores={count} completed_restores=0 threshold_days=30"
            )],
            remediation: "Perform and verify a controlled restore drill, then retain the successful restore evidence."
                .to_string(),
        };
    };

    let age_hours = (assessment_now() - completed_at).num_hours();
    let threshold_hours = 30 * 24;
    let fresh = (0..=threshold_hours).contains(&age_hours);

    Finding {
        rule_id: "RT-016".to_string(),
        category: "Runtime Recovery".to_string(),
        title: "Recent successful restore verification evidence exists".to_string(),
        status: if fresh { "PASS" } else { "FAIL" },
        score: if fresh { 10.0 } else { 0.0 },
        weight: 10.0,
        evidence: vec![format!(
            "latest_completed_restore={name} age_hours={age_hours} threshold_hours={threshold_hours}"
        )],
        remediation: "Run a successful restore drill within the defined 30-day evidence window and verify restored workload/data integrity."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::latest_completed_restore;
    use serde_json::json;

    #[test]
    fn selects_latest_completed_restore() {
        let value = json!({
            "items": [
                {"metadata": {"namespace": "velero", "name": "old"}, "status": {"phase": "Completed", "completionTimestamp": "2026-07-20T00:00:00Z"}},
                {"metadata": {"namespace": "velero", "name": "new"}, "status": {"phase": "Completed", "completionTimestamp": "2026-08-20T00:00:00Z"}},
                {"metadata": {"namespace": "velero", "name": "failed"}, "status": {"phase": "Failed", "completionTimestamp": "2026-08-26T00:00:00Z"}}
            ]
        });

        let (name, _) = latest_completed_restore(&value).expect("completed restore");
        assert_eq!(name, "velero/new");
    }
}
