use std::{path::Path, process::Command};

use crate::Finding;

pub(crate) struct ExecutionProbe {
    pub(crate) id: &'static str,
    pub(crate) title: &'static str,
    pub(crate) weight: f64,
    pub(crate) program: &'static str,
    pub(crate) args: &'static [&'static str],
    pub(crate) remediation: &'static str,
}

pub(crate) fn probes(root: &Path) -> Vec<ExecutionProbe> {
    if root.join("Cargo.toml").is_file() {
        return vec![
            ExecutionProbe {
                id: "EXE-RUST-001",
                title: "Rust project compiles",
                weight: 8.0,
                program: "cargo",
                args: &["check", "--all-targets", "--all-features"],
                remediation: "Fix compilation errors detected by cargo check.",
            },
            ExecutionProbe {
                id: "EXE-RUST-002",
                title: "Rust tests pass",
                weight: 8.0,
                program: "cargo",
                args: &["test", "--all-targets", "--all-features"],
                remediation: "Fix failing tests or document intentional exclusions.",
            },
            ExecutionProbe {
                id: "EXE-RUST-003",
                title: "Rust clippy passes without warnings",
                weight: 6.0,
                program: "cargo",
                args: &[
                    "clippy",
                    "--all-targets",
                    "--all-features",
                    "--",
                    "-D",
                    "warnings",
                ],
                remediation: "Resolve clippy warnings or narrowly justify lint exceptions.",
            },
        ];
    }

    if root.join("go.mod").is_file() {
        return vec![
            ExecutionProbe {
                id: "EXE-GO-001",
                title: "Go project compiles",
                weight: 8.0,
                program: "go",
                args: &["build", "./..."],
                remediation: "Fix compilation errors detected by go build.",
            },
            ExecutionProbe {
                id: "EXE-GO-002",
                title: "Go tests pass",
                weight: 8.0,
                program: "go",
                args: &["test", "./..."],
                remediation: "Fix failing Go tests or document intentional exclusions.",
            },
            ExecutionProbe {
                id: "EXE-GO-003",
                title: "Go vet passes",
                weight: 6.0,
                program: "go",
                args: &["vet", "./..."],
                remediation: "Resolve issues reported by go vet.",
            },
        ];
    }

    Vec::new()
}

fn compact_output(stdout: &[u8], stderr: &[u8]) -> Vec<String> {
    let stdout_text = String::from_utf8_lossy(stdout);
    let stderr_text = String::from_utf8_lossy(stderr);
    let mut lines: Vec<String> = stdout_text
        .lines()
        .chain(stderr_text.lines())
        .filter(|line| !line.trim().is_empty())
        .map(ToOwned::to_owned)
        .collect();

    if lines.len() > 8 {
        lines = lines.split_off(lines.len() - 8);
    }
    lines
}

fn run_probe(root: &Path, probe: &ExecutionProbe) -> Finding {
    let command_text = format!("{} {}", probe.program, probe.args.join(" "));
    let output = Command::new(probe.program)
        .args(probe.args)
        .current_dir(root)
        .output();

    match output {
        Ok(output) => {
            let passed = output.status.success();
            let mut evidence = vec![
                format!("command={command_text}"),
                format!("exit={}", output.status.code().unwrap_or(-1)),
            ];
            evidence.extend(compact_output(&output.stdout, &output.stderr));
            Finding {
                rule_id: probe.id.to_string(),
                category: "Execution".to_string(),
                title: probe.title.to_string(),
                status: if passed { "PASS" } else { "FAIL" },
                score: if passed { probe.weight } else { 0.0 },
                weight: probe.weight,
                evidence,
                remediation: probe.remediation.to_string(),
            }
        }
        Err(error) => Finding {
            rule_id: probe.id.to_string(),
            category: "Execution".to_string(),
            title: probe.title.to_string(),
            status: "FAIL",
            score: 0.0,
            weight: probe.weight,
            evidence: vec![format!("command={command_text}"), format!("error={error}")],
            remediation: format!(
                "{} Ensure '{}' is installed and available in PATH.",
                probe.remediation, probe.program
            ),
        },
    }
}

pub(crate) fn findings(root: &Path, enabled: bool) -> Vec<Finding> {
    let probes = probes(root);
    if probes.is_empty() {
        return Vec::new();
    }

    if !enabled {
        return probes
            .into_iter()
            .map(|probe| Finding {
                rule_id: probe.id.to_string(),
                category: "Execution".to_string(),
                title: probe.title.to_string(),
                status: "SKIP",
                score: 0.0,
                weight: probe.weight,
                evidence: vec!["execution disabled; pass --run-execution to enable".to_string()],
                remediation: probe.remediation.to_string(),
            })
            .collect();
    }

    probes.iter().map(|probe| run_probe(root, probe)).collect()
}
