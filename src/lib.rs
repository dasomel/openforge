pub mod assessment;
pub mod baseline;
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
mod runtime_storage;
mod runtime_targets;

pub(crate) use assessment::Finding;

use anyhow::{Context, Result};
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
