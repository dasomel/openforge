use anyhow::{Context, Result, bail};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{collections::BTreeMap, fs, path::Path};

const SCHEMA: &str = "openforge-calibration/v0.1";

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
    pub assessed_rules: usize,
    pub classified_rules: usize,
    pub unclassified_rules: usize,
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
        if status == "FAIL" {
            failed_rules += 1;
        }

        let expectation = manifest.expectations.get(&rule_id);
        if let Some(expectation) = expectation {
            classified_rules += 1;
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
            bail!("calibration manifest references rule '{rule_id}' that is absent from the assessment");
        }
    }

    let failure_classified = true_findings + false_positives;
    let failure_precision_percent = if failure_classified == 0 {
        None
    } else {
        Some(percentage(true_findings, failure_classified))
    };
    let assessed_rules = rules.len();

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
        "Classified: {}/{} ({:.1}%)",
        report.summary.classified_rules,
        report.summary.assessed_rules,
        report.summary.classification_coverage_percent
    );
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
    use std::{fs, path::PathBuf, time::{SystemTime, UNIX_EPOCH}};

    fn temp(name: &str) -> PathBuf {
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        std::env::temp_dir().join(format!("openforge-calibration-{name}-{nonce}.json"))
    }

    #[test]
    fn calculates_failure_precision_and_coverage() {
        let assessment_path = temp("assessment");
        let manifest_path = temp("manifest");
        fs::write(
            &assessment_path,
            r#"{"schema":"openforge-assessment/v0.17","ruleset":"maturity-v0.1","findings":[{"rule_id":"A","status":"FAIL"},{"rule_id":"B","status":"FAIL"},{"rule_id":"C","status":"PASS"}]}"#,
        )
        .unwrap();
        fs::write(
            &manifest_path,
            r#"{"project":"fixture","expectations":{"A":{"classification":"true_finding","rationale":"real"},"B":{"classification":"false_positive","rationale":"noise"}}}"#,
        )
        .unwrap();

        let report = calibrate(&assessment_path, &manifest_path).unwrap();
        assert_eq!(report.summary.classified_rules, 2);
        assert_eq!(report.summary.unclassified_rules, 1);
        assert_eq!(report.summary.failure_precision_percent, Some(50.0));
        assert_eq!(report.rules[0].classification, Some(Classification::TrueFinding));
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
