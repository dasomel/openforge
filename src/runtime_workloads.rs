use crate::Finding;
use serde_json::Value;
use std::process::Command;

mod previous {
    include!("runtime_autoscaling.rs");
}

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

fn skipped(id: &str, title: &str, reason: String) -> Finding {
    Finding {
        rule_id: id.into(),
        category: "Runtime Workload Health".into(),
        title: title.into(),
        status: "SKIP",
        score: 0.0,
        weight: 0.0,
        evidence: vec![reason],
        remediation: String::new(),
    }
}

fn weighted(
    id: &str,
    title: &str,
    ok: usize,
    total: usize,
    mut evidence: Vec<String>,
    remediation: &str,
) -> Finding {
    if total == 0 {
        return skipped(id, title, "no applicable resources detected".into());
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
        category: "Runtime Workload Health".into(),
        title: title.into(),
        status: if ok == total { "PASS" } else { "FAIL" },
        score: (WEIGHT * coverage * 10.0).round() / 10.0,
        weight: WEIGHT,
        evidence,
        remediation: remediation.into(),
    }
}

fn deployment_revisions(items: &[Value]) -> Finding {
    let mut ok = 0;
    let mut evidence = Vec::new();
    for d in items {
        let generation = d
            .pointer("/metadata/generation")
            .and_then(Value::as_u64)
            .unwrap_or(0);
        let observed = d
            .pointer("/status/observedGeneration")
            .and_then(Value::as_u64)
            .unwrap_or(0);
        let revision = d
            .pointer("/metadata/annotations/deployment.kubernetes.io~1revision")
            .and_then(Value::as_str);
        if observed >= generation && revision.is_some() {
            ok += 1;
        } else {
            evidence.push(format!(
                "deployment={} generation={} observed_generation={} revision={}",
                identity(d),
                generation,
                observed,
                revision.unwrap_or("missing")
            ));
        }
    }
    weighted(
        "RT-034",
        "Deployments expose an observed rollout revision",
        ok,
        items.len(),
        evidence,
        "Wait for the Deployment controller to observe the latest generation and preserve rollout revision metadata for rollback diagnostics.",
    )
}

fn evaluate_statefulsets(items: &[Value]) -> Finding {
    let mut ok = 0;
    let mut evidence = Vec::new();
    for s in items {
        let desired = s
            .pointer("/spec/replicas")
            .and_then(Value::as_u64)
            .unwrap_or(1);
        let ready = s
            .pointer("/status/readyReplicas")
            .and_then(Value::as_u64)
            .unwrap_or(0);
        let current = s.pointer("/status/currentRevision").and_then(Value::as_str);
        let update = s.pointer("/status/updateRevision").and_then(Value::as_str);
        let observed = s
            .pointer("/status/observedGeneration")
            .and_then(Value::as_u64)
            .unwrap_or(0);
        let generation = s
            .pointer("/metadata/generation")
            .and_then(Value::as_u64)
            .unwrap_or(0);
        if ready >= desired && current.is_some() && current == update && observed >= generation {
            ok += 1;
        } else {
            evidence.push(format!(
                "statefulset={} ready={}/{} current_revision={} update_revision={} generation={}/{}",
                identity(s),
                ready,
                desired,
                current.unwrap_or("missing"),
                update.unwrap_or("missing"),
                observed,
                generation
            ));
        }
    }
    weighted(
        "RT-035",
        "StatefulSet rollouts are converged and ready",
        ok,
        items.len(),
        evidence,
        "Investigate StatefulSets with unavailable replicas, stale controller observations, or mismatched current/update revisions.",
    )
}

fn evaluate_jobs(jobs: &[Value], cronjobs: &[Value]) -> Finding {
    let total = jobs.len() + cronjobs.len();
    let mut ok = 0;
    let mut evidence = Vec::new();
    for j in jobs {
        let failed = j
            .pointer("/status/failed")
            .and_then(Value::as_u64)
            .unwrap_or(0);
        let active = j
            .pointer("/status/active")
            .and_then(Value::as_u64)
            .unwrap_or(0);
        let completions = j
            .pointer("/spec/completions")
            .and_then(Value::as_u64)
            .unwrap_or(1);
        let succeeded = j
            .pointer("/status/succeeded")
            .and_then(Value::as_u64)
            .unwrap_or(0);
        if failed == 0 && (active > 0 || succeeded >= completions) {
            ok += 1;
        } else {
            evidence.push(format!(
                "job={} active={} succeeded={}/{} failed={}",
                identity(j),
                active,
                succeeded,
                completions,
                failed
            ));
        }
    }
    for c in cronjobs {
        let suspended = c
            .pointer("/spec/suspend")
            .and_then(Value::as_bool)
            .unwrap_or(false);
        let last_schedule = c
            .pointer("/status/lastScheduleTime")
            .and_then(Value::as_str);
        let last_success = c
            .pointer("/status/lastSuccessfulTime")
            .and_then(Value::as_str);
        if suspended || last_success.is_some() || last_schedule.is_none() {
            ok += 1;
        } else {
            evidence.push(format!(
                "cronjob={} suspended={} last_schedule={} last_success=missing",
                identity(c),
                suspended,
                last_schedule.unwrap_or("never")
            ));
        }
    }
    weighted(
        "RT-036",
        "Jobs and CronJobs report healthy execution state",
        ok,
        total,
        evidence,
        "Investigate failed Jobs and CronJobs that have scheduled without a recorded successful execution; review pod logs, backoff limits, schedules, and dependencies.",
    )
}

fn workload_findings(
    enabled: bool,
    context: Option<&str>,
    namespace: Option<&str>,
) -> Vec<Finding> {
    let titles = [
        ("RT-034", "Deployments expose an observed rollout revision"),
        ("RT-035", "StatefulSet rollouts are converged and ready"),
        ("RT-036", "Jobs and CronJobs report healthy execution state"),
    ];
    if !enabled {
        return titles
            .into_iter()
            .map(|(id, title)| {
                skipped(
                    id,
                    title,
                    "runtime assessment disabled; use --runtime".into(),
                )
            })
            .collect();
    }
    let deployments_result = kubectl_json(context, namespace, "deployments.apps");
    let statefulsets_result = kubectl_json(context, namespace, "statefulsets.apps");
    let jobs_result = kubectl_json(context, namespace, "jobs.batch");
    let cronjobs_result = kubectl_json(context, namespace, "cronjobs.batch");
    let d = match deployments_result {
        Ok(v) => deployment_revisions(
            v.get("items")
                .and_then(Value::as_array)
                .map(Vec::as_slice)
                .unwrap_or(&[]),
        ),
        Err(e) => skipped(titles[0].0, titles[0].1, e),
    };
    let s = match statefulsets_result {
        Ok(v) => evaluate_statefulsets(
            v.get("items")
                .and_then(Value::as_array)
                .map(Vec::as_slice)
                .unwrap_or(&[]),
        ),
        Err(e) => skipped(titles[1].0, titles[1].1, e),
    };
    let j = match (jobs_result, cronjobs_result) {
        (Ok(jv), Ok(cv)) => evaluate_jobs(
            jv.get("items")
                .and_then(Value::as_array)
                .map(Vec::as_slice)
                .unwrap_or(&[]),
            cv.get("items")
                .and_then(Value::as_array)
                .map(Vec::as_slice)
                .unwrap_or(&[]),
        ),
        (Err(e), _) | (_, Err(e)) => skipped(titles[2].0, titles[2].1, e),
    };
    vec![d, s, j]
}

pub fn findings(enabled: bool, context: Option<&str>, namespace: Option<&str>) -> Vec<Finding> {
    let mut out = previous::findings(enabled, context, namespace);
    out.extend(workload_findings(enabled, context, namespace));
    out
}
