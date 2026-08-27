use crate::Finding;
use serde_json::Value;
use std::process::Command;

const CONTROL_WEIGHT: f64 = 8.0;
const REPLICA_WEIGHT: f64 = 8.0;
const HEADROOM_WEIGHT: f64 = 8.0;

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

fn skipped(id: &str, title: &str, reason: String) -> Finding {
    Finding {
        rule_id: id.to_string(),
        category: "Runtime Autoscaling".to_string(),
        title: title.to_string(),
        status: "SKIP",
        score: 0.0,
        weight: 0.0,
        evidence: vec![reason],
        remediation: String::new(),
    }
}

fn identity(hpa: &Value) -> String {
    let namespace = hpa
        .pointer("/metadata/namespace")
        .and_then(Value::as_str)
        .unwrap_or("default");
    let name = hpa
        .pointer("/metadata/name")
        .and_then(Value::as_str)
        .unwrap_or("unknown");
    format!("{namespace}/{name}")
}

fn condition_status<'a>(hpa: &'a Value, condition_type: &str) -> Option<&'a str> {
    hpa.pointer("/status/conditions")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .find(|condition| condition.get("type").and_then(Value::as_str) == Some(condition_type))
        .and_then(|condition| condition.get("status"))
        .and_then(Value::as_str)
}

fn control_loop_finding(hpas: &[Value]) -> Finding {
    let title = "HorizontalPodAutoscaler control loops are healthy";
    let mut issues = Vec::new();
    for hpa in hpas {
        for condition_type in ["AbleToScale", "ScalingActive"] {
            let status = condition_status(hpa, condition_type).unwrap_or("Missing");
            if status != "True" {
                issues.push(format!(
                    "hpa={} condition={} status={}",
                    identity(hpa),
                    condition_type,
                    status
                ));
            }
        }
    }

    Finding {
        rule_id: "RT-028".to_string(),
        category: "Runtime Autoscaling".to_string(),
        title: title.to_string(),
        status: if issues.is_empty() { "PASS" } else { "FAIL" },
        score: if issues.is_empty() { CONTROL_WEIGHT } else { 0.0 },
        weight: CONTROL_WEIGHT,
        evidence: if issues.is_empty() {
            vec![format!("hpas_checked={} unhealthy_conditions=0", hpas.len())]
        } else {
            issues
        },
        remediation: "Restore HPA metric availability and scaling control-loop health; investigate failed metrics, scale target access, and autoscaling conditions."
            .to_string(),
    }
}

fn replica_finding(hpas: &[Value]) -> Finding {
    let title = "HorizontalPodAutoscaler current replicas satisfy desired replicas";
    let mut checked = 0usize;
    let mut satisfied = 0usize;
    let mut evidence = Vec::new();

    for hpa in hpas {
        let current = hpa
            .pointer("/status/currentReplicas")
            .and_then(Value::as_u64);
        let desired = hpa
            .pointer("/status/desiredReplicas")
            .and_then(Value::as_u64);
        let Some((current, desired)) = current.zip(desired) else {
            continue;
        };
        checked += 1;
        if current >= desired {
            satisfied += 1;
        } else {
            evidence.push(format!(
                "hpa={} current_replicas={} desired_replicas={}",
                identity(hpa),
                current,
                desired
            ));
        }
    }

    if checked == 0 {
        return skipped(
            "RT-029",
            title,
            "no HPA current/desired replica status evidence found".to_string(),
        );
    }
    let coverage = satisfied as f64 / checked as f64;
    evidence.insert(
        0,
        format!(
            "replica_coverage={satisfied}/{checked} coverage_percent={:.1}",
            coverage * 100.0
        ),
    );

    Finding {
        rule_id: "RT-029".to_string(),
        category: "Runtime Autoscaling".to_string(),
        title: title.to_string(),
        status: if satisfied == checked { "PASS" } else { "FAIL" },
        score: (REPLICA_WEIGHT * coverage * 10.0).round() / 10.0,
        weight: REPLICA_WEIGHT,
        evidence,
        remediation: "Investigate workloads that cannot reach HPA desired replicas; verify scheduler capacity, quotas, image readiness, and scale-target health."
            .to_string(),
    }
}

fn headroom_finding(hpas: &[Value]) -> Finding {
    let title = "HorizontalPodAutoscalers retain replica headroom";
    let mut checked = 0usize;
    let mut healthy = 0usize;
    let mut evidence = Vec::new();

    for hpa in hpas {
        let max = hpa.pointer("/spec/maxReplicas").and_then(Value::as_u64);
        let current = hpa
            .pointer("/status/currentReplicas")
            .and_then(Value::as_u64);
        let desired = hpa
            .pointer("/status/desiredReplicas")
            .and_then(Value::as_u64);
        let Some(max) = max else {
            continue;
        };
        checked += 1;
        let limited = condition_status(hpa, "ScalingLimited") == Some("True");
        let at_limit = current.is_some_and(|value| value >= max)
            || desired.is_some_and(|value| value >= max)
            || limited;
        if at_limit {
            evidence.push(format!(
                "hpa={} current_replicas={} desired_replicas={} max_replicas={} scaling_limited={}",
                identity(hpa),
                current.map_or_else(|| "n/a".to_string(), |value| value.to_string()),
                desired.map_or_else(|| "n/a".to_string(), |value| value.to_string()),
                max,
                limited
            ));
        } else {
            healthy += 1;
        }
    }

    if checked == 0 {
        return skipped(
            "RT-030",
            title,
            "no HPA max replica evidence found".to_string(),
        );
    }
    let coverage = healthy as f64 / checked as f64;
    evidence.insert(
        0,
        format!(
            "headroom_coverage={healthy}/{checked} coverage_percent={:.1}",
            coverage * 100.0
        ),
    );

    Finding {
        rule_id: "RT-030".to_string(),
        category: "Runtime Autoscaling".to_string(),
        title: title.to_string(),
        status: if healthy == checked { "PASS" } else { "FAIL" },
        score: (HEADROOM_WEIGHT * coverage * 10.0).round() / 10.0,
        weight: HEADROOM_WEIGHT,
        evidence,
        remediation: "Restore autoscaling headroom by reviewing maxReplicas, workload efficiency, cluster capacity, and sustained demand before the HPA remains scaling-limited."
            .to_string(),
    }
}

pub fn findings(enabled: bool, context: Option<&str>, namespace: Option<&str>) -> Vec<Finding> {
    let titles = [
        (
            "RT-028",
            "HorizontalPodAutoscaler control loops are healthy",
        ),
        (
            "RT-029",
            "HorizontalPodAutoscaler current replicas satisfy desired replicas",
        ),
        ("RT-030", "HorizontalPodAutoscalers retain replica headroom"),
    ];
    if !enabled {
        return titles
            .into_iter()
            .map(|(id, title)| {
                skipped(
                    id,
                    title,
                    "runtime assessment disabled; use --runtime".to_string(),
                )
            })
            .collect();
    }

    let value = match kubectl_json(
        context,
        namespace,
        &["get", "horizontalpodautoscalers.autoscaling"],
    ) {
        Ok(value) => value,
        Err(error) => {
            return titles
                .into_iter()
                .map(|(id, title)| skipped(id, title, error.clone()))
                .collect();
        }
    };
    let hpas: Vec<Value> = value
        .get("items")
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default();
    if hpas.is_empty() {
        return titles
            .into_iter()
            .map(|(id, title)| {
                skipped(
                    id,
                    title,
                    "no HorizontalPodAutoscaler resources detected".to_string(),
                )
            })
            .collect();
    }

    vec![
        control_loop_finding(&hpas),
        replica_finding(&hpas),
        headroom_finding(&hpas),
    ]
}
