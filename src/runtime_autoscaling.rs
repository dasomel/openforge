use crate::Finding;
use serde_json::Value;
use std::process::Command;

const WEIGHT: f64 = 8.0;

fn kubectl_json(
    context: Option<&str>,
    namespace: Option<&str>,
    resource: &str,
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
    command.args(["get", resource, "-o", "json"]);
    let output = command
        .output()
        .map_err(|e| format!("kubectl unavailable: {e}"))?;
    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).trim().to_string());
    }
    serde_json::from_slice(&output.stdout).map_err(|e| format!("invalid kubectl JSON: {e}"))
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

fn identity(v: &Value) -> String {
    let ns = v
        .pointer("/metadata/namespace")
        .and_then(Value::as_str)
        .unwrap_or("default");
    let name = v
        .pointer("/metadata/name")
        .and_then(Value::as_str)
        .unwrap_or("unknown");
    format!("{ns}/{name}")
}

fn condition<'a>(v: &'a Value, kind: &str) -> Option<&'a str> {
    v.pointer("/status/conditions")
        .and_then(Value::as_array)?
        .iter()
        .find(|c| c.get("type").and_then(Value::as_str) == Some(kind))?
        .get("status")?
        .as_str()
}

fn weighted(
    id: &str,
    title: &str,
    category: &str,
    ok: usize,
    total: usize,
    mut evidence: Vec<String>,
    remediation: &str,
) -> Finding {
    if total == 0 {
        return Finding {
            rule_id: id.into(),
            category: category.into(),
            title: title.into(),
            status: "SKIP",
            score: 0.0,
            weight: 0.0,
            evidence: vec!["no applicable resources detected".into()],
            remediation: String::new(),
        };
    }
    let coverage = ok as f64 / total as f64;
    evidence.insert(
        0,
        format!(
            "coverage={ok}/{total} coverage_percent={:.1}",
            coverage * 100.0
        ),
    );
    Finding {
        rule_id: id.into(),
        category: category.into(),
        title: title.into(),
        status: if ok == total { "PASS" } else { "FAIL" },
        score: (WEIGHT * coverage * 10.0).round() / 10.0,
        weight: WEIGHT,
        evidence,
        remediation: remediation.into(),
    }
}

fn autoscaling(hpas: &[Value]) -> Vec<Finding> {
    let mut control = Vec::new();
    let mut replica = Vec::new();
    let mut headroom = Vec::new();
    let mut control_ok = 0;
    let mut replica_ok = 0;
    let mut headroom_ok = 0;
    for h in hpas {
        let able = condition(h, "AbleToScale") == Some("True");
        let active = condition(h, "ScalingActive") == Some("True");
        if able && active {
            control_ok += 1;
        } else {
            control.push(format!(
                "hpa={} able_to_scale={} scaling_active={}",
                identity(h),
                able,
                active
            ));
        }
        let current = h
            .pointer("/status/currentReplicas")
            .and_then(Value::as_u64)
            .unwrap_or(0);
        let desired = h
            .pointer("/status/desiredReplicas")
            .and_then(Value::as_u64)
            .unwrap_or(0);
        if current >= desired {
            replica_ok += 1;
        } else {
            replica.push(format!(
                "hpa={} current_replicas={} desired_replicas={}",
                identity(h),
                current,
                desired
            ));
        }
        let max = h
            .pointer("/spec/maxReplicas")
            .and_then(Value::as_u64)
            .unwrap_or(0);
        let limited = condition(h, "ScalingLimited") == Some("True");
        if !limited && current < max && desired < max {
            headroom_ok += 1;
        } else {
            headroom.push(format!(
                "hpa={} current_replicas={} desired_replicas={} max_replicas={} scaling_limited={}",
                identity(h),
                current,
                desired,
                max,
                limited
            ));
        }
    }
    vec![
        weighted(
            "RT-028",
            "HorizontalPodAutoscaler control loops are healthy",
            "Runtime Autoscaling",
            control_ok,
            hpas.len(),
            control,
            "Restore HPA metric availability and scaling control-loop health.",
        ),
        weighted(
            "RT-029",
            "HorizontalPodAutoscaler current replicas satisfy desired replicas",
            "Runtime Autoscaling",
            replica_ok,
            hpas.len(),
            replica,
            "Investigate workloads that cannot reach HPA desired replicas.",
        ),
        weighted(
            "RT-030",
            "HorizontalPodAutoscalers retain replica headroom",
            "Runtime Autoscaling",
            headroom_ok,
            hpas.len(),
            headroom,
            "Review maxReplicas, workload efficiency, cluster capacity, and sustained demand.",
        ),
    ]
}

fn rollouts(deployments: &[Value]) -> Vec<Finding> {
    let mut progress = Vec::new();
    let mut availability = Vec::new();
    let mut strategy = Vec::new();
    let mut progress_ok = 0;
    let mut availability_ok = 0;
    let mut strategy_ok = 0;
    for d in deployments {
        let stalled = condition(d, "Progressing") == Some("False")
            || d.pointer("/status/conditions")
                .and_then(Value::as_array)
                .is_some_and(|cs| {
                    cs.iter().any(|c| {
                        c.get("reason").and_then(Value::as_str) == Some("ProgressDeadlineExceeded")
                    })
                });
        if !stalled {
            progress_ok += 1;
        } else {
            progress.push(format!("deployment={} rollout_stalled=true", identity(d)));
        }
        let desired = d
            .pointer("/spec/replicas")
            .and_then(Value::as_u64)
            .unwrap_or(1);
        let available = d
            .pointer("/status/availableReplicas")
            .and_then(Value::as_u64)
            .unwrap_or(0);
        let unavailable = d
            .pointer("/status/unavailableReplicas")
            .and_then(Value::as_u64)
            .unwrap_or(desired.saturating_sub(available));
        if available >= desired && unavailable == 0 {
            availability_ok += 1;
        } else {
            availability.push(format!(
                "deployment={} available={}/{} unavailable={}",
                identity(d),
                available,
                desired,
                unavailable
            ));
        }
        let kind = d
            .pointer("/spec/strategy/type")
            .and_then(Value::as_str)
            .unwrap_or("RollingUpdate");
        let explicit = d
            .pointer("/spec/strategy/rollingUpdate/maxUnavailable")
            .is_some()
            && d.pointer("/spec/strategy/rollingUpdate/maxSurge").is_some();
        if kind == "RollingUpdate" && explicit {
            strategy_ok += 1;
        } else {
            strategy.push(format!(
                "deployment={} strategy={} explicit_budget={}",
                identity(d),
                kind,
                explicit
            ));
        }
    }
    vec![
        weighted(
            "RT-031",
            "Deployment rollouts are progressing",
            "Runtime Rollout Safety",
            progress_ok,
            deployments.len(),
            progress,
            "Investigate stalled Deployments, readiness, image pulls, scheduling, and progress deadlines.",
        ),
        weighted(
            "RT-032",
            "Deployments have no unavailable replicas",
            "Runtime Rollout Safety",
            availability_ok,
            deployments.len(),
            availability,
            "Restore unavailable replicas and verify readiness, capacity, disruption budgets, and rollout state.",
        ),
        weighted(
            "RT-033",
            "Deployments declare explicit rolling update budgets",
            "Runtime Rollout Safety",
            strategy_ok,
            deployments.len(),
            strategy,
            "Use RollingUpdate and explicitly set maxUnavailable and maxSurge according to availability requirements.",
        ),
    ]
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
            .map(|(id, t)| skipped(id, t, "runtime assessment disabled; use --runtime".into()))
            .collect();
    }
    let mut out = match kubectl_json(context, namespace, "horizontalpodautoscalers.autoscaling") {
        Ok(v) => {
            let items = v
                .get("items")
                .and_then(Value::as_array)
                .cloned()
                .unwrap_or_default();
            if items.is_empty() {
                titles
                    .into_iter()
                    .map(|(id, t)| {
                        skipped(
                            id,
                            t,
                            "no HorizontalPodAutoscaler resources detected".into(),
                        )
                    })
                    .collect()
            } else {
                autoscaling(&items)
            }
        }
        Err(e) => titles
            .into_iter()
            .map(|(id, t)| skipped(id, t, e.clone()))
            .collect(),
    };
    match kubectl_json(context, namespace, "deployments.apps") {
        Ok(v) => {
            let items = v
                .get("items")
                .and_then(Value::as_array)
                .cloned()
                .unwrap_or_default();
            out.extend(rollouts(&items));
        }
        Err(e) => {
            for (id, title) in [
                ("RT-031", "Deployment rollouts are progressing"),
                ("RT-032", "Deployments have no unavailable replicas"),
                (
                    "RT-033",
                    "Deployments declare explicit rolling update budgets",
                ),
            ] {
                out.push(Finding {
                    rule_id: id.into(),
                    category: "Runtime Rollout Safety".into(),
                    title: title.into(),
                    status: "SKIP",
                    score: 0.0,
                    weight: 0.0,
                    evidence: vec![e.clone()],
                    remediation: String::new(),
                });
            }
        }
    }
    out
}
