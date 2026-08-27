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

fn skipped(id: &str, category: &str, title: &str, reason: String) -> Finding {
    Finding {
        rule_id: id.to_string(),
        category: category.to_string(),
        title: title.to_string(),
        status: "SKIP",
        score: 0.0,
        weight: 0.0,
        evidence: vec![reason],
        remediation: String::new(),
    }
}

fn namespaced_name(item: &Value) -> String {
    let namespace = item
        .pointer("/metadata/namespace")
        .and_then(Value::as_str)
        .unwrap_or("default");
    let name = item
        .pointer("/metadata/name")
        .and_then(Value::as_str)
        .unwrap_or("unknown");
    format!("{namespace}/{name}")
}

fn unschedulable_pods(value: &Value) -> (usize, Vec<String>) {
    let mut total = 0usize;
    let mut unhealthy = Vec::new();

    for pod in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        total += 1;
        let phase = pod
            .pointer("/status/phase")
            .and_then(Value::as_str)
            .unwrap_or("Unknown");
        let condition = pod
            .pointer("/status/conditions")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
            .find(|condition| {
                condition.get("type").and_then(Value::as_str) == Some("PodScheduled")
                    && condition.get("status").and_then(Value::as_str) == Some("False")
                    && condition.get("reason").and_then(Value::as_str) == Some("Unschedulable")
            });

        if phase == "Pending" {
            if let Some(condition) = condition {
                let reason = condition
                    .get("reason")
                    .and_then(Value::as_str)
                    .unwrap_or("Unschedulable");
                let message = condition
                    .get("message")
                    .and_then(Value::as_str)
                    .unwrap_or("<none>");
                unhealthy.push(format!(
                    "pod={} phase=Pending reason={reason} message={message}",
                    namespaced_name(pod)
                ));
            }
        }
    }

    (total, unhealthy)
}

fn node_pressure(value: &Value) -> (usize, Vec<String>) {
    const PRESSURE_TYPES: [&str; 4] = [
        "MemoryPressure",
        "DiskPressure",
        "PIDPressure",
        "NetworkUnavailable",
    ];

    let mut total = 0usize;
    let mut unhealthy = Vec::new();
    for node in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        total += 1;
        let name = node
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        for condition in node
            .pointer("/status/conditions")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
        {
            let kind = condition.get("type").and_then(Value::as_str).unwrap_or("");
            let active = condition.get("status").and_then(Value::as_str) == Some("True");
            if PRESSURE_TYPES.contains(&kind) && active {
                let reason = condition
                    .get("reason")
                    .and_then(Value::as_str)
                    .unwrap_or("<none>");
                unhealthy.push(format!("node={name} condition={kind} reason={reason}"));
            }
        }
    }
    (total, unhealthy)
}

fn has_topology_protection(workload: &Value) -> bool {
    let template_spec = workload.pointer("/spec/template/spec");
    let spread = template_spec
        .and_then(|spec| spec.get("topologySpreadConstraints"))
        .and_then(Value::as_array)
        .is_some_and(|items| !items.is_empty());
    let required_anti_affinity = template_spec
        .and_then(|spec| spec.pointer("/affinity/podAntiAffinity/requiredDuringSchedulingIgnoredDuringExecution"))
        .and_then(Value::as_array)
        .is_some_and(|items| !items.is_empty());
    let preferred_anti_affinity = template_spec
        .and_then(|spec| spec.pointer("/affinity/podAntiAffinity/preferredDuringSchedulingIgnoredDuringExecution"))
        .and_then(Value::as_array)
        .is_some_and(|items| !items.is_empty());

    spread || required_anti_affinity || preferred_anti_affinity
}

fn topology_coverage(value: &Value) -> (usize, usize, Vec<String>) {
    let mut total = 0usize;
    let mut covered = 0usize;
    let mut missing = Vec::new();

    for workload in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let replicas = workload
            .pointer("/spec/replicas")
            .and_then(Value::as_u64)
            .unwrap_or(1);
        if replicas < 2 {
            continue;
        }
        total += 1;
        if has_topology_protection(workload) {
            covered += 1;
        } else {
            let kind = workload
                .get("kind")
                .and_then(Value::as_str)
                .unwrap_or("Workload");
            missing.push(format!(
                "workload={}/{} replicas={replicas} topology_protection=missing",
                kind,
                namespaced_name(workload)
            ));
        }
    }

    (total, covered, missing)
}

fn scheduling_finding(
    enabled: bool,
    context: Option<&str>,
    namespace: Option<&str>,
) -> Finding {
    let title = "No Pods are blocked by scheduler constraints";
    if !enabled {
        return skipped(
            "RT-022",
            "Runtime Scheduling",
            title,
            "runtime assessment disabled; use --runtime".to_string(),
        );
    }
    let value = match kubectl_json(context, namespace, &["get", "pods"]) {
        Ok(value) => value,
        Err(error) => return skipped("RT-022", "Runtime Scheduling", title, error),
    };
    let (total, unhealthy) = unschedulable_pods(&value);
    if total == 0 {
        return skipped(
            "RT-022",
            "Runtime Scheduling",
            title,
            "no Pods found in assessment scope".to_string(),
        );
    }

    Finding {
        rule_id: "RT-022".to_string(),
        category: "Runtime Scheduling".to_string(),
        title: title.to_string(),
        status: if unhealthy.is_empty() { "PASS" } else { "FAIL" },
        score: if unhealthy.is_empty() { 8.0 } else { 0.0 },
        weight: 8.0,
        evidence: if unhealthy.is_empty() {
            vec![format!("pods_checked={total} unschedulable=0")]
        } else {
            unhealthy
        },
        remediation: "Resolve scheduler constraints such as insufficient resources, taints/tolerations, affinity, topology, PVC binding, or node selectors that keep Pods Pending."
            .to_string(),
    }
}

fn pressure_finding(enabled: bool, context: Option<&str>) -> Finding {
    let title = "Nodes report no active resource pressure conditions";
    if !enabled {
        return skipped(
            "RT-023",
            "Runtime Capacity",
            title,
            "runtime assessment disabled; use --runtime".to_string(),
        );
    }
    let value = match kubectl_json(context, None, &["get", "nodes"]) {
        Ok(value) => value,
        Err(error) => return skipped("RT-023", "Runtime Capacity", title, error),
    };
    let (total, unhealthy) = node_pressure(&value);
    if total == 0 {
        return skipped(
            "RT-023",
            "Runtime Capacity",
            title,
            "no Nodes found".to_string(),
        );
    }

    Finding {
        rule_id: "RT-023".to_string(),
        category: "Runtime Capacity".to_string(),
        title: title.to_string(),
        status: if unhealthy.is_empty() { "PASS" } else { "FAIL" },
        score: if unhealthy.is_empty() { 8.0 } else { 0.0 },
        weight: 8.0,
        evidence: if unhealthy.is_empty() {
            vec![format!("nodes_checked={total} active_pressure_conditions=0")]
        } else {
            unhealthy
        },
        remediation: "Restore node capacity and health for active MemoryPressure, DiskPressure, PIDPressure, or NetworkUnavailable conditions before they cause eviction or scheduling failures."
            .to_string(),
    }
}

fn topology_finding(
    enabled: bool,
    context: Option<&str>,
    namespace: Option<&str>,
) -> Finding {
    let title = "Replicated workloads declare topology distribution protection";
    if !enabled {
        return skipped(
            "RT-024",
            "Runtime Availability",
            title,
            "runtime assessment disabled; use --runtime".to_string(),
        );
    }
    let value = match kubectl_json(context, namespace, &["get", "deployments,statefulsets"]) {
        Ok(value) => value,
        Err(error) => return skipped("RT-024", "Runtime Availability", title, error),
    };
    let (total, covered, mut evidence) = topology_coverage(&value);
    if total == 0 {
        return skipped(
            "RT-024",
            "Runtime Availability",
            title,
            "no replicated Deployment or StatefulSet workloads found".to_string(),
        );
    }

    let ratio = covered as f64 / total as f64;
    evidence.insert(
        0,
        format!(
            "topology_protected={covered}/{total} coverage_percent={:.1}",
            ratio * 100.0
        ),
    );

    Finding {
        rule_id: "RT-024".to_string(),
        category: "Runtime Availability".to_string(),
        title: title.to_string(),
        status: if covered == total { "PASS" } else { "FAIL" },
        score: (ratio * 10.0 * 10.0).round() / 10.0,
        weight: 10.0,
        evidence,
        remediation: "Add topologySpreadConstraints or Pod anti-affinity to replicated workloads so replicas are distributed across appropriate failure domains."
            .to_string(),
    }
}

pub(crate) fn findings(
    enabled: bool,
    context: Option<&str>,
    namespace: Option<&str>,
) -> Vec<Finding> {
    vec![
        scheduling_finding(enabled, context, namespace),
        pressure_finding(enabled, context),
        topology_finding(enabled, context, namespace),
    ]
}

#[cfg(test)]
mod tests {
    use super::{node_pressure, topology_coverage, unschedulable_pods};
    use serde_json::json;

    #[test]
    fn detects_pending_unschedulable_pods() {
        let value = json!({"items": [
            {"metadata": {"namespace": "apps", "name": "ok"}, "status": {"phase": "Running"}},
            {"metadata": {"namespace": "apps", "name": "blocked"}, "status": {
                "phase": "Pending",
                "conditions": [{"type": "PodScheduled", "status": "False", "reason": "Unschedulable", "message": "0/2 nodes available"}]
            }}
        ]});
        let (total, unhealthy) = unschedulable_pods(&value);
        assert_eq!(total, 2);
        assert_eq!(unhealthy.len(), 1);
        assert!(unhealthy[0].contains("apps/blocked"));
    }

    #[test]
    fn detects_active_node_pressure_only() {
        let value = json!({"items": [{
            "metadata": {"name": "worker-a"},
            "status": {"conditions": [
                {"type": "MemoryPressure", "status": "False"},
                {"type": "DiskPressure", "status": "True", "reason": "KubeletHasDiskPressure"}
            ]}
        }]});
        let (total, unhealthy) = node_pressure(&value);
        assert_eq!(total, 1);
        assert_eq!(unhealthy.len(), 1);
        assert!(unhealthy[0].contains("DiskPressure"));
    }

    #[test]
    fn calculates_topology_coverage_for_replicated_workloads() {
        let value = json!({"items": [
            {"kind": "Deployment", "metadata": {"namespace": "apps", "name": "api"}, "spec": {
                "replicas": 3,
                "template": {"spec": {"topologySpreadConstraints": [{"topologyKey": "kubernetes.io/hostname"}]}}
            }},
            {"kind": "StatefulSet", "metadata": {"namespace": "apps", "name": "db"}, "spec": {
                "replicas": 2,
                "template": {"spec": {}}
            }},
            {"kind": "Deployment", "metadata": {"namespace": "apps", "name": "single"}, "spec": {
                "replicas": 1,
                "template": {"spec": {}}
            }}
        ]});
        let (total, covered, missing) = topology_coverage(&value);
        assert_eq!(total, 2);
        assert_eq!(covered, 1);
        assert_eq!(missing.len(), 1);
        assert!(missing[0].contains("apps/db"));
    }
}
