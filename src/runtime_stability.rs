use crate::Finding;
use serde_json::Value;
use std::{collections::BTreeMap, process::Command};

const POD_SATURATION_THRESHOLD: f64 = 0.90;
const NODE_SATURATION_THRESHOLD: f64 = 0.85;
const RESTART_THRESHOLD: u64 = 5;

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

fn kubectl_raw_json(context: Option<&str>, path: &str) -> Result<Value, String> {
    let mut command = Command::new("kubectl");
    if let Some(context) = context {
        command.arg("--context").arg(context);
    }
    command.args(["get", "--raw", path]);

    let output = command
        .output()
        .map_err(|error| format!("kubectl unavailable: {error}"))?;
    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).trim().to_string());
    }
    serde_json::from_slice(&output.stdout).map_err(|error| format!("invalid metrics JSON: {error}"))
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

fn parse_cpu_millicores(raw: &str) -> Option<f64> {
    if let Some(value) = raw.strip_suffix('n') {
        return value.parse::<f64>().ok().map(|value| value / 1_000_000.0);
    }
    if let Some(value) = raw.strip_suffix('u') {
        return value.parse::<f64>().ok().map(|value| value / 1_000.0);
    }
    if let Some(value) = raw.strip_suffix('m') {
        return value.parse::<f64>().ok();
    }
    raw.parse::<f64>().ok().map(|value| value * 1_000.0)
}

fn parse_memory_bytes(raw: &str) -> Option<f64> {
    const UNITS: [(&str, f64); 8] = [
        ("Ki", 1024.0),
        ("Mi", 1024.0 * 1024.0),
        ("Gi", 1024.0 * 1024.0 * 1024.0),
        ("Ti", 1024.0 * 1024.0 * 1024.0 * 1024.0),
        ("K", 1_000.0),
        ("M", 1_000_000.0),
        ("G", 1_000_000_000.0),
        ("T", 1_000_000_000_000.0),
    ];
    for (suffix, multiplier) in UNITS {
        if let Some(value) = raw.strip_suffix(suffix) {
            return value.parse::<f64>().ok().map(|value| value * multiplier);
        }
    }
    raw.parse::<f64>().ok()
}

fn terminated_reason(status: &Value) -> Option<&str> {
    status
        .pointer("/state/terminated/reason")
        .or_else(|| status.pointer("/lastState/terminated/reason"))
        .and_then(Value::as_str)
}

fn restart_issues(value: &Value) -> (usize, Vec<String>) {
    let mut checked = 0usize;
    let mut issues = Vec::new();

    for pod in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let namespace = pod
            .pointer("/metadata/namespace")
            .and_then(Value::as_str)
            .unwrap_or("default");
        let pod_name = pod
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        for field in ["containerStatuses", "initContainerStatuses"] {
            for status in pod
                .pointer(&format!("/status/{field}"))
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
            {
                checked += 1;
                let container = status
                    .get("name")
                    .and_then(Value::as_str)
                    .unwrap_or("unknown");
                let restarts = status
                    .get("restartCount")
                    .and_then(Value::as_u64)
                    .unwrap_or(0);
                let reason = terminated_reason(status).unwrap_or("");
                if restarts >= RESTART_THRESHOLD || reason == "OOMKilled" {
                    issues.push(format!(
                        "container={namespace}/{pod_name}/{container} restarts={restarts} terminated_reason={}",
                        if reason.is_empty() { "<none>" } else { reason }
                    ));
                }
            }
        }
    }
    (checked, issues)
}

fn pod_limits(value: &Value) -> BTreeMap<String, (Option<f64>, Option<f64>)> {
    let mut limits = BTreeMap::new();
    for pod in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let namespace = pod
            .pointer("/metadata/namespace")
            .and_then(Value::as_str)
            .unwrap_or("default");
        let pod_name = pod
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        for container in pod
            .pointer("/spec/containers")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
        {
            let container_name = container
                .get("name")
                .and_then(Value::as_str)
                .unwrap_or("unknown");
            let cpu = container
                .pointer("/resources/limits/cpu")
                .and_then(Value::as_str)
                .and_then(parse_cpu_millicores);
            let memory = container
                .pointer("/resources/limits/memory")
                .and_then(Value::as_str)
                .and_then(parse_memory_bytes);
            limits.insert(
                format!("{namespace}/{pod_name}/{container_name}"),
                (cpu, memory),
            );
        }
    }
    limits
}

fn pod_saturation_issues(
    pods: &Value,
    metrics: &Value,
    namespace_filter: Option<&str>,
) -> (usize, Vec<String>) {
    let limits = pod_limits(pods);
    let mut checked = 0usize;
    let mut issues = Vec::new();

    for pod in metrics
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let namespace = pod
            .pointer("/metadata/namespace")
            .and_then(Value::as_str)
            .unwrap_or("default");
        if namespace_filter.is_some_and(|filter| filter != namespace) {
            continue;
        }
        let pod_name = pod
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        for container in pod
            .get("containers")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
        {
            let container_name = container
                .get("name")
                .and_then(Value::as_str)
                .unwrap_or("unknown");
            let key = format!("{namespace}/{pod_name}/{container_name}");
            let Some((cpu_limit, memory_limit)) = limits.get(&key) else {
                continue;
            };
            if cpu_limit.is_none() && memory_limit.is_none() {
                continue;
            }
            checked += 1;

            let cpu_usage = container
                .pointer("/usage/cpu")
                .and_then(Value::as_str)
                .and_then(parse_cpu_millicores);
            let memory_usage = container
                .pointer("/usage/memory")
                .and_then(Value::as_str)
                .and_then(parse_memory_bytes);
            let cpu_ratio = cpu_usage
                .zip(*cpu_limit)
                .filter(|(_, limit)| *limit > 0.0)
                .map(|(usage, limit)| usage / limit);
            let memory_ratio = memory_usage
                .zip(*memory_limit)
                .filter(|(_, limit)| *limit > 0.0)
                .map(|(usage, limit)| usage / limit);

            if cpu_ratio.is_some_and(|ratio| ratio >= POD_SATURATION_THRESHOLD)
                || memory_ratio.is_some_and(|ratio| ratio >= POD_SATURATION_THRESHOLD)
            {
                issues.push(format!(
                    "container={key} cpu_percent={} memory_percent={} threshold_percent=90.0",
                    cpu_ratio
                        .map(|ratio| format!("{:.1}", ratio * 100.0))
                        .unwrap_or_else(|| "n/a".to_string()),
                    memory_ratio
                        .map(|ratio| format!("{:.1}", ratio * 100.0))
                        .unwrap_or_else(|| "n/a".to_string())
                ));
            }
        }
    }
    (checked, issues)
}

fn node_allocatable(value: &Value) -> BTreeMap<String, (Option<f64>, Option<f64>)> {
    let mut allocatable = BTreeMap::new();
    for node in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let name = node
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        let cpu = node
            .pointer("/status/allocatable/cpu")
            .and_then(Value::as_str)
            .and_then(parse_cpu_millicores);
        let memory = node
            .pointer("/status/allocatable/memory")
            .and_then(Value::as_str)
            .and_then(parse_memory_bytes);
        allocatable.insert(name.to_string(), (cpu, memory));
    }
    allocatable
}

fn node_saturation_issues(nodes: &Value, metrics: &Value) -> (usize, Vec<String>) {
    let allocatable = node_allocatable(nodes);
    let mut checked = 0usize;
    let mut issues = Vec::new();

    for metric in metrics
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let name = metric
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        let Some((cpu_capacity, memory_capacity)) = allocatable.get(name) else {
            continue;
        };
        if cpu_capacity.is_none() && memory_capacity.is_none() {
            continue;
        }
        checked += 1;
        let cpu_usage = metric
            .pointer("/usage/cpu")
            .and_then(Value::as_str)
            .and_then(parse_cpu_millicores);
        let memory_usage = metric
            .pointer("/usage/memory")
            .and_then(Value::as_str)
            .and_then(parse_memory_bytes);
        let cpu_ratio = cpu_usage
            .zip(*cpu_capacity)
            .filter(|(_, capacity)| *capacity > 0.0)
            .map(|(usage, capacity)| usage / capacity);
        let memory_ratio = memory_usage
            .zip(*memory_capacity)
            .filter(|(_, capacity)| *capacity > 0.0)
            .map(|(usage, capacity)| usage / capacity);

        if cpu_ratio.is_some_and(|ratio| ratio >= NODE_SATURATION_THRESHOLD)
            || memory_ratio.is_some_and(|ratio| ratio >= NODE_SATURATION_THRESHOLD)
        {
            issues.push(format!(
                "node={name} cpu_percent={} memory_percent={} threshold_percent=85.0",
                cpu_ratio
                    .map(|ratio| format!("{:.1}", ratio * 100.0))
                    .unwrap_or_else(|| "n/a".to_string()),
                memory_ratio
                    .map(|ratio| format!("{:.1}", ratio * 100.0))
                    .unwrap_or_else(|| "n/a".to_string())
            ));
        }
    }
    (checked, issues)
}

fn restart_finding(enabled: bool, context: Option<&str>, namespace: Option<&str>) -> Finding {
    let title = "Containers avoid repeated restarts and OOM termination evidence";
    if !enabled {
        return skipped(
            "RT-025",
            "Runtime Stability",
            title,
            "runtime assessment disabled; use --runtime".to_string(),
        );
    }
    let pods = match kubectl_json(context, namespace, &["get", "pods"]) {
        Ok(value) => value,
        Err(error) => return skipped("RT-025", "Runtime Stability", title, error),
    };
    let (checked, issues) = restart_issues(&pods);
    if checked == 0 {
        return skipped(
            "RT-025",
            "Runtime Stability",
            title,
            "no container status evidence found".to_string(),
        );
    }
    Finding {
        rule_id: "RT-025".to_string(),
        category: "Runtime Stability".to_string(),
        title: title.to_string(),
        status: if issues.is_empty() { "PASS" } else { "FAIL" },
        score: if issues.is_empty() { 8.0 } else { 0.0 },
        weight: 8.0,
        evidence: if issues.is_empty() {
            vec![format!(
                "containers_checked={checked} restart_threshold={RESTART_THRESHOLD} restart_or_oom_issues=0"
            )]
        } else {
            issues
        },
        remediation: "Investigate repeated container restarts and OOMKilled events; verify memory limits, application stability, probes, and dependency health."
            .to_string(),
    }
}

fn pod_saturation_finding(
    enabled: bool,
    context: Option<&str>,
    namespace: Option<&str>,
) -> Finding {
    let title = "Container CPU and memory usage stay below declared limits";
    if !enabled {
        return skipped(
            "RT-026",
            "Runtime Saturation",
            title,
            "runtime assessment disabled; use --runtime".to_string(),
        );
    }
    let pods = match kubectl_json(context, namespace, &["get", "pods"]) {
        Ok(value) => value,
        Err(error) => return skipped("RT-026", "Runtime Saturation", title, error),
    };
    let metrics = match kubectl_raw_json(context, "/apis/metrics.k8s.io/v1beta1/pods") {
        Ok(value) => value,
        Err(error) => return skipped("RT-026", "Runtime Saturation", title, error),
    };
    let (checked, issues) = pod_saturation_issues(&pods, &metrics, namespace);
    if checked == 0 {
        return skipped(
            "RT-026",
            "Runtime Saturation",
            title,
            "no container metrics with parseable resource limits found".to_string(),
        );
    }
    Finding {
        rule_id: "RT-026".to_string(),
        category: "Runtime Saturation".to_string(),
        title: title.to_string(),
        status: if issues.is_empty() { "PASS" } else { "FAIL" },
        score: if issues.is_empty() { 10.0 } else { 0.0 },
        weight: 10.0,
        evidence: if issues.is_empty() {
            vec![format!(
                "containers_checked={checked} saturation_issues=0 threshold_percent=90.0"
            )]
        } else {
            issues
        },
        remediation: "Reduce sustained CPU or memory saturation, right-size limits, or scale workloads before they reach throttling or OOM risk."
            .to_string(),
    }
}

fn node_saturation_finding(enabled: bool, context: Option<&str>) -> Finding {
    let title = "Node CPU and memory usage retain allocatable headroom";
    if !enabled {
        return skipped(
            "RT-027",
            "Runtime Capacity",
            title,
            "runtime assessment disabled; use --runtime".to_string(),
        );
    }
    let nodes = match kubectl_json(context, None, &["get", "nodes"]) {
        Ok(value) => value,
        Err(error) => return skipped("RT-027", "Runtime Capacity", title, error),
    };
    let metrics = match kubectl_raw_json(context, "/apis/metrics.k8s.io/v1beta1/nodes") {
        Ok(value) => value,
        Err(error) => return skipped("RT-027", "Runtime Capacity", title, error),
    };
    let (checked, issues) = node_saturation_issues(&nodes, &metrics);
    if checked == 0 {
        return skipped(
            "RT-027",
            "Runtime Capacity",
            title,
            "no node metrics with parseable allocatable capacity found".to_string(),
        );
    }
    Finding {
        rule_id: "RT-027".to_string(),
        category: "Runtime Capacity".to_string(),
        title: title.to_string(),
        status: if issues.is_empty() { "PASS" } else { "FAIL" },
        score: if issues.is_empty() { 10.0 } else { 0.0 },
        weight: 10.0,
        evidence: if issues.is_empty() {
            vec![format!(
                "nodes_checked={checked} saturation_issues=0 threshold_percent=85.0"
            )]
        } else {
            issues
        },
        remediation: "Restore node headroom by scaling the node pool, moving workloads, or right-sizing requests and limits before resource pressure develops."
            .to_string(),
    }
}

pub(crate) fn findings(
    enabled: bool,
    context: Option<&str>,
    namespace: Option<&str>,
) -> Vec<Finding> {
    vec![
        restart_finding(enabled, context, namespace),
        pod_saturation_finding(enabled, context, namespace),
        node_saturation_finding(enabled, context),
    ]
}

#[cfg(test)]
mod tests {
    use super::{
        node_saturation_issues, parse_cpu_millicores, parse_memory_bytes, pod_saturation_issues,
        restart_issues,
    };
    use serde_json::json;

    #[test]
    fn parses_kubernetes_resource_quantities() {
        assert_eq!(parse_cpu_millicores("500m"), Some(500.0));
        assert_eq!(parse_cpu_millicores("2"), Some(2000.0));
        assert_eq!(parse_memory_bytes("1Gi"), Some(1024.0 * 1024.0 * 1024.0));
        assert_eq!(parse_memory_bytes("512Mi"), Some(512.0 * 1024.0 * 1024.0));
    }

    #[test]
    fn detects_restart_and_oom_evidence() {
        let pods = json!({"items": [{"metadata": {"namespace": "apps", "name": "api"}, "status": {
            "containerStatuses": [{"name": "api", "restartCount": 6, "lastState": {"terminated": {"reason": "OOMKilled"}}}]
        }}]});
        let (checked, issues) = restart_issues(&pods);
        assert_eq!(checked, 1);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].contains("OOMKilled"));
    }

    #[test]
    fn detects_pod_limit_saturation() {
        let pods = json!({"items": [{"metadata": {"namespace": "apps", "name": "api"}, "spec": {
            "containers": [{"name": "api", "resources": {"limits": {"cpu": "500m", "memory": "512Mi"}}}]
        }}]});
        let metrics = json!({"items": [{"metadata": {"namespace": "apps", "name": "api"}, "containers": [
            {"name": "api", "usage": {"cpu": "475m", "memory": "256Mi"}}
        ]}]});
        let (checked, issues) = pod_saturation_issues(&pods, &metrics, None);
        assert_eq!(checked, 1);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].contains("cpu_percent=95.0"));
    }

    #[test]
    fn detects_node_allocatable_saturation() {
        let nodes = json!({"items": [{"metadata": {"name": "worker-a"}, "status": {"allocatable": {
            "cpu": "4", "memory": "8Gi"
        }}}]});
        let metrics = json!({"items": [{"metadata": {"name": "worker-a"}, "usage": {
            "cpu": "3600m", "memory": "4Gi"
        }}]});
        let (checked, issues) = node_saturation_issues(&nodes, &metrics);
        assert_eq!(checked, 1);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].contains("cpu_percent=90.0"));
    }
}
