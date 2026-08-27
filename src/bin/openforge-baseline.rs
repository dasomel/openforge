use anyhow::{Context, Result};
use chrono::Utc;
use serde::{Deserialize, Serialize};
use serde_json::{Map, Value};
use std::{collections::BTreeMap, env, fs, path::{Path, PathBuf}, process::ExitCode};

#[derive(Debug, Deserialize)]
struct Assessment {
    schema: String,
    ruleset: String,
    overall: f64,
    #[serde(default)]
    policy: Option<PolicyIdentity>,
    #[serde(default)]
    findings: Vec<Finding>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
struct PolicyIdentity {
    profile: String,
    #[serde(default)]
    fingerprint: Option<String>,
}

#[derive(Debug, Deserialize)]
struct Finding {
    rule_id: String,
    status: String,
    score: f64,
}

#[derive(Debug, Serialize)]
struct BaselineMetadata {
    schema: &'static str,
    created_at: String,
    assessment_schema: String,
    ruleset: String,
    overall: f64,
    policy: Option<PolicyIdentity>,
}

fn read_value(path: &Path) -> Result<Value> {
    let text = fs::read_to_string(path)
        .with_context(|| format!("cannot read {}", path.display()))?;
    serde_json::from_str(&text)
        .with_context(|| format!("invalid assessment JSON: {}", path.display()))
}

fn read_assessment(path: &Path) -> Result<Assessment> {
    serde_json::from_value(read_value(path)?)
        .with_context(|| format!("invalid assessment structure: {}", path.display()))
}

fn create(assessment: &Path, output: &Path) -> Result<()> {
    let value = read_value(assessment)?;
    let mut object: Map<String, Value> = value
        .as_object()
        .cloned()
        .context("assessment JSON root must be an object")?;
    let identity: Assessment = serde_json::from_value(Value::Object(object.clone()))
        .context("assessment is missing identity fields")?;

    let metadata = BaselineMetadata {
        schema: "openforge-baseline/v0.1",
        created_at: Utc::now().to_rfc3339(),
        assessment_schema: identity.schema,
        ruleset: identity.ruleset,
        overall: identity.overall,
        policy: identity.policy,
    };
    object.insert("_baseline".to_string(), serde_json::to_value(metadata)?);

    if let Some(parent) = output.parent() {
        if !parent.as_os_str().is_empty() {
            fs::create_dir_all(parent)
                .with_context(|| format!("cannot create {}", parent.display()))?;
        }
    }
    fs::write(output, serde_json::to_string_pretty(&Value::Object(object))?)
        .with_context(|| format!("cannot write {}", output.display()))?;
    println!("Baseline created: {}", output.display());
    Ok(())
}

fn policy_same(left: &Option<PolicyIdentity>, right: &Option<PolicyIdentity>) -> bool {
    match (left, right) {
        (None, None) => true,
        (Some(left), Some(right)) => {
            left.profile == right.profile && left.fingerprint == right.fingerprint
        }
        _ => false,
    }
}

fn check(baseline: &Path, current: &Path, require_compatible: bool) -> Result<i32> {
    let before = read_assessment(baseline)?;
    let after = read_assessment(current)?;

    let mut compatible = true;
    if before.schema != after.schema {
        compatible = false;
        println!("WARN schema changed: {} -> {}", before.schema, after.schema);
    }
    if before.ruleset != after.ruleset {
        compatible = false;
        println!("WARN ruleset changed: {} -> {}", before.ruleset, after.ruleset);
    }
    if !policy_same(&before.policy, &after.policy) {
        compatible = false;
        println!("WARN policy identity changed");
    }

    let before_rules: BTreeMap<_, _> = before
        .findings
        .into_iter()
        .map(|finding| (finding.rule_id.clone(), finding))
        .collect();
    let after_rules: BTreeMap<_, _> = after
        .findings
        .into_iter()
        .map(|finding| (finding.rule_id.clone(), finding))
        .collect();

    let mut regressions = 0usize;
    let mut improvements = 0usize;
    for (rule_id, previous) in &before_rules {
        let Some(current) = after_rules.get(rule_id) else {
            continue;
        };
        if current.score < previous.score
            || (previous.status == "PASS" && current.status == "FAIL")
        {
            regressions += 1;
            println!(
                "REGRESSED [{rule_id}] {}({:.1}) -> {}({:.1})",
                previous.status, previous.score, current.status, current.score
            );
        } else if current.score > previous.score
            || (previous.status == "FAIL" && current.status == "PASS")
        {
            improvements += 1;
        }
    }

    println!(
        "Overall: {:.1} -> {:.1} ({:+.1})",
        before.overall,
        after.overall,
        after.overall - before.overall
    );
    println!(
        "Summary: compatible={} regressions={} improvements={}",
        compatible, regressions, improvements
    );

    if require_compatible && !compatible {
        return Ok(3);
    }
    if regressions > 0 {
        return Ok(2);
    }
    Ok(0)
}

fn run() -> Result<i32> {
    let args: Vec<String> = env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("create") => {
            let source = args.get(2).context("usage: openforge-baseline create <assessment.json> [output.json]")?;
            let output = args
                .get(3)
                .map(PathBuf::from)
                .unwrap_or_else(|| PathBuf::from(".openforge/baseline.json"));
            create(Path::new(source), &output)?;
            Ok(0)
        }
        Some("check") => {
            let baseline = args.get(2).context("usage: openforge-baseline check <baseline.json> <current.json> [--require-compatible]")?;
            let current = args.get(3).context("usage: openforge-baseline check <baseline.json> <current.json> [--require-compatible]")?;
            let require_compatible = args.iter().any(|arg| arg == "--require-compatible");
            check(Path::new(baseline), Path::new(current), require_compatible)
        }
        _ => anyhow::bail!(
            "usage: openforge-baseline create <assessment.json> [output.json]\n       openforge-baseline check <baseline.json> <current.json> [--require-compatible]"
        ),
    }
}

fn main() -> ExitCode {
    match run() {
        Ok(code) => ExitCode::from(code as u8),
        Err(error) => {
            eprintln!("openforge-baseline: {error:#}");
            ExitCode::FAILURE
        }
    }
}
