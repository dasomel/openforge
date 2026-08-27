mod execution;
mod runtime;
mod runtime_backup;
mod runtime_certificates;
mod runtime_gitops;
mod runtime_metrics;
mod runtime_observability;
mod runtime_pod_security;
mod runtime_rbac;
mod runtime_restore;
mod runtime_storage;
mod runtime_targets;

use anyhow::{Context, Result};
use clap::{Parser, ValueEnum};
use globset::{Glob, GlobSetBuilder};
use serde::{Deserialize, Serialize};
use std::{
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
    process::ExitCode,
};
use walkdir::WalkDir;

const DEFAULT_RULES: &str = include_str!("../rules/maturity-v0.1.json");

#[derive(Parser, Debug)]
#[command(
    name = "openforge",
    version,
    about = "Deterministic OSS and platform maturity assessment"
)]
struct Cli {
    #[arg(default_value = ".")]
    path: PathBuf,

    #[arg(long, value_enum, default_value_t = OutputFormat::Text)]
    format: OutputFormat,

    #[arg(long)]
    output: Option<PathBuf>,

    #[arg(long)]
    rules: Option<PathBuf>,

    #[arg(long)]
    fail_under: Option<f64>,

    #[arg(
        long,
        help = "Run trusted built-in build/test/lint probes. This may execute target repository code."
    )]
    run_execution: bool,

    #[arg(
        long,
        help = "Collect read-only Kubernetes runtime evidence using the selected kube context."
    )]
    runtime: bool,

    #[arg(long, help = "Kubernetes context used by runtime assessment.")]
    kube_context: Option<String>,

    #[arg(
        long,
        help = "Limit namespaced runtime checks to one Kubernetes namespace."
    )]
    namespace: Option<String>,
}

#[derive(Copy, Clone, Debug, ValueEnum)]
enum OutputFormat {
    Text,
    Json,
}

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
pub(crate) struct Finding {
    pub(crate) rule_id: String,
    pub(crate) category: String,
    pub(crate) title: String,
    pub(crate) status: &'static str,
    pub(crate) score: f64,
    pub(crate) weight: f64,
    pub(crate) evidence: Vec<String>,
    pub(crate) remediation: String,
}

#[derive(Debug, Serialize)]
struct CategoryScore {
    score: f64,
    earned: f64,
    max: f64,
}

#[derive(Debug, Serialize)]
struct Report {
    schema: &'static str,
    ruleset: String,
    root: String,
    execution_enabled: bool,
    runtime_enabled: bool,
    runtime_context: Option<String>,
    runtime_namespace: Option<String>,
    overall: f64,
    grade: &'static str,
    level: &'static str,
    categories: BTreeMap<String, CategoryScore>,
    findings: Vec<Finding>,
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
        if finding.status == "SKIP" {
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

fn assess(
    root: &Path,
    rules: Ruleset,
    run_execution: bool,
    runtime_enabled: bool,
    runtime_context: Option<&str>,
    runtime_namespace: Option<&str>,
) -> Result<Report> {
    let files = collect_files(root);
    let mut findings = Vec::new();

    for rule in &rules.rules {
        findings.push(evaluate_static_rule(root, &files, rule)?);
    }

    findings.extend(execution::findings(root, run_execution));
    findings.extend(runtime::findings(
        runtime_enabled,
        runtime_context,
        runtime_namespace,
    ));
    findings.push(runtime_metrics::finding(runtime_enabled, runtime_context));
    findings.extend(runtime_rbac::findings(runtime_enabled, runtime_context));
    findings.push(runtime_pod_security::finding(
        runtime_enabled,
        runtime_context,
        runtime_namespace,
    ));
    findings.push(runtime_storage::finding(
        runtime_enabled,
        runtime_context,
        runtime_namespace,
    ));
    findings.push(runtime_certificates::finding(
        runtime_enabled,
        runtime_context,
        runtime_namespace,
    ));
    findings.push(runtime_backup::finding(
        runtime_enabled,
        runtime_context,
        runtime_namespace,
    ));
    findings.push(runtime_observability::finding(
        runtime_enabled,
        runtime_context,
    ));
    findings.push(runtime_gitops::finding(runtime_enabled, runtime_context));
    findings.push(runtime_restore::finding(runtime_enabled, runtime_context));
    findings.push(runtime_targets::finding(runtime_enabled, runtime_context));

    let (categories, overall) = score_findings(&findings);

    Ok(Report {
        schema: "openforge-assessment/v0.7",
        ruleset: rules.version,
        root: root
            .canonicalize()
            .unwrap_or_else(|_| root.to_path_buf())
            .display()
            .to_string(),
        execution_enabled: run_execution,
        runtime_enabled,
        runtime_context: runtime_context.map(str::to_string),
        runtime_namespace: runtime_namespace.map(str::to_string),
        overall,
        grade: grade(overall),
        level: level(overall),
        categories,
        findings,
    })
}

fn print_text(report: &Report) {
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
    println!("{}", "-".repeat(72));

    for (name, category) in &report.categories {
        println!("{:<24} {:>5.1} / 100", name, category.score);
    }

    println!("{}", "-".repeat(72));

    for finding in report
        .findings
        .iter()
        .filter(|finding| finding.status == "FAIL" || finding.status == "SKIP")
    {
        println!("{} [{}] {}", finding.status, finding.rule_id, finding.title);
        if finding.status == "FAIL" && !finding.remediation.is_empty() {
            println!("     {}", finding.remediation);
        }
    }
}

fn run() -> Result<i32> {
    let cli = Cli::parse();
    let root = cli
        .path
        .canonicalize()
        .with_context(|| format!("invalid path: {}", cli.path.display()))?;

    let rules_text = match cli.rules {
        Some(path) => fs::read_to_string(&path)
            .with_context(|| format!("cannot read rules: {}", path.display()))?,
        None => DEFAULT_RULES.to_string(),
    };
    let rules: Ruleset = serde_json::from_str(&rules_text).context("invalid maturity ruleset")?;

    let report = assess(
        &root,
        rules,
        cli.run_execution,
        cli.runtime,
        cli.kube_context.as_deref(),
        cli.namespace.as_deref(),
    )?;
    let json = serde_json::to_string_pretty(&report)?;

    if let Some(output) = &cli.output {
        fs::write(output, &json).with_context(|| format!("cannot write {}", output.display()))?;
    }

    match cli.format {
        OutputFormat::Text => print_text(&report),
        OutputFormat::Json => println!("{json}"),
    }

    Ok(
        if cli
            .fail_under
            .is_some_and(|threshold| report.overall < threshold)
        {
            2
        } else {
            0
        },
    )
}

fn main() -> ExitCode {
    match run() {
        Ok(code) => ExitCode::from(code as u8),
        Err(error) => {
            eprintln!("openforge: {error:#}");
            ExitCode::FAILURE
        }
    }
}
