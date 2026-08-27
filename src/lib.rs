pub mod assessment;
pub mod baseline;
pub mod calibration;
pub mod compare;

mod execution;
mod policy;
mod profiles;
mod runtime;
mod runtime_alertmanager;
mod runtime_backup;
mod runtime_certificates;
mod runtime_csi;
mod runtime_csi_nodes;
mod runtime_gitops;
mod runtime_metrics;
mod runtime_observability;
mod runtime_pod_security;
mod runtime_post_restore;
mod runtime_rbac;
mod runtime_restore;
mod runtime_scheduling;
mod runtime_stability;
mod runtime_storage;
mod runtime_targets;
mod web_assets;
mod web_cache;
mod web_cache_effectiveness;
mod web_cache_runtime;

pub(crate) use assessment::Finding;

use anyhow::{Context, Result};
use serde_json::json;
use std::{fs, path::Path};

pub fn compare_files(
    before: &Path,
    after: &Path,
    format: &str,
    output: Option<&Path>,
    fail_on_regression: bool,
) -> Result<i32> {
    let comparison = compare::compare(before, after)?;
    let json = serde_json::to_string_pretty(&comparison)?;

    if let Some(path) = output {
        fs::write(path, &json).with_context(|| format!("cannot write {}", path.display()))?;
    }

    match format {
        "json" => println!("{json}"),
        "text" => compare::print_text(&comparison),
        other => anyhow::bail!("unsupported compare format: {other}"),
    }

    Ok(if fail_on_regression && comparison.summary.regressed > 0 {
        2
    } else {
        0
    })
}

pub fn calibrate_files(
    assessment: &Path,
    manifest: &Path,
    format: &str,
    output: Option<&Path>,
    require_complete: bool,
) -> Result<i32> {
    let report = calibration::calibrate(assessment, manifest)?;
    let json = serde_json::to_string_pretty(&report)?;

    if let Some(path) = output {
        fs::write(path, &json).with_context(|| format!("cannot write {}", path.display()))?;
    }

    match format {
        "json" => println!("{json}"),
        "text" => calibration::print_text(&report),
        other => anyhow::bail!("unsupported calibration format: {other}"),
    }

    Ok(
        if require_complete && report.summary.unclassified_rules > 0 {
            2
        } else {
            0
        },
    )
}

pub fn baseline_create(assessment: &Path, output: &Path) -> Result<()> {
    baseline::create(assessment, output)
}

pub fn baseline_check(
    baseline_path: &Path,
    current: &Path,
    fail_on_regression: bool,
    require_compatible: bool,
    json: bool,
) -> Result<i32> {
    baseline::check(
        baseline_path,
        current,
        fail_on_regression,
        require_compatible,
        json,
    )
}

pub fn resolve_profile_policy_json(
    profile_name: &str,
    override_policy_path: Option<&Path>,
) -> Result<String> {
    let base = profiles::builtin(profile_name)?;
    let resolved = match override_policy_path {
        Some(path) => profiles::overlay(base, policy::load(path)?),
        None => base,
    };

    let waivers: Vec<_> = resolved
        .waivers
        .iter()
        .map(|waiver| {
            json!({
                "rule_id": waiver.rule_id,
                "reason": waiver.reason,
                "expires": waiver.expires,
            })
        })
        .collect();

    Ok(serde_json::to_string_pretty(&json!({
        "profile": {
            "name": resolved.profile.name,
            "include_rules": resolved.profile.include_rules,
            "exclude_rules": resolved.profile.exclude_rules,
        },
        "waivers": waivers,
    }))?)
}
