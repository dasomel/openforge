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

fn driver_names(drivers: &Value) -> BTreeSet<String> {
    drivers
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|item| item.pointer("/metadata/name").and_then(Value::as_str))
        .map(str::to_string)
        .collect()
}

fn volume_attachment_health(
    attachments: &Value,
    provisioners: &BTreeSet<String>,
) -> (usize, Vec<String>) {
    let mut total = 0usize;
    let mut unhealthy = Vec::new();

    for item in attachments
        .get("items")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let attacher = item
            .pointer("/spec/attacher")
            .and_then(Value::as_str)
            .unwrap_or("");
        if !provisioners.contains(attacher) {
            continue;
        }
        total += 1;

        let name = item
            .pointer("/metadata/name")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        let node = item
            .pointer("/spec/nodeName")
            .and_then(Value::as_str)
            .unwrap_or("unknown");
        let attached = item
            .pointer("/status/attached")
            .and_then(Value::as_bool)
            .unwrap_or(false);
        let error = item
            .pointer("/status/attachError/message")
            .and_then(Value::as_str)
            .unwrap_or("");

        if !attached || !error.is_empty() {
            unhealthy.push(format!(
                "volumeattachment={name} attacher={attacher} node={node} attached={attached} attach_error={}",
                if error.is_empty() { "<none>" } else { error }
            ));
        }
    }

    (total, unhealthy)
}

fn skipped(reason: String) -> Finding {
    Finding {
        rule_id: "RT-019".to_string(),
        category: "Runtime Storage".to_string(),
        title: "CSI storage drivers and active volume attachments are healthy".to_string(),
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
    let provisioners = csi_provisioners(&storage_classes);
    if provisioners.is_empty() {
        return skipped("no CSI-backed StorageClass provisioners detected".to_string());
    }

    let drivers = match kubectl_json(context, &["get", "csidrivers.storage.k8s.io"]) {
        Ok(value) => value,
        Err(error) => return skipped(format!("CSIDriver API unavailable: {error}")),
    };
    let registered = driver_names(&drivers);
    let missing: Vec<String> = provisioners
        .difference(&registered)
        .map(|name| format!("missing_csidriver={name}"))
        .collect();

    let attachments = match kubectl_json(context, &["get", "volumeattachments.storage.k8s.io"]) {
        Ok(value) => value,
        Err(error) => return skipped(format!("VolumeAttachment API unavailable: {error}")),
    };
    let (attachment_total, unhealthy_attachments) =
        volume_attachment_health(&attachments, &provisioners);

    let driver_total = provisioners.len();
    let driver_healthy = driver_total.saturating_sub(missing.len());
    let attachment_healthy = attachment_total.saturating_sub(unhealthy_attachments.len());
    let denominator = driver_total + attachment_total;
    let healthy = driver_healthy + attachment_healthy;
    let ratio = if denominator == 0 {
        1.0
    } else {
        healthy as f64 / denominator as f64
    };

    let mut evidence = Vec::new();
    evidence.push(format!(
        "csi_drivers_registered={driver_healthy}/{driver_total} volumeattachments_healthy={attachment_healthy}/{attachment_total} coverage_percent={:.1}",
        ratio * 100.0
    ));
    evidence.extend(missing);
    evidence.extend(unhealthy_attachments);

    Finding {
        rule_id: "RT-019".to_string(),
        category: "Runtime Storage".to_string(),
        title: "CSI storage drivers and active volume attachments are healthy".to_string(),
        status: if ratio == 1.0 { "PASS" } else { "FAIL" },
        score: (ratio * 10.0 * 10.0).round() / 10.0,
        weight: 10.0,
        evidence,
        remediation: "Register the expected CSIDriver resources and investigate failed or pending CSI volume attachments, controller health, node plugins, topology, and backend connectivity."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::{csi_provisioners, driver_names, volume_attachment_health};
    use serde_json::json;

    #[test]
    fn detects_csi_provisioners_and_ignores_legacy_in_tree_plugins() {
        let classes = json!({"items": [
            {"provisioner": "ebs.csi.aws.com"},
            {"provisioner": "kubernetes.io/no-provisioner"}
        ]});
        let provisioners = csi_provisioners(&classes);
        assert!(provisioners.contains("ebs.csi.aws.com"));
        assert!(!provisioners.contains("kubernetes.io/no-provisioner"));
    }

    #[test]
    fn detects_registered_driver_names() {
        let drivers = json!({"items": [
            {"metadata": {"name": "ebs.csi.aws.com"}},
            {"metadata": {"name": "nfs.csi.k8s.io"}}
        ]});
        let names = driver_names(&drivers);
        assert_eq!(names.len(), 2);
        assert!(names.contains("nfs.csi.k8s.io"));
    }

    #[test]
    fn reports_failed_volume_attachments_for_known_provisioners() {
        let provisioners = ["ebs.csi.aws.com".to_string()].into_iter().collect();
        let attachments = json!({"items": [
            {"metadata": {"name": "ok"}, "spec": {"attacher": "ebs.csi.aws.com", "nodeName": "node-a"}, "status": {"attached": true}},
            {"metadata": {"name": "bad"}, "spec": {"attacher": "ebs.csi.aws.com", "nodeName": "node-b"}, "status": {"attached": false, "attachError": {"message": "timeout"}}},
            {"metadata": {"name": "other"}, "spec": {"attacher": "other.csi.io"}, "status": {"attached": false}}
        ]});
        let (total, unhealthy) = volume_attachment_health(&attachments, &provisioners);
        assert_eq!(total, 2);
        assert_eq!(unhealthy.len(), 1);
        assert!(unhealthy[0].contains("bad"));
        assert!(unhealthy[0].contains("timeout"));
    }
}
