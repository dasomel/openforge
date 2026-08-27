use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::Path,
};

#[derive(Debug, Deserialize)]
struct Assessment {
    schema: String,
    ruleset: String,
    overall: f64,
    grade: String,
    level: String,
    #[serde(default)]
    policy: Option<AssessmentPolicy>,
    #[serde(default)]
    categories: BTreeMap<String, Category>,
    #[serde(default)]
    findings: Vec<Finding>,
}

#[derive(Debug, Deserialize)]
struct AssessmentPolicy {
    profile: String,
    #[serde(default)]
    fingerprint: Option<String>,
}

#[derive(Debug, Deserialize)]
struct Category {
    score: f64,
}

#[derive(Debug, Deserialize)]
struct Finding {
    rule_id: String,
    category: String,
    title: String,
    status: String,
    score: f64,
}

#[derive(Debug, Serialize)]
pub(crate) struct Comparison {
    pub(crate) schema: &'static str,
    pub(crate) before_schema: String,
    pub(crate) after_schema: String,
    pub(crate) before_ruleset: String,
    pub(crate) after_ruleset: String,
    pub(crate) before_policy: Option<PolicyIdentity>,
    pub(crate) after_policy: Option<PolicyIdentity>,
    pub(crate) compatible: bool,
    pub(crate) warnings: Vec<String>,
    pub(crate) overall: OverallDelta,
    pub(crate) categories: Vec<CategoryDelta>,
    pub(crate) rules: Vec<RuleDelta>,
    pub(crate) summary: Summary,
}

#[derive(Debug, Serialize)]
pub(crate) struct PolicyIdentity {
    profile: String,
    fingerprint: Option<String>,
}

#[derive(Debug, Serialize)]
pub(crate) struct OverallDelta {
    before: f64,
    after: f64,
    delta: f64,
    before_grade: String,
    after_grade: String,
    before_level: String,
    after_level: String,
}

#[derive(Debug, Serialize)]
pub(crate) struct CategoryDelta {
    name: String,
    before: Option<f64>,
    after: Option<f64>,
    delta: Option<f64>,
}

#[derive(Debug, Serialize)]
pub(crate) struct RuleDelta {
    rule_id: String,
    category: String,
    title: String,
    before_status: Option<String>,
    after_status: Option<String>,
    before_score: Option<f64>,
    after_score: Option<f64>,
    delta: Option<f64>,
    change: &'static str,
}

#[derive(Debug, Serialize)]
pub(crate) struct Summary {
    pub(crate) improved: usize,
    pub(crate) regressed: usize,
    pub(crate) unchanged: usize,
    pub(crate) added: usize,
    pub(crate) removed: usize,
}

fn round1(value: f64) -> f64 {
    (value * 10.0).round() / 10.0
}

fn read_assessment(path: &Path) -> Result<Assessment> {
    let text = fs::read_to_string(path)
        .with_context(|| format!("cannot read assessment: {}", path.display()))?;
    serde_json::from_str(&text)
        .with_context(|| format!("invalid assessment JSON: {}", path.display()))
}

fn policy_identity(policy: &Option<AssessmentPolicy>) -> Option<PolicyIdentity> {
    policy.as_ref().map(|policy| PolicyIdentity {
        profile: policy.profile.clone(),
        fingerprint: policy.fingerprint.clone(),
    })
}

fn add_policy_warnings(
    before: &Option<AssessmentPolicy>,
    after: &Option<AssessmentPolicy>,
    warnings: &mut Vec<String>,
) {
    match (before, after) {
        (None, None) => {}
        (None, Some(after)) => warnings.push(format!(
            "assessment policy introduced: profile={} fingerprint={}",
            after.profile,
            after.fingerprint.as_deref().unwrap_or("<unavailable>")
        )),
        (Some(before), None) => warnings.push(format!(
            "assessment policy removed: profile={} fingerprint={}",
            before.profile,
            before.fingerprint.as_deref().unwrap_or("<unavailable>")
        )),
        (Some(before), Some(after)) => {
            if before.profile != after.profile {
                warnings.push(format!(
                    "policy profile changed: {} -> {}",
                    before.profile, after.profile
                ));
            }
            match (&before.fingerprint, &after.fingerprint) {
                (Some(left), Some(right)) if left != right => {
                    warnings.push(format!("policy fingerprint changed: {left} -> {right}"))
                }
                (None, Some(_)) | (Some(_), None) => warnings.push(
                    "policy fingerprint availability changed; policy equivalence cannot be proven"
                        .to_string(),
                ),
                _ => {}
            }
        }
    }
}

fn rule_map(findings: Vec<Finding>) -> BTreeMap<String, Finding> {
    findings
        .into_iter()
        .map(|finding| (finding.rule_id.clone(), finding))
        .collect()
}

fn classify(before: Option<&Finding>, after: Option<&Finding>) -> &'static str {
    match (before, after) {
        (None, Some(_)) => "ADDED",
        (Some(_), None) => "REMOVED",
        (Some(before), Some(after)) => {
            if before.status == after.status && (before.score - after.score).abs() < f64::EPSILON {
                "UNCHANGED"
            } else if after.score > before.score
                || (before.status == "FAIL" && after.status == "PASS")
            {
                "IMPROVED"
            } else if after.score < before.score
                || (before.status == "PASS" && after.status == "FAIL")
            {
                "REGRESSED"
            } else {
                "CHANGED"
            }
        }
        (None, None) => "UNCHANGED",
    }
}

pub(crate) fn compare(before_path: &Path, after_path: &Path) -> Result<Comparison> {
    let before = read_assessment(before_path)?;
    let after = read_assessment(after_path)?;

    let mut warnings = Vec::new();
    if before.schema != after.schema {
        warnings.push(format!(
            "assessment schema changed: {} -> {}",
            before.schema, after.schema
        ));
    }
    if before.ruleset != after.ruleset {
        warnings.push(format!(
            "ruleset changed: {} -> {}",
            before.ruleset, after.ruleset
        ));
    }
    add_policy_warnings(&before.policy, &after.policy, &mut warnings);
    let compatible = warnings.is_empty();

    let mut category_names: BTreeSet<String> = before.categories.keys().cloned().collect();
    category_names.extend(after.categories.keys().cloned());
    let categories = category_names
        .into_iter()
        .map(|name| {
            let before_score = before.categories.get(&name).map(|category| category.score);
            let after_score = after.categories.get(&name).map(|category| category.score);
            let delta = match (before_score, after_score) {
                (Some(before), Some(after)) => Some(round1(after - before)),
                _ => None,
            };
            CategoryDelta {
                name,
                before: before_score,
                after: after_score,
                delta,
            }
        })
        .collect();

    let before_policy = policy_identity(&before.policy);
    let after_policy = policy_identity(&after.policy);
    let before_rules = rule_map(before.findings);
    let after_rules = rule_map(after.findings);
    let mut rule_ids: BTreeSet<String> = before_rules.keys().cloned().collect();
    rule_ids.extend(after_rules.keys().cloned());

    let mut summary = Summary {
        improved: 0,
        regressed: 0,
        unchanged: 0,
        added: 0,
        removed: 0,
    };

    let mut rules = Vec::new();
    for rule_id in rule_ids {
        let before_rule = before_rules.get(&rule_id);
        let after_rule = after_rules.get(&rule_id);
        let change = classify(before_rule, after_rule);
        match change {
            "IMPROVED" => summary.improved += 1,
            "REGRESSED" => summary.regressed += 1,
            "ADDED" => summary.added += 1,
            "REMOVED" => summary.removed += 1,
            _ => summary.unchanged += 1,
        }

        let source = after_rule
            .or(before_rule)
            .expect("rule id came from one report");
        let delta = match (before_rule, after_rule) {
            (Some(before), Some(after)) => Some(round1(after.score - before.score)),
            _ => None,
        };
        rules.push(RuleDelta {
            rule_id,
            category: source.category.clone(),
            title: source.title.clone(),
            before_status: before_rule.map(|rule| rule.status.clone()),
            after_status: after_rule.map(|rule| rule.status.clone()),
            before_score: before_rule.map(|rule| rule.score),
            after_score: after_rule.map(|rule| rule.score),
            delta,
            change,
        });
    }

    rules.sort_by(|left, right| {
        let rank = |change: &str| match change {
            "REGRESSED" => 0,
            "IMPROVED" => 1,
            "ADDED" => 2,
            "REMOVED" => 3,
            _ => 4,
        };
        rank(left.change)
            .cmp(&rank(right.change))
            .then_with(|| left.rule_id.cmp(&right.rule_id))
    });

    Ok(Comparison {
        schema: "openforge-comparison/v0.2",
        before_schema: before.schema,
        after_schema: after.schema,
        before_ruleset: before.ruleset,
        after_ruleset: after.ruleset,
        before_policy,
        after_policy,
        compatible,
        warnings,
        overall: OverallDelta {
            before: before.overall,
            after: after.overall,
            delta: round1(after.overall - before.overall),
            before_grade: before.grade,
            after_grade: after.grade,
            before_level: before.level,
            after_level: after.level,
        },
        categories,
        rules,
        summary,
    })
}

pub(crate) fn print_text(comparison: &Comparison) {
    println!("OpenForge Assessment Comparison");
    println!("{}", "=".repeat(72));
    println!(
        "Overall: {:.1} -> {:.1} ({:+.1})   Grade: {} -> {}",
        comparison.overall.before,
        comparison.overall.after,
        comparison.overall.delta,
        comparison.overall.before_grade,
        comparison.overall.after_grade
    );
    println!(
        "Level:   {} -> {}",
        comparison.overall.before_level, comparison.overall.after_level
    );
    if !comparison.warnings.is_empty() {
        for warning in &comparison.warnings {
            println!("WARN: {warning}");
        }
    }
    println!("{}", "-".repeat(72));
    println!("Categories");
    for category in &comparison.categories {
        match (category.before, category.after, category.delta) {
            (Some(before), Some(after), Some(delta)) => {
                println!(
                    "{:<28} {:>5.1} -> {:>5.1} ({:+.1})",
                    category.name, before, after, delta
                );
            }
            (None, Some(after), _) => println!("{:<28}   NEW -> {:>5.1}", category.name, after),
            (Some(before), None, _) => {
                println!("{:<28} {:>5.1} -> REMOVED", category.name, before);
            }
            _ => {}
        }
    }
    println!("{}", "-".repeat(72));
    println!(
        "Rules: improved={} regressed={} added={} removed={} unchanged={}",
        comparison.summary.improved,
        comparison.summary.regressed,
        comparison.summary.added,
        comparison.summary.removed,
        comparison.summary.unchanged
    );
    for rule in comparison
        .rules
        .iter()
        .filter(|rule| rule.change != "UNCHANGED")
    {
        println!(
            "{:<9} [{}] {}  {} -> {}{}",
            rule.change,
            rule.rule_id,
            rule.title,
            rule.before_status.as_deref().unwrap_or("-"),
            rule.after_status.as_deref().unwrap_or("-"),
            rule.delta
                .map(|delta| format!(" ({delta:+.1})"))
                .unwrap_or_default()
        );
    }
}

#[cfg(test)]
mod tests {
    use super::{AssessmentPolicy, Finding, add_policy_warnings, classify};

    fn finding(status: &str, score: f64) -> Finding {
        Finding {
            rule_id: "R-1".to_string(),
            category: "Test".to_string(),
            title: "Rule".to_string(),
            status: status.to_string(),
            score,
        }
    }

    #[test]
    fn classifies_improvement_and_regression() {
        let fail = finding("FAIL", 0.0);
        let pass = finding("PASS", 10.0);
        assert_eq!(classify(Some(&fail), Some(&pass)), "IMPROVED");
        assert_eq!(classify(Some(&pass), Some(&fail)), "REGRESSED");
    }

    #[test]
    fn classifies_added_removed_and_unchanged() {
        let pass = finding("PASS", 10.0);
        assert_eq!(classify(None, Some(&pass)), "ADDED");
        assert_eq!(classify(Some(&pass), None), "REMOVED");
        assert_eq!(classify(Some(&pass), Some(&pass)), "UNCHANGED");
    }

    #[test]
    fn warns_when_policy_fingerprint_changes() {
        let before = Some(AssessmentPolicy {
            profile: "platform".to_string(),
            fingerprint: Some("fnv1a64:aaa".to_string()),
        });
        let after = Some(AssessmentPolicy {
            profile: "platform".to_string(),
            fingerprint: Some("fnv1a64:bbb".to_string()),
        });
        let mut warnings = Vec::new();
        add_policy_warnings(&before, &after, &mut warnings);
        assert_eq!(warnings.len(), 1);
        assert!(warnings[0].contains("policy fingerprint changed"));
    }
}
