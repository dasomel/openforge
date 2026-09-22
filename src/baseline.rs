use crate::compare;
use anyhow::{Context, Result};
use chrono::Utc;
use serde::{Deserialize, Serialize};
use serde_json::{Map, Value};
use std::{fs, path::Path};

#[derive(Debug, Deserialize)]
struct AssessmentIdentity {
    schema: String,
    ruleset: String,
    overall: f64,
    #[serde(default)]
    policy: Option<PolicyIdentity>,
}

#[derive(Debug, Deserialize)]
struct PolicyIdentity {
    profile: String,
    #[serde(default)]
    fingerprint: Option<String>,
}

#[derive(Debug, Serialize)]
struct BaselineMetadata {
    schema: &'static str,
    created_at: String,
    assessment_schema: String,
    ruleset: String,
    overall: f64,
    policy_profile: Option<String>,
    policy_fingerprint: Option<String>,
}

fn read_object(path: &Path) -> Result<(Map<String, Value>, AssessmentIdentity)> {
    let text = fs::read_to_string(path)
        .with_context(|| format!("cannot read assessment: {}", path.display()))?;
    let value: Value = serde_json::from_str(&text)
        .with_context(|| format!("invalid assessment JSON: {}", path.display()))?;
    let object = value
        .as_object()
        .cloned()
        .context("assessment JSON root must be an object")?;
    let identity: AssessmentIdentity = serde_json::from_value(Value::Object(object.clone()))
        .context("assessment is missing required identity fields")?;
    Ok((object, identity))
}

pub(crate) fn create(assessment_path: &Path, output_path: &Path) -> Result<()> {
    let (mut object, identity) = read_object(assessment_path)?;
    let metadata = BaselineMetadata {
        schema: "openforge-baseline/v0.1",
        created_at: Utc::now().to_rfc3339(),
        assessment_schema: identity.schema,
        ruleset: identity.ruleset,
        overall: identity.overall,
        policy_profile: identity
            .policy
            .as_ref()
            .map(|policy| policy.profile.clone()),
        policy_fingerprint: identity.policy.and_then(|policy| policy.fingerprint),
    };
    object.insert("_baseline".to_string(), serde_json::to_value(metadata)?);

    if let Some(parent) = output_path.parent() {
        if !parent.as_os_str().is_empty() {
            fs::create_dir_all(parent)
                .with_context(|| format!("cannot create {}", parent.display()))?;
        }
    }
    fs::write(
        output_path,
        serde_json::to_string_pretty(&Value::Object(object))?,
    )
    .with_context(|| format!("cannot write baseline: {}", output_path.display()))?;
    Ok(())
}

pub(crate) fn check(
    baseline_path: &Path,
    current_path: &Path,
    fail_on_regression: bool,
    require_compatible: bool,
    json: bool,
) -> Result<i32> {
    let comparison = compare::compare(baseline_path, current_path)?;
    if json {
        println!("{}", serde_json::to_string_pretty(&comparison)?);
    } else {
        compare::print_text(&comparison);
    }

    if require_compatible && !comparison.compatible {
        return Ok(3);
    }
    if fail_on_regression && comparison.summary.regressed > 0 {
        return Ok(2);
    }
    Ok(0)
}

#[cfg(test)]
mod tests {
    use super::AssessmentIdentity;

    #[test]
    fn baseline_identity_accepts_policy_fingerprint() {
        let identity: AssessmentIdentity = serde_json::from_str(
            r#"{
                "schema":"openforge-assessment/v0.12",
                "ruleset":"maturity-v0.1",
                "overall":88.4,
                "policy":{"profile":"production","fingerprint":"fnv1a64:abcd"}
            }"#,
        )
        .unwrap();
        assert_eq!(identity.ruleset, "maturity-v0.1");
        assert_eq!(identity.policy.unwrap().profile, "production");
    }
}
