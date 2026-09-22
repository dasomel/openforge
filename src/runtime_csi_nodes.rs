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

fn csi_provisioners(storage_classes: &Value) -> BTreeSet<String> {
    storage_classes
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|item| item.pointer("/provisioner").and_then(Value::as_str))
        .filter(|provisioner| !provisioner.starts_with("kubernetes.io/"))
        .map(str::to_string)
        .collect()
}

fn ready_nodes(nodes: &Value) -> BTreeSet<String> {
    nodes
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter(|item| {
            item.pointer("/status/conditions")
                .and_then(Value::as_array)
                .is_some_and(|conditions| {
                    conditions.iter().any(|condition| {
                        condition.get("type").and_then(Value::as_str) == Some("Ready")
                            && condition.get("status").and_then(Value::as_str) == Some("True")
                    })
                })
        })
        .filter_map(|item| item.pointer("/metadata/name").and_then(Value::as_str))
        .map(str::to_string)
        .collect()
}

fn driver_node_coverage(
    csi_nodes: &Value,
    ready: &BTreeSet<String>,
    drivers: &BTreeSet<String>,
) -> (usize, usize, Vec<String>) {
    let expected = ready.len() * drivers.len();
    let mut registered = 0usize;
    let mut missing = Vec::new();

    let mut node_drivers = std::collections::BTreeMap::<String, BTreeSet<String>>::new();
    for item in csi_nodes
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let Some(node) = item.pointer("/metadata/name").and_then(Value::as_str) else {
            continue;
        };
        let registered_drivers = item
            .pointer("/spec/drivers")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
            .filter_map(|driver| driver.get("name").and_then(Value::as_str))
            .map(str::to_string)
            .collect::<BTreeSet<_>>();
        node_drivers.insert(node.to_string(), registered_drivers);
    }

    for node in ready {
        for driver in drivers {
            if node_drivers
                .get(node)
                .is_some_and(|registered_drivers| registered_drivers.contains(driver))
            {
                registered += 1;
            } else {
                missing.push(format!("node={node} missing_csi_driver={driver}"));
            }
        }
    }

    (expected, registered, missing)
}

fn skipped(reason: String) -> Finding {
    Finding {
        rule_id: "RT-020".to_string(),
        category: "Runtime Storage".to_string(),
        title: "CSI node plugins are registered across Ready nodes".to_string(),
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

    let storage_classes = match kubectl_json(context, &["get", "storageclasses.storage.k8s.io"]) {
        Ok(value) => value,
        Err(error) => return skipped(format!("StorageClass API unavailable: {error}")),
    };
    let drivers = csi_provisioners(&storage_classes);
    if drivers.is_empty() {
        return skipped("no CSI-backed StorageClass provisioners detected".to_string());
    }

    let nodes = match kubectl_json(context, &["get", "nodes"]) {
        Ok(value) => value,
        Err(error) => return skipped(format!("Node API unavailable: {error}")),
    };
    let ready = ready_nodes(&nodes);
    if ready.is_empty() {
        return skipped("no Ready nodes detected".to_string());
    }

    let csi_nodes = match kubectl_json(context, &["get", "csinodes.storage.k8s.io"]) {
        Ok(value) => value,
        Err(error) => return skipped(format!("CSINode API unavailable: {error}")),
    };

    let (expected, registered, mut missing) = driver_node_coverage(&csi_nodes, &ready, &drivers);
    if expected == 0 {
        return skipped("no CSI node-plugin coverage targets detected".to_string());
    }

    let ratio = registered as f64 / expected as f64;
    let mut evidence = vec![format!(
        "csi_node_registrations={registered}/{expected} ready_nodes={} csi_drivers={} coverage_percent={:.1}",
        ready.len(),
        drivers.len(),
        ratio * 100.0
    )];
    evidence.append(&mut missing);

    Finding {
        rule_id: "RT-020".to_string(),
        category: "Runtime Storage".to_string(),
        title: "CSI node plugins are registered across Ready nodes".to_string(),
        status: if registered == expected { "PASS" } else { "FAIL" },
        score: (ratio * 10.0 * 10.0).round() / 10.0,
        weight: 10.0,
        evidence,
        remediation: "Restore CSI node-plugin registration on Ready nodes and investigate DaemonSet scheduling, kubelet plugin registration, tolerations, node selectors, topology, and driver health."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::{driver_node_coverage, ready_nodes};
    use serde_json::json;
    use std::collections::BTreeSet;

    #[test]
    fn detects_ready_nodes_only() {
        let nodes = json!({"items": [
            {"metadata": {"name": "node-a"}, "status": {"conditions": [{"type": "Ready", "status": "True"}]}},
            {"metadata": {"name": "node-b"}, "status": {"conditions": [{"type": "Ready", "status": "False"}]}}
        ]});
        let ready = ready_nodes(&nodes);
        assert_eq!(ready.len(), 1);
        assert!(ready.contains("node-a"));
    }

    #[test]
    fn calculates_driver_registration_coverage_per_ready_node() {
        let ready = ["node-a".to_string(), "node-b".to_string()]
            .into_iter()
            .collect::<BTreeSet<_>>();
        let drivers = ["ebs.csi.aws.com".to_string(), "nfs.csi.k8s.io".to_string()]
            .into_iter()
            .collect::<BTreeSet<_>>();
        let csi_nodes = json!({"items": [
            {"metadata": {"name": "node-a"}, "spec": {"drivers": [{"name": "ebs.csi.aws.com"}, {"name": "nfs.csi.k8s.io"}]}},
            {"metadata": {"name": "node-b"}, "spec": {"drivers": [{"name": "ebs.csi.aws.com"}]}}
        ]});

        let (expected, registered, missing) = driver_node_coverage(&csi_nodes, &ready, &drivers);
        assert_eq!(expected, 4);
        assert_eq!(registered, 3);
        assert_eq!(missing.len(), 1);
        assert!(missing[0].contains("node-b"));
        assert!(missing[0].contains("nfs.csi.k8s.io"));
    }
}
