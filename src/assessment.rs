use crate::{
    execution, policy, runtime, runtime_alertmanager, runtime_backup, runtime_certificates,
    runtime_csi, runtime_csi_nodes, runtime_gitops, runtime_metrics, runtime_observability,
    runtime_pod_security, runtime_post_restore, runtime_rbac, runtime_restore, runtime_storage,
    runtime_targets, web_assets, web_cache,
};
use anyhow::{Context, Result};
use globset::{Glob, GlobSetBuilder};
use serde::{Deserialize, Serialize};
use std::{
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
};
use walkdir::WalkDir;

const DEFAULT_RULES: &str = include_str!("../rules/maturity-v0.1.json");

#[derive(Debug, Deserialize)]
struct Ruleset {
    version: String,
    rules: Vec<Rule>,
}

#[derive(Debug, Deserialize)]
struct Rule {
    id: String,
    category: String,
    title: String,
    weight: f64,
    check: Check,
    #[serde(default)]
    remediation: String,
}

#[derive(Debug, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
enum Check {
    AnyFile {
        patterns: Vec<String>,
    },
    Contains {
        patterns: Vec<String>,
        needles: Vec<String>,
    },
}

#[derive(Debug, Serialize)]
pub struct Finding {
    pub rule_id: String,
    pub category: String,
    pub title: String,
    pub status: &'static str,
    pub score: f64,
    pub weight: f64,
    pub evidence: Vec<String>,
    pub remediation: String,
}

#[derive(Debug, Serialize)]
pub struct CategoryScore {
    pub score: f64,
    pub earned: f64,
    pub max: f64,
}

#[derive(Debug, Serialize)]
pub struct Report {
    pub schema: &'static str,
    pub ruleset: String,
    pub root: String,
    pub execution_enabled: bool,
    pub runtime_enabled: bool,
    pub runtime_context: Option<String>,
    pub runtime_namespace: Option<String>,
    pub post_restore_spec: Option<String>,
    pub policy: Option<policy::PolicySummary>,
    pub overall: f64,
    pub grade: &'static str,
    pub level: &'static str,
    pub categories: BTreeMap<String, CategoryScore>,
    pub findings: Vec<Finding>,
}

#[derive(Debug, Default)]
pub struct AssessOptions<'a> {
    pub rules: Option<&'a Path>,
    pub policy: Option<&'a Path>,
    pub run_execution: bool,
    pub runtime: bool,
    pub kube_context: Option<&'a str>,
    pub namespace: Option<&'a str>,
    pub post_restore_spec: Option<&'a Path>,
}

fn collect_files(root: &Path) -> Vec<PathBuf> {
    WalkDir::new(root)
        .into_iter()
        .filter_entry(|entry| {
            let name = entry.file_name().to_string_lossy();
            name != ".git" && name != "target" && name != "node_modules" && name != "vendor"
        })
        .filter_map(Result::ok)
        .filter(|entry| entry.file_type().is_file())
        .filter_map(|entry| entry.path().strip_prefix(root).ok().map(PathBuf::from))
        .collect()
}

fn matches(files: &[PathBuf], patterns: &[String]) -> Result<Vec<String>> {
    let mut builder = GlobSetBuilder::new();
    for pattern in patterns {
        builder
            .add(Glob::new(pattern).with_context(|| format!("invalid glob pattern: {pattern}"))?);
    }
    let set = builder.build()?;
    let mut matched: Vec<String> = files
        .iter()
        .filter(|path| set.is_match(path))
        .map(|path| path.to_string_lossy().to_string())
        .collect();
    matched.sort();
    matched.dedup();
    Ok(matched)
}

fn evaluate_static_rule(root: &Path, files: &[PathBuf], rule: &Rule) -> Result<Finding> {
    let (passed, evidence) = match &rule.check {
        Check::AnyFile { patterns } => {
            let evidence = matches(files, patterns)?;
            (!evidence.is_empty(), evidence)
        }
        Check::Contains { patterns, needles } => {
            let candidates = matches(files, patterns)?;
            let needles: Vec<String> = needles.iter().map(|needle| needle.to_lowercase()).collect();
            let mut evidence = Vec::new();
            for relative_path in candidates {
                if let Ok(text) = fs::read_to_string(root.join(&relative_path)) {
                    let text = text.to_lowercase();
                    if needles.iter().any(|needle| text.contains(needle)) {
                        evidence.push(relative_path);
                    }
                }
            }
            (!evidence.is_empty(), evidence)
        }
    };

    Ok(Finding {
        rule_id: rule.id.clone(),
        category: rule.category.clone(),
        title: rule.title.clone(),
        status: if passed { "PASS" } else { "FAIL" },
        score: if passed { rule.weight } else { 0.0 },
        weight: rule.weight,
        evidence,
        remediation: rule.remediation.clone(),
    })
}

fn grade(score: f64) -> &'static str {
    if score >= 90.0 {
        "A"
    } else if score >= 80.0 {
        "B"
    } else if score >= 70.0 {
        "C"
    } else if score >= 60.0 {
        "D"
    } else {
        "E"
    }
}

fn level(score: f64) -> &'static str {
    if score >= 90.0 {
        "L5 Optimizing"
    } else if score >= 80.0 {
        "L4 Resilient"
    } else if score >= 70.0 {
        "L3 Production"
    } else if score >= 55.0 {
        "L2 Managed"
    } else if score >= 35.0 {
        "L1 Repeatable"
    } else {
        "L0 Initial"
    }
}

fn round1(value: f64) -> f64 {
    (value * 10.0).round() / 10.0
}

fn score_findings(findings: &[Finding]) -> (BTreeMap<String, CategoryScore>, f64) {
    let mut totals: BTreeMap<String, (f64, f64)> = BTreeMap::new();
    for finding in findings {
        if !matches!(finding.status, "PASS" | "FAIL") {
            continue;
        }
        let total = totals.entry(finding.category.clone()).or_default();
        total.0 += finding.score;
        total.1 += finding.weight;
    }

    let mut categories = BTreeMap::new();
    let (mut earned, mut maximum) = (0.0, 0.0);
    for (name, (category_earned, category_maximum)) in totals {
        categories.insert(
            name,
            CategoryScore {
                score: if category_maximum > 0.0 {
                    round1(category_earned / category_maximum * 100.0)
                } else {
                    0.0
                },
                earned: category_earned,
                max: category_maximum,
            },
        );
        earned += category_earned;
        maximum += category_maximum;
    }
    let overall = if maximum > 0.0 {
        round1(earned / maximum * 100.0)
    } else {
        0.0
    };
    (categories, overall)
}

pub fn assess(root: &Path, options: &AssessOptions<'_>) -> Result<Report> {
    let root = root
        .canonicalize()
        .with_context(|| format!("invalid path: {}", root.display()))?;
    let rules_text = match options.rules {
        Some(path) => fs::read_to_string(path)
            .with_context(|| format!("cannot read rules: {}", path.display()))?,
        None => DEFAULT_RULES.to_string(),
    };
    let rules: Ruleset = serde_json::from_str(&rules_text).context("invalid maturity ruleset")?;
    let assessment_policy = options.policy.map(policy::load).transpose()?;

    let files = collect_files(&root);
    let mut findings = Vec::new();
    for rule in &rules.rules {
        findings.push(evaluate_static_rule(&root, &files, rule)?);
    }

    findings.extend(web_assets::findings(&root));
    findings.push(web_cache::finding(&root));
    findings.extend(execution::findings(&root, options.run_execution));
    findings.extend(runtime::findings(
        options.runtime,
        options.kube_context,
        options.namespace,
    ));
    findings.push(runtime_metrics::finding(
        options.runtime,
        options.kube_context,
    ));
    findings.extend(runtime_rbac::findings(
        options.runtime,
        options.kube_context,
    ));
    findings.push(runtime_pod_security::finding(
        options.runtime,
        options.kube_context,
        options.namespace,
    ));
    findings.push(runtime_storage::finding(
        options.runtime,
        options.kube_context,
        options.namespace,
    ));
    findings.push(runtime_certificates::finding(
        options.runtime,
        options.kube_context,
        options.namespace,
    ));
    findings.push(runtime_backup::finding(
        options.runtime,
        options.kube_context,
        options.namespace,
    ));
    findings.push(runtime_observability::finding(
        options.runtime,
        options.kube_context,
    ));
    findings.push(runtime_gitops::finding(
        options.runtime,
        options.kube_context,
    ));
    findings.push(runtime_restore::finding(
        options.runtime,
        options.kube_context,
    ));
    findings.push(runtime_targets::finding(
        options.runtime,
        options.kube_context,
    ));
    findings.push(runtime_alertmanager::finding(
        options.runtime,
        options.kube_context,
    ));
    findings.push(runtime_csi::finding(options.runtime, options.kube_context));
    findings.push(runtime_csi_nodes::finding(
        options.runtime,
        options.kube_context,
    ));
    findings.push(runtime_post_restore::finding(
        options.runtime,
        options.kube_context,
        options.post_restore_spec,
    ));

    let policy_summary = assessment_policy
        .as_ref()
        .map(|p| policy::apply(&mut findings, p))
        .transpose()?;
    let (categories, overall) = score_findings(&findings);

    Ok(Report {
        schema: "openforge-assessment/v0.15",
        ruleset: rules.version,
        root: root.display().to_string(),
        execution_enabled: options.run_execution,
        runtime_enabled: options.runtime,
        runtime_context: options.kube_context.map(str::to_string),
        runtime_namespace: options.namespace.map(str::to_string),
        post_restore_spec: options
            .post_restore_spec
            .map(|path| path.display().to_string()),
        policy: policy_summary,
        overall,
        grade: grade(overall),
        level: level(overall),
        categories,
        findings,
    })
}

pub fn print_text(report: &Report) {
    println!("OpenForge Maturity Assessment");
    println!("{}", "=".repeat(72));
    println!(
        "Overall: {:>5.1} / 100   Grade: {}   {}",
        report.overall, report.grade, report.level
    );
    println!(
        "Execution evidence: {}",
        if report.execution_enabled {
            "enabled"
        } else {
            "disabled"
        }
    );
    println!(
        "Runtime evidence:   {}",
        if report.runtime_enabled {
            "enabled"
        } else {
            "disabled"
        }
    );
    if let Some(policy) = &report.policy {
        println!(
            "Policy profile:     {} (not-applicable={}, waived={}, expired={}, invalid={})",
            policy.profile,
            policy.not_applicable,
            policy.waived,
            policy.expired_waivers,
            policy.invalid_waivers
        );
    }
    println!("{}", "-".repeat(72));
    for (name, category) in &report.categories {
        println!("{:<24} {:>5.1} / 100", name, category.score);
    }
    println!("{}", "-".repeat(72));
    for finding in report
        .findings
        .iter()
        .filter(|f| matches!(f.status, "FAIL" | "SKIP" | "WAIVED" | "NOT_APPLICABLE"))
    {
        println!("{} [{}] {}", finding.status, finding.rule_id, finding.title);
        if finding.status == "FAIL" && !finding.remediation.is_empty() {
            println!("     {}", finding.remediation);
        }
    }
}
