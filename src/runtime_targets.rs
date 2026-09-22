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

fn kubectl_raw(context: Option<&str>, path: &str) -> Result<Value, String> {
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
    serde_json::from_slice(&output.stdout)
        .map_err(|error| format!("invalid Prometheus JSON: {error}"))
}

fn prometheus_instances(value: &Value) -> Vec<(String, String)> {
    value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|item| {
            let namespace = item.pointer("/metadata/namespace")?.as_str()?;
            let name = item.pointer("/metadata/name")?.as_str()?;
            Some((namespace.to_string(), name.to_string()))
        })
        .collect()
}

fn prometheus_pods(
    context: Option<&str>,
    namespace: &str,
    name: &str,
) -> Result<Vec<String>, String> {
    let selector = format!("prometheus={name}");
    let value = kubectl_json(context, &["get", "pods", "-n", namespace, "-l", &selector])?;
    Ok(value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|item| item.pointer("/metadata/name").and_then(Value::as_str))
        .map(str::to_string)
        .collect())
}

fn target_summary(value: &Value) -> (usize, usize, Vec<String>) {
    let mut total = 0usize;
    let mut up = 0usize;
    let mut down = Vec::new();

    for target in value
        .pointer("/data/activeTargets")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        total += 1;
        let health = target
            .get("health")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        if health == "up" {
            up += 1;
            continue;
        }
        let pool = target
            .get("scrapePool")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        let url = target
            .get("scrapeUrl")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        let error = target
            .get("lastError")
            .and_then(Value::as_str)
            .unwrap_or("");
        down.push(format!(
            "scrape_pool={pool} health={health} url={url} last_error={error}"
        ));
    }

    (total, up, down)
}

fn skipped(reason: String) -> Finding {
    Finding {
        rule_id: "RT-017".to_string(),
        category: "Runtime Observability".to_string(),
        title: "Prometheus scrape targets are healthy".to_string(),
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

    let prometheuses = match kubectl_json(
        context,
        &["get", "prometheuses.monitoring.coreos.com", "-A"],
    ) {
        Ok(value) => value,
        Err(error) => {
            return skipped(format!(
                "Prometheus Operator API unavailable; provider not detected or inaccessible: {error}"
            ));
        }
    };
    let instances = prometheus_instances(&prometheuses);
    if instances.is_empty() {
        return skipped("no Prometheus Operator Prometheus resources found".to_string());
    }

    let mut total = 0usize;
    let mut up = 0usize;
    let mut evidence = Vec::new();
    let mut seen = BTreeSet::new();
    let mut queried_pods = 0usize;

    for (namespace, name) in instances {
        let pods = match prometheus_pods(context, &namespace, &name) {
            Ok(pods) => pods,
            Err(error) => {
                evidence.push(format!(
                    "prometheus={namespace}/{name} pod_discovery_error={error}"
                ));
                continue;
            }
        };

        for pod in pods {
            let path =
                format!("/api/v1/namespaces/{namespace}/pods/http:{pod}:9090/proxy/api/v1/targets");
            let value = match kubectl_raw(context, &path) {
                Ok(value) => value,
                Err(error) => {
                    evidence.push(format!(
                        "prometheus_pod={namespace}/{pod} target_api_error={error}"
                    ));
                    continue;
                }
            };
            queried_pods += 1;
            let (pod_total, pod_up, pod_down) = target_summary(&value);
            total += pod_total;
            up += pod_up;
            for item in pod_down {
                if seen.insert(item.clone()) {
                    evidence.push(item);
                }
            }
        }
    }

    if queried_pods == 0 {
        return skipped(if evidence.is_empty() {
            "no Prometheus pods could be queried".to_string()
        } else {
            evidence.join("; ")
        });
    }
    if total == 0 {
        return skipped("Prometheus target API returned zero active targets".to_string());
    }

    let ratio = up as f64 / total as f64;
    let score = (ratio * 10.0 * 10.0).round() / 10.0;
    let healthy = up == total;
    evidence.insert(
        0,
        format!(
            "targets_up={up} targets_total={total} coverage_percent={:.1}",
            ratio * 100.0
        ),
    );

    Finding {
        rule_id: "RT-017".to_string(),
        category: "Runtime Observability".to_string(),
        title: "Prometheus scrape targets are healthy".to_string(),
        status: if healthy { "PASS" } else { "FAIL" },
        score,
        weight: 10.0,
        evidence,
        remediation: "Investigate down Prometheus targets, scrape discovery, endpoint reachability, TLS/authentication and exporter health."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::target_summary;
    use serde_json::json;

    #[test]
    fn calculates_target_health_and_reports_errors() {
        let value = json!({
            "data": {
                "activeTargets": [
                    {"scrapePool": "api", "scrapeUrl": "http://api:9100/metrics", "health": "up", "lastError": ""},
                    {"scrapePool": "db", "scrapeUrl": "http://db:9100/metrics", "health": "down", "lastError": "connection refused"}
                ]
            }
        });
        let (total, up, down) = target_summary(&value);
        assert_eq!(total, 2);
        assert_eq!(up, 1);
        assert_eq!(down.len(), 1);
        assert!(down[0].contains("connection refused"));
    }
}
