use anyhow::{Context, Result};
use std::{
    env,
    path::{Path, PathBuf},
    process::ExitCode,
};

fn run() -> Result<i32> {
    let args: Vec<String> = env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("create") => {
            let source = args
                .get(2)
                .context("usage: openforge-baseline create <assessment.json> [output.json]")?;
            let output = args
                .get(3)
                .map(PathBuf::from)
                .unwrap_or_else(|| PathBuf::from(".openforge/baseline.json"));
            openforge::baseline_create(Path::new(source), &output)?;
            Ok(0)
        }
        Some("check") => {
            let baseline = args.get(2).context(
                "usage: openforge-baseline check <baseline.json> <current.json> [--fail-on-regression] [--require-compatible] [--json]",
            )?;
            let current = args.get(3).context(
                "usage: openforge-baseline check <baseline.json> <current.json> [--fail-on-regression] [--require-compatible] [--json]",
            )?;
            let fail_on_regression = args.iter().any(|arg| arg == "--fail-on-regression");
            let require_compatible = args.iter().any(|arg| arg == "--require-compatible");
            let json = args.iter().any(|arg| arg == "--json");
            openforge::baseline_check(
                Path::new(baseline),
                Path::new(current),
                fail_on_regression,
                require_compatible,
                json,
            )
        }
        _ => anyhow::bail!(
            "usage: openforge-baseline create <assessment.json> [output.json]\n       openforge-baseline check <baseline.json> <current.json> [--fail-on-regression] [--require-compatible] [--json]"
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
