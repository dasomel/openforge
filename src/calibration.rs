use anyhow::{Context, Result, bail};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{collections::BTreeMap, fs, path::Path};

const SCHEMA: &str = "openforge-calibration/v0.2";

#[derive(Debug, Clone, Deserialize)]
pub struct CalibrationManifest {
    pub project: String,
    #[serde(default)]
    pub commit: Option<String>,
    #[serde(default)]
    pub profile: Option<String>,
    #[serde(default)]
    pub expectations: BTreeMap<String, Expectation>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Expectation {
    pub classification: Classification,
    #[serde(default)]
    pub rationale: String,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Classification {
    TrueFinding,
    FalsePositive,
    NotApplicable,
    Accepted,
}

#[derive(Debug, Clone, Serialize)]
pub struct CalibrationRule {
    pub rule_id: String,
    pub assessment_status: String,
    pub classification: Option<Classification>,
    pub rationale: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct CalibrationSummary {
    /// PASS/FAIL rules that were actually scored in this assessment run.
    pub assessed_rules: usize,
    /// Active PASS/FAIL rules with a reviewed calibration classification.
    pub classified_rules: usize,
    /// Active PASS/FAIL rules that still need review.
    pub unclassified_rules: usize,
    /// SKIP/NOT_APPLICABLE/WAIVED and other non-scoring findings.
    pub inactive_rules: usize,
    pub failed_rules: usize,
    pub true_findings: usize,
    pub false_positives: usize,
    pub not_applicable: usize,
    pub accepted: usize,
    pub failure_precision_percent: Option<f64>,
    pub classification_coverage_percent: f64,
}

#[derive(Debug, Clone, Serialize)]
pub struct CalibrationReport {
    pub schema: String,
    pub project: String,
    pub commit: Option<String>,
    pub profile: Option<String>,
    pub assessment_schema: String,
    pub assessment_ruleset: String,
    pub summary: CalibrationSummary,
    pub rules: Vec<CalibrationRule>,
}

fn read_json(path: &Path) -> Result<Value> {
    let raw = fs::read_to_string(path)
        .with_context(|| format!("cannot read calibration input {}", path.display()))?;
    serde_json::from_str(&raw).with_context(|| format!("invalid JSON in {}", path.display()))
}

fn percentage(part: usize, total: usize) -> f64 {
    if total == 0 {
        100.0
    } else {
        (part as f64 / total as f64) * 100.0
    }
}

fn is_active(status: &str) -> bool {
    matches!(status, "PASS" | "FAIL")
}

fn validate_classification(
    rule_id: &str,
    status: &str,
    classification: Classification,
) -> Result<()> {
    let valid = match classification {
        Classification::TrueFinding | Classification::FalsePositive => status == "FAIL",
        Classification::NotApplicable => matches!(status, "FAIL" | "NOT_APPLICABLE"),
        Classification::Accepted => status == "PASS",
    };

    if !valid {
        bail!(
            "calibration classification '{classification:?}' is inconsistent with {rule_id} status '{status}'"
        );
    }
    Ok(())
}

pub fn calibrate(assessment_path: &Path, manifest_path: &Path) -> Result<CalibrationReport> {
    let assessment = read_json(assessment_path)?;
    let manifest_value = read_json(manifest_path)?;
    let manifest: CalibrationManifest = serde_json::from_value(manifest_value)
        .with_context(|| format!("invalid calibration manifest {}", manifest_path.display()))?;

    let assessment_schema = assessment
        .get("schema")
        .and_then(Value::as_str)
        .unwrap_or("unknown")
        .to_string();
    let assessment_ruleset = assessment
        .get("ruleset")
        .and_then(Value::as_str)
        .unwrap_or("unknown")
        .to_string();
    let findings = assessment
        .get("findings")
        .and_then(Value::as_array)
        .ok_or_else(|| anyhow::anyhow!("assessment does not contain a findings array"))?;

    let mut rules = Vec::with_capacity(findings.len());
    let mut assessed_rules = 0usize;
    let mut inactive_rules = 0usize;
    let mut failed_rules = 0usize;
    let mut classified_rules = 0usize;
    let mut true_findings = 0usize;
    let mut false_positives = 0usize;
    let mut not_applicable = 0usize;
    let mut accepted = 0usize;

    for finding in findings {
        let rule_id = finding
            .get("rule_id")
            .and_then(Value::as_str)
            .ok_or_else(|| anyhow::anyhow!("assessment finding is missing rule_id"))?
            .to_string();
        let status = finding
            .get("status")
            .and_then(Value::as_str)
            .unwrap_or("UNKNOWN")
            .to_string();
        let active = is_active(&status);
        if active {
            assessed_rules += 1;
        } else {
            inactive_rules += 1;
        }
        if status == "FAIL" {
            failed_rules += 1;
        }

        let expectation = manifest.expectations.get(&rule_id);
        if let Some(expectation) = expectation {
            validate_classification(&rule_id, &status, expectation.classification)?;
            if active {
                classified_rules += 1;
            }
            match expectation.classification {
                Classification::TrueFinding => true_findings += 1,
                Classification::FalsePositive => false_positives += 1,
                Classification::NotApplicable => not_applicable += 1,
                Classification::Accepted => accepted += 1,
            }
        }

        rules.push(CalibrationRule {
            rule_id,
            assessment_status: status,
            classification: expectation.map(|item| item.classification),
            rationale: expectation
                .map(|item| item.rationale.clone())
                .unwrap_or_default(),
        });
    }

    for rule_id in manifest.expectations.keys() {
        if !rules.iter().any(|rule| &rule.rule_id == rule_id) {
            bail!(
                "calibration manifest references rule '{rule_id}' that is absent from the assessment"
            );
        }
    }

    let failure_classified = true_findings + false_positives;
    let failure_precision_percent = if failure_classified == 0 {
        None
    } else {
        Some(percentage(true_findings, failure_classified))
    };

    Ok(CalibrationReport {
        schema: SCHEMA.to_string(),
        project: manifest.project,
        commit: manifest.commit,
        profile: manifest.profile,
        assessment_schema,
        assessment_ruleset,
        summary: CalibrationSummary {
            assessed_rules,
            classified_rules,
            unclassified_rules: assessed_rules.saturating_sub(classified_rules),
            inactive_rules,
            failed_rules,
            true_findings,
            false_positives,
            not_applicable,
            accepted,
            failure_precision_percent,
            classification_coverage_percent: percentage(classified_rules, assessed_rules),
        },
        rules,
    })
}

pub fn print_text(report: &CalibrationReport) {
    println!("OpenForge Calibration Report");
    println!("Project: {}", report.project);
    if let Some(commit) = &report.commit {
        println!("Commit:  {commit}");
    }
    if let Some(profile) = &report.profile {
        println!("Profile: {profile}");
    }
    println!(
        "Classified active rules: {}/{} ({:.1}%)",
        report.summary.classified_rules,
        report.summary.assessed_rules,
        report.summary.classification_coverage_percent
    );
    println!("Inactive findings: {}", report.summary.inactive_rules);
    if let Some(precision) = report.summary.failure_precision_percent {
        println!("Failure precision: {precision:.1}%");
    } else {
        println!("Failure precision: n/a");
    }
    println!(
        "true_finding={} false_positive={} not_applicable={} accepted={} unclassified={}",
        report.summary.true_findings,
        report.summary.false_positives,
        report.summary.not_applicable,
        report.summary.accepted,
        report.summary.unclassified_rules
    );

    for rule in &report.rules {
        let Some(classification) = rule.classification else {
            continue;
        };
        println!(
            "{:?} [{}] status={}{}",
            classification,
            rule.rule_id,
            rule.assessment_status,
            if rule.rationale.is_empty() {
                String::new()
            } else {
                format!(" — {}", rule.rationale)
            }
        );
    }
}

#[cfg(test)]
mod tests {
    use super::{Classification, calibrate};
    use std::{
        fs,
        path::PathBuf,
        time::{SystemTime, UNIX_EPOCH},
    };

    fn temp(name: &str) -> PathBuf {
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        std::env::temp_dir().join(format!("openforge-calibration-{name}-{nonce}.json"))
    }

    #[test]
    fn calculates_precision_and_coverage_from_active_rules_only() {
        let assessment_path = temp("assessment");
        let manifest_path = temp("manifest");
        fs::write(
            &assessment_path,
            r#"{"schema":"openforge-assessment/v0.17","ruleset":"maturity-v0.1","findings":[{"rule_id":"A","status":"FAIL"},{"rule_id":"B","status":"FAIL"},{"rule_id":"C","status":"PASS"},{"rule_id":"R","status":"SKIP"}]}"#,
        )
        .unwrap();
        fs::write(
            &manifest_path,
            r#"{"project":"fixture","expectations":{"A":{"classification":"true_finding","rationale":"real"},"B":{"classification":"false_positive","rationale":"noise"}}}"#,
        )
        .unwrap();

        let report = calibrate(&assessment_path, &manifest_path).unwrap();
        assert_eq!(report.summary.assessed_rules, 3);
        assert_eq!(report.summary.inactive_rules, 1);
        assert_eq!(report.summary.classified_rules, 2);
        assert_eq!(report.summary.unclassified_rules, 1);
        assert_eq!(report.summary.failure_precision_percent, Some(50.0));
        assert_eq!(
            report.rules[0].classification,
            Some(Classification::TrueFinding)
        );
    }

    #[test]
    fn rejects_failure_classification_for_passed_rule() {
        let assessment_path = temp("status-assessment");
        let manifest_path = temp("status-manifest");
        fs::write(
            &assessment_path,
            r#"{"findings":[{"rule_id":"A","status":"PASS"}]}"#,
        )
        .unwrap();
        fs::write(
            &manifest_path,
            r#"{"project":"fixture","expectations":{"A":{"classification":"false_positive"}}}"#,
        )
        .unwrap();

        assert!(calibrate(&assessment_path, &manifest_path).is_err());
    }

    #[test]
    fn accepts_not_applicable_classification_for_not_applicable_rule() {
        let assessment_path = temp("na-assessment");
        let manifest_path = temp("na-manifest");
        fs::write(
            &assessment_path,
            r#"{"findings":[{"rule_id":"WEB-001","status":"NOT_APPLICABLE"}]}"#,
        )
        .unwrap();
        fs::write(
            &manifest_path,
            r#"{"project":"fixture","expectations":{"WEB-001":{"classification":"not_applicable"}}}"#,
        )
        .unwrap();

        let report = calibrate(&assessment_path, &manifest_path).unwrap();
        assert_eq!(report.summary.assessed_rules, 0);
        assert_eq!(report.summary.inactive_rules, 1);
        assert_eq!(report.summary.not_applicable, 1);
    }

    #[test]
    fn rejects_expectations_for_missing_rules() {
        let assessment_path = temp("missing-assessment");
        let manifest_path = temp("missing-manifest");
        fs::write(
            &assessment_path,
            r#"{"findings":[{"rule_id":"A","status":"PASS"}]}"#,
        )
        .unwrap();
        fs::write(
            &manifest_path,
            r#"{"project":"fixture","expectations":{"Z":{"classification":"accepted"}}}"#,
        )
        .unwrap();

        assert!(calibrate(&assessment_path, &manifest_path).is_err());
    }
}
