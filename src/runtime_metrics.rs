use crate::Finding;
use std::process::Command;

fn kubectl_raw(context: Option<&str>, path: &str) -> Result<String, String> {
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
    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}

fn skipped(reason: String) -> Finding {
    Finding {
        rule_id: "RT-007".to_string(),
        category: "Runtime Compatibility".to_string(),
        title: "No deprecated Kubernetes APIs are actively requested".to_string(),
        status: "SKIP",
        score: 0.0,
        weight: 0.0,
        evidence: vec![reason],
        remediation: String::new(),
    }
}

fn deprecated_api_requests(metrics: &str) -> Vec<String> {
    metrics
        .lines()
        .filter(|line| line.starts_with("apiserver_requested_deprecated_apis{"))
        .filter_map(|line| {
            let (labels, value) = line.rsplit_once(' ')?;
            let active = value.parse::<f64>().ok().is_some_and(|value| value > 0.0);
            active.then(|| labels.to_string())
        })
        .collect()
}

pub(crate) fn finding(enabled: bool, context: Option<&str>) -> Finding {
    if !enabled {
        return skipped("runtime assessment disabled; use --runtime".to_string());
    }

    let metrics = match kubectl_raw(context, "/metrics") {
        Ok(metrics) => metrics,
        Err(error) => return skipped(error),
    };
    let deprecated = deprecated_api_requests(&metrics);

    Finding {
        rule_id: "RT-007".to_string(),
        category: "Runtime Compatibility".to_string(),
        title: "No deprecated Kubernetes APIs are actively requested".to_string(),
        status: if deprecated.is_empty() { "PASS" } else { "FAIL" },
        score: if deprecated.is_empty() { 8.0 } else { 0.0 },
        weight: 8.0,
        evidence: if deprecated.is_empty() {
            vec!["active_deprecated_api_requests=0".to_string()]
        } else {
            deprecated
        },
        remediation: "Identify clients requesting deprecated APIs and migrate them before the API removal release."
            .to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::deprecated_api_requests;

    #[test]
    fn finds_active_deprecated_api_metric() {
        let metrics = r#"
apiserver_requested_deprecated_apis{group="extensions",removed_release="1.22",resource="ingresses",version="v1beta1"} 1
apiserver_requested_deprecated_apis{group="policy",removed_release="1.25",resource="podsecuritypolicies",version="v1beta1"} 0
"#;
        let found = deprecated_api_requests(metrics);
        assert_eq!(found.len(), 1);
        assert!(found[0].contains("ingresses"));
    }
}
