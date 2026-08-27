use crate::Finding;
use serde_json::{Map, Value};
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

fn finding(
    id: &str,
    category: &str,
    title: &str,
    passed: bool,
    weight: f64,
    evidence: Vec<String>,
    remediation: &str,
) -> Finding {
    Finding {
        rule_id: id.to_string(),
        category: category.to_string(),
        title: title.to_string(),
        status: if passed { "PASS" } else { "FAIL" },
        score: if passed { weight } else { 0.0 },
        weight,
        evidence,
        remediation: remediation.to_string(),
    }
}

fn coverage_finding(
    id: &str,
    category: &str,
    title: &str,
    covered: usize,
    total: usize,
    weight: f64,
    mut evidence: Vec<String>,
    remediation: &str,
) -> Finding {
    if total == 0 {
        return skipped(
            id,
            category,
            title,
            "no applicable workloads found".to_string(),
        );
    }

    let coverage = covered as f64 / total as f64;
    evidence.insert(
        0,
        format!(
            "coverage={:.1}% ({covered}/{total})",
            coverage * 100.0
        ),
    );

    Finding {
        rule_id: id.to_string(),
        category: category.to_string(),
        title: title.to_string(),
        status: if covered == total { "PASS" } else { "FAIL" },
        score: (weight * coverage * 10.0).round() / 10.0,
        weight,
        evidence,
        remediation: remediation.to_string(),
    }
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

fn object_name(item: &Value) -> String {
    let namespace = item
        .pointer("/metadata/namespace")
        .and_then(Value::as_str)
        .unwrap_or("cluster");
    let name = item
        .pointer("/metadata/name")
        .and_then(Value::as_str)
        .unwrap_or("unknown");
    format!("{namespace}/{name}")
}

fn nodes_ready(context: Option<&str>) -> Finding {
    let value = match kubectl_json(context, None, &["get", "nodes"]) {
        Ok(value) => value,
        Err(error) => {
            return skipped(
                "RT-001",
                "Runtime Availability",
                "All Kubernetes nodes are Ready",
                error,
            );
        }
    };

    let mut not_ready = Vec::new();
    let mut total = 0usize;
    for item in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        total += 1;
        let ready = item
            .pointer("/status/conditions")
            .and_then(Value::as_array)
            .is_some_and(|conditions| {
                conditions.iter().any(|condition| {
                    condition.get("type").and_then(Value::as_str) == Some("Ready")
                        && condition.get("status").and_then(Value::as_str) == Some("True")
                })
            });
        if !ready {
            not_ready.push(object_name(item));
        }
    }

    finding(
        "RT-001",
        "Runtime Availability",
        "All Kubernetes nodes are Ready",
        total > 0 && not_ready.is_empty(),
        12.0,
        if not_ready.is_empty() {
            vec![format!("ready_nodes={total}")]
        } else {
            not_ready
        },
        "Restore non-Ready nodes before treating the platform as production-ready.",
    )
}

fn workloads_available(context: Option<&str>, namespace: Option<&str>) -> Finding {
    let value = match kubectl_json(
        context,
        namespace,
        &["get", "deployments,statefulsets,daemonsets"],
    ) {
        Ok(value) => value,
        Err(error) => {
            return skipped(
                "RT-002",
                "Runtime Availability",
                "Workloads meet desired availability",
                error,
            );
        }
    };

    let mut failures = Vec::new();
    let mut total = 0usize;
    for item in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        total += 1;
        let kind = item.get("kind").and_then(Value::as_str).unwrap_or("");
        let desired = match kind {
            "DaemonSet" => item
                .pointer("/status/desiredNumberScheduled")
                .and_then(Value::as_u64)
                .unwrap_or(0),
            _ => item
                .pointer("/spec/replicas")
                .and_then(Value::as_u64)
                .unwrap_or(1),
        };
        let available = match kind {
            "StatefulSet" => item
                .pointer("/status/readyReplicas")
                .and_then(Value::as_u64)
                .unwrap_or(0),
            "DaemonSet" => item
                .pointer("/status/numberAvailable")
                .and_then(Value::as_u64)
                .unwrap_or(0),
            _ => item
                .pointer("/status/availableReplicas")
                .and_then(Value::as_u64)
                .unwrap_or(0),
        };
        if available < desired {
            failures.push(format!("{} {available}/{desired}", object_name(item)));
        }
    }

    finding(
        "RT-002",
        "Runtime Availability",
        "Workloads meet desired availability",
        total > 0 && failures.is_empty(),
        14.0,
        if failures.is_empty() {
            vec![format!("healthy_workloads={total}")]
        } else {
            failures
        },
        "Investigate unavailable replicas, scheduling failures and unhealthy pods.",
    )
}

fn workload_policy_checks(context: Option<&str>, namespace: Option<&str>) -> Vec<Finding> {
    let value = match kubectl_json(
        context,
        namespace,
        &["get", "deployments,statefulsets,daemonsets"],
    ) {
        Ok(value) => value,
        Err(error) => {
            return vec![
                skipped(
                    "RT-003",
                    "Runtime Reliability",
                    "Containers define health probes",
                    error.clone(),
                ),
                skipped(
                    "RT-004",
                    "Runtime Operations",
                    "Containers define requests and limits",
                    error,
                ),
            ];
        }
    };

    let mut missing_probes = Vec::new();
    let mut missing_resources = Vec::new();
    let mut containers = 0usize;

    for item in value
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let workload = object_name(item);
        if let Some(items) = item
            .pointer("/spec/template/spec/containers")
            .and_then(Value::as_array)
        {
            for container in items {
                containers += 1;
                let name = container
                    .get("name")
                    .and_then(Value::as_str)
                    .unwrap_or("unknown");
                let has_probe = container.get("readinessProbe").is_some()
                    || container.get("livenessProbe").is_some()
                    || container.get("startupProbe").is_some();
                if !has_probe {
                    missing_probes.push(format!("{workload}:{name}"));
                }
                let requests = container
                    .pointer("/resources/requests")
                    .and_then(Value::as_object)
                    .is_some_and(|map| !map.is_empty());
                let limits = container
                    .pointer("/resources/limits")
                    .and_then(Value::as_object)
                    .is_some_and(|map| !map.is_empty());
                if !(requests && limits) {
                    missing_resources.push(format!("{workload}:{name}"));
                }
            }
        }
    }

    vec![
        finding(
            "RT-003",
            "Runtime Reliability",
            "Containers define health probes",
            containers > 0 && missing_probes.is_empty(),
            10.0,
            if missing_probes.is_empty() {
                vec![format!("containers_with_probes={containers}")]
            } else {
                missing_probes
            },
            "Define readiness/liveness/startup probes appropriate to each workload.",
        ),
        finding(
            "RT-004",
            "Runtime Operations",
            "Containers define requests and limits",
            containers > 0 && missing_resources.is_empty(),
            10.0,
            if missing_resources.is_empty() {
                vec![format!("containers_with_resources={containers}")]
            } else {
                missing_resources
            },
            "Define CPU/memory requests and limits for workload containers.",
        ),
    ]
}

fn labels(item: &Value, pointer: &str) -> Map<String, Value> {
    item.pointer(pointer)
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default()
}

fn selector_matches(selector: &Value, workload_labels: &Map<String, Value>) -> bool {
    let match_labels = selector
        .get("matchLabels")
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default();

    if !match_labels.iter().all(|(key, expected)| {
        workload_labels
            .get(key)
            .is_some_and(|actual| actual == expected)
    }) {
        return false;
    }

    selector
        .get("matchExpressions")
        .and_then(Value::as_array)
        .is_none_or(|expressions| {
            expressions.iter().all(|expression| {
                let Some(key) = expression.get("key").and_then(Value::as_str) else {
                    return false;
                };
                let operator = expression
                    .get("operator")
                    .and_then(Value::as_str)
                    .unwrap_or("");
                let values = expression
                    .get("values")
                    .and_then(Value::as_array)
                    .cloned()
                    .unwrap_or_default();
                let actual = workload_labels.get(key);

                match operator {
                    "In" => actual.is_some_and(|actual| values.iter().any(|value| value == actual)),
                    "NotIn" => actual.is_some_and(|actual| values.iter().all(|value| value != actual)),
                    "Exists" => actual.is_some(),
                    "DoesNotExist" => actual.is_none(),
                    _ => false,
                }
            })
        })
}

fn workload_items(
    context: Option<&str>,
    namespace: Option<&str>,
) -> Result<Vec<Value>, String> {
    let value = kubectl_json(
        context,
        namespace,
        &["get", "deployments,statefulsets,daemonsets"],
    )?;
    Ok(value
        .get("items")
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default())
}

fn policy_items(
    context: Option<&str>,
    namespace: Option<&str>,
    kind: &str,
) -> Result<Vec<Value>, String> {
    let value = kubectl_json(context, namespace, &["get", kind])?;
    Ok(value
        .get("items")
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default())
}

fn pdb_coverage(context: Option<&str>, namespace: Option<&str>) -> Finding {
    let workloads = match workload_items(context, namespace) {
        Ok(items) => items,
        Err(error) => {
            return skipped(
                "RT-005",
                "Runtime Reliability",
                "PodDisruptionBudget workload coverage",
                error,
            );
        }
    };
    let policies = match policy_items(context, namespace, "poddisruptionbudgets") {
        Ok(items) => items,
        Err(error) => {
            return skipped(
                "RT-005",
                "Runtime Reliability",
                "PodDisruptionBudget workload coverage",
                error,
            );
        }
    };

    let eligible: Vec<&Value> = workloads
        .iter()
        .filter(|item| {
            item.get("kind").and_then(Value::as_str) != Some("DaemonSet")
                && item
                    .pointer("/spec/replicas")
                    .and_then(Value::as_u64)
                    .unwrap_or(1)
                    > 1
        })
        .collect();

    let mut uncovered = Vec::new();
    let mut covered = 0usize;
    for workload in &eligible {
        let namespace = workload
            .pointer("/metadata/namespace")
            .and_then(Value::as_str)
            .unwrap_or("default");
        let workload_labels = labels(workload, "/spec/template/metadata/labels");
        let matched = policies.iter().any(|policy| {
            policy
                .pointer("/metadata/namespace")
                .and_then(Value::as_str)
                .unwrap_or("default")
                == namespace
                && policy
                    .pointer("/spec/selector")
                    .is_some_and(|selector| selector_matches(selector, &workload_labels))
        });
        if matched {
            covered += 1;
        } else {
            uncovered.push(object_name(workload));
        }
    }

    coverage_finding(
        "RT-005",
        "Runtime Reliability",
        "PodDisruptionBudget workload coverage",
        covered,
        eligible.len(),
        8.0,
        uncovered,
        "Add or adjust PodDisruptionBudget selectors for replicated workloads that require disruption protection.",
    )
}

fn network_policy_coverage(context: Option<&str>, namespace: Option<&str>) -> Finding {
    let workloads = match workload_items(context, namespace) {
        Ok(items) => items,
        Err(error) => {
            return skipped(
                "RT-006",
                "Runtime Security",
                "NetworkPolicy workload coverage",
                error,
            );
        }
    };
    let policies = match policy_items(context, namespace, "networkpolicies") {
        Ok(items) => items,
        Err(error) => {
            return skipped(
                "RT-006",
                "Runtime Security",
                "NetworkPolicy workload coverage",
                error,
            );
        }
    };

    let mut uncovered = Vec::new();
    let mut covered = 0usize;
    for workload in &workloads {
        let namespace = workload
            .pointer("/metadata/namespace")
            .and_then(Value::as_str)
            .unwrap_or("default");
        let workload_labels = labels(workload, "/spec/template/metadata/labels");
        let matched = policies.iter().any(|policy| {
            policy
                .pointer("/metadata/namespace")
                .and_then(Value::as_str)
                .unwrap_or("default")
                == namespace
                && policy
                    .pointer("/spec/podSelector")
                    .is_some_and(|selector| selector_matches(selector, &workload_labels))
        });
        if matched {
            covered += 1;
        } else {
            uncovered.push(object_name(workload));
        }
    }

    coverage_finding(
        "RT-006",
        "Runtime Security",
        "NetworkPolicy workload coverage",
        covered,
        workloads.len(),
        8.0,
        uncovered,
        "Add or adjust NetworkPolicy pod selectors for workloads that require network isolation.",
    )
}

pub(crate) fn findings(
    enabled: bool,
    context: Option<&str>,
    namespace: Option<&str>,
) -> Vec<Finding> {
    if !enabled {
        return vec![skipped(
            "RT-000",
            "Runtime",
            "Kubernetes runtime evidence",
            "runtime assessment disabled; use --runtime".to_string(),
        )];
    }

    let mut findings = vec![
        nodes_ready(context),
        workloads_available(context, namespace),
    ];
    findings.extend(workload_policy_checks(context, namespace));
    findings.push(pdb_coverage(context, namespace));
    findings.push(network_policy_coverage(context, namespace));
    findings
}
