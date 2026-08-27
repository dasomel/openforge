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
        rule_id: "RT-012".to_string(),
        category: "Runtime Reliability".to_string(),
        title: "Managed certificates have safe remaining lifetime".to_string(),
        status: "SKIP",
        score: 0.0,
        weight: 0.0,
        evidence: vec![reason],
        remediation: String::new(),
    }
}

fn certificate_findings(value: &Value, now: DateTime<Utc>) -> (usize, Vec<String>) {
    let mut total = 0usize;
    let mut risky = Vec::new();

    for item in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let namespace = item
            .pointer("/metadata/namespace")
            .and_then(Value::as_str)
            .unwrap_or("default");
        let name = item
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        let Some(not_after) = item.pointer("/status/notAfter").and_then(Value::as_str) else {
            continue;
        };
        let Ok(expiry) = DateTime::parse_from_rfc3339(not_after) else {
            risky.push(format!("{namespace}/{name} invalid_notAfter={not_after}"));
            total += 1;
            continue;
        };

        total += 1;
        let remaining = expiry.with_timezone(&Utc) - now;
        let days = remaining.num_days();
        if days < 30 {
            risky.push(format!(
                "{namespace}/{name} expires_in_days={days} notAfter={not_after}"
            ));
        }
    }

    (total, risky)
}

pub(crate) fn finding(enabled: bool, context: Option<&str>, namespace: Option<&str>) -> Finding {
    if !enabled {
        return skipped("runtime assessment disabled; use --runtime".to_string());
    }

    let value = match kubectl_json(context, namespace, &["get", "certificates.cert-manager.io"]) {
        Ok(value) => value,
        Err(error) => return skipped(format!("cert-manager Certificate API unavailable: {error}")),
    };

    let (total, risky) = certificate_findings(&value, Utc::now());
    if total == 0 {
        return skipped(
            "no cert-manager Certificate resources with status.notAfter found".to_string(),
        );
    }

    Finding {
        rule_id: "RT-012".to_string(),
        category: "Runtime Reliability".to_string(),
        title: "Managed certificates have safe remaining lifetime".to_string(),
        status: if risky.is_empty() { "PASS" } else { "FAIL" },
        score: if risky.is_empty() { 8.0 } else { 0.0 },
        weight: 8.0,
        evidence: if risky.is_empty() {
            vec![format!("certificates_checked={total} threshold_days=30")]
        } else {
            risky
        },
        remediation: "Renew or replace certificates expiring within 30 days and verify automated renewal readiness."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::certificate_findings;
    use chrono::{TimeZone, Utc};
    use serde_json::json;

    #[test]
    fn reports_certificates_expiring_within_threshold() {
        let value = json!({
            "items": [
                {"metadata": {"namespace": "prod", "name": "soon"}, "status": {"notAfter": "2026-09-10T00:00:00Z"}},
                {"metadata": {"namespace": "prod", "name": "later"}, "status": {"notAfter": "2026-12-01T00:00:00Z"}}
            ]
        });
        let now = Utc.with_ymd_and_hms(2026, 8, 27, 0, 0, 0).unwrap();
        let (total, risky) = certificate_findings(&value, now);
        assert_eq!(total, 2);
        assert_eq!(risky.len(), 1);
        assert!(risky[0].contains("prod/soon"));
    }
}
