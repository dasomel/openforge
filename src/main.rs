use anyhow::{Context, Result};
use clap::{Parser, ValueEnum};
use globset::{Glob, GlobSetBuilder};
use serde::{Deserialize, Serialize};
use std::{collections::BTreeMap, fs, path::{Path, PathBuf}, process::ExitCode};
use walkdir::WalkDir;

const DEFAULT_RULES: &str = include_str!("../rules/maturity-v0.1.json");

#[derive(Parser, Debug)]
#[command(name = "openforge", version, about = "Deterministic OSS and platform maturity assessment")]
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
}

#[derive(Copy, Clone, Debug, ValueEnum)]
enum OutputFormat { Text, Json }

#[derive(Debug, Deserialize)]
struct Ruleset { version: String, rules: Vec<Rule> }

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
    AnyFile { patterns: Vec<String> },
    Contains { patterns: Vec<String>, needles: Vec<String> },
}

#[derive(Debug, Serialize)]
struct Finding {
    rule_id: String,
    category: String,
    title: String,
    status: &'static str,
    score: f64,
    weight: f64,
    evidence: Vec<String>,
    remediation: String,
}

#[derive(Debug, Serialize)]
struct CategoryScore { score: f64, earned: f64, max: f64 }

#[derive(Debug, Serialize)]
struct Report {
    schema: &'static str,
    ruleset: String,
    root: String,
    overall: f64,
    grade: &'static str,
    level: &'static str,
    categories: BTreeMap<String, CategoryScore>,
    findings: Vec<Finding>,
}

fn collect_files(root: &Path) -> Vec<PathBuf> {
    WalkDir::new(root)
        .into_iter()
        .filter_entry(|e| {
            let n = e.file_name().to_string_lossy();
            n != ".git" && n != "target" && n != "node_modules" && n != "vendor"
        })
        .filter_map(Result::ok)
        .filter(|e| e.file_type().is_file())
        .filter_map(|e| e.path().strip_prefix(root).ok().map(PathBuf::from))
        .collect()
}

fn matches(files: &[PathBuf], patterns: &[String]) -> Result<Vec<String>> {
    let mut builder = GlobSetBuilder::new();
    for p in patterns { builder.add(Glob::new(p).with_context(|| format!("invalid glob: {p}"))?); }
    let set = builder.build()?;
    let mut out: Vec<String> = files.iter()
        .filter(|p| set.is_match(p))
        .map(|p| p.to_string_lossy().to_string())
        .collect();
    out.sort(); out.dedup(); Ok(out)
}

fn evaluate(root: &Path, files: &[PathBuf], rule: &Rule) -> Result<Finding> {
    let (passed, evidence) = match &rule.check {
        Check::AnyFile { patterns } => {
            let ev = matches(files, patterns)?;
            (!ev.is_empty(), ev)
        }
        Check::Contains { patterns, needles } => {
            let candidates = matches(files, patterns)?;
            let needles: Vec<String> = needles.iter().map(|n| n.to_lowercase()).collect();
            let mut ev = Vec::new();
            for rel in candidates {
                if let Ok(text) = fs::read_to_string(root.join(&rel)) {
                    let text = text.to_lowercase();
                    if needles.iter().any(|n| text.contains(n)) { ev.push(rel); }
                }
            }
            (!ev.is_empty(), ev)
        }
    };
    Ok(Finding {
        rule_id: rule.id.clone(), category: rule.category.clone(), title: rule.title.clone(),
        status: if passed { "PASS" } else { "FAIL" },
        score: if passed { rule.weight } else { 0.0 }, weight: rule.weight,
        evidence, remediation: rule.remediation.clone(),
    })
}

fn grade(s: f64) -> &'static str { if s >= 90.0 {"A"} else if s >= 80.0 {"B"} else if s >= 70.0 {"C"} else if s >= 60.0 {"D"} else {"E"} }
fn level(s: f64) -> &'static str { if s >= 90.0 {"L5 Optimizing"} else if s >= 80.0 {"L4 Resilient"} else if s >= 70.0 {"L3 Production"} else if s >= 55.0 {"L2 Managed"} else if s >= 35.0 {"L1 Repeatable"} else {"L0 Initial"} }
fn round1(v: f64) -> f64 { (v * 10.0).round() / 10.0 }

fn assess(root: &Path, rules: Ruleset) -> Result<Report> {
    let files = collect_files(root);
    let mut findings = Vec::new();
    for rule in &rules.rules { findings.push(evaluate(root, &files, rule)?); }

    let mut totals: BTreeMap<String, (f64, f64)> = BTreeMap::new();
    for f in &findings {
        let e = totals.entry(f.category.clone()).or_default();
        e.0 += f.score; e.1 += f.weight;
    }
    let mut categories = BTreeMap::new();
    let (mut earned, mut max) = (0.0, 0.0);
    for (name, (e, m)) in totals {
        categories.insert(name, CategoryScore { score: if m > 0.0 { round1(e / m * 100.0) } else { 0.0 }, earned: e, max: m });
        earned += e; max += m;
    }
    let overall = if max > 0.0 { round1(earned / max * 100.0) } else { 0.0 };
    Ok(Report {
        schema: "openforge-assessment/v0.1", ruleset: rules.version,
        root: root.canonicalize().unwrap_or_else(|_| root.to_path_buf()).display().to_string(),
        overall, grade: grade(overall), level: level(overall), categories, findings,
    })
}

fn print_text(r: &Report) {
    println!("OpenForge Maturity Assessment");
    println!("{}", "=".repeat(72));
    println!("Overall: {:>5.1} / 100   Grade: {}   {}", r.overall, r.grade, r.level);
    println!("{}", "-".repeat(72));
    for (name, c) in &r.categories { println!("{:<24} {:>5.1} / 100", name, c.score); }
    println!("{}", "-".repeat(72));
    for f in r.findings.iter().filter(|f| f.status == "FAIL") {
        println!("FAIL [{}] {} (+{} possible)", f.rule_id, f.title, f.weight);
        if !f.remediation.is_empty() { println!("     {}", f.remediation); }
    }
}

fn run() -> Result<i32> {
    let cli = Cli::parse();
    let root = cli.path.canonicalize().with_context(|| format!("invalid path: {}", cli.path.display()))?;
    let rules_text = match cli.rules { Some(p) => fs::read_to_string(&p).with_context(|| format!("cannot read rules: {}", p.display()))?, None => DEFAULT_RULES.to_string() };
    let rules: Ruleset = serde_json::from_str(&rules_text).context("invalid maturity ruleset")?;
    let report = assess(&root, rules)?;
    let json = serde_json::to_string_pretty(&report)?;
    if let Some(out) = &cli.output { fs::write(out, &json).with_context(|| format!("cannot write {}", out.display()))?; }
    match cli.format { OutputFormat::Text => print_text(&report), OutputFormat::Json => println!("{json}") }
    Ok(if cli.fail_under.is_some_and(|t| report.overall < t) { 2 } else { 0 })
}

fn main() -> ExitCode {
    match run() { Ok(code) => ExitCode::from(code as u8), Err(e) => { eprintln!("openforge: {e:#}"); ExitCode::FAILURE } }
}
