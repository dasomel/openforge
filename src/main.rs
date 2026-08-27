use anyhow::{Context, Result};
use clap::{Args, Parser, Subcommand, ValueEnum};
use openforge::assessment::{self, AssessOptions};
use std::{env, fs, path::PathBuf, process::ExitCode};

#[derive(Copy, Clone, Debug, ValueEnum)]
enum OutputFormat {
    Text,
    Json,
}

#[derive(Args, Debug, Clone)]
struct AssessArgs {
    #[arg(default_value = ".")]
    path: PathBuf,

    #[arg(long, value_enum, default_value_t = OutputFormat::Text)]
    format: OutputFormat,

    #[arg(long)]
    output: Option<PathBuf>,

    #[arg(long)]
    rules: Option<PathBuf>,

    #[arg(
        long,
        help = "Built-in applicability profile: production, kubernetes-platform, oss-library, or repository."
    )]
    profile: Option<String>,

    #[arg(
        long,
        help = "JSON policy defining rule applicability and time-bounded waivers. When --profile is also set, explicit policy profile fields override the preset and waivers are added."
    )]
    policy: Option<PathBuf>,

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

    #[arg(
        long,
        help = "JSON spec containing explicit GET-only Kubernetes Service probes for post-restore functional verification."
    )]
    post_restore_spec: Option<PathBuf>,

    #[arg(
        long,
        help = "Explicit HTTP(S) image URL to probe with a read-only HEAD request for runtime cache headers."
    )]
    web_cache_url: Option<String>,
}

#[derive(Parser, Debug)]
#[command(
    name = "openforge",
    version,
    about = "Deterministic OSS and platform maturity assessment"
)]
struct UnifiedCli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand, Debug)]
enum Command {
    Assess(AssessArgs),
    Compare {
        before: PathBuf,
        after: PathBuf,
        #[arg(long, default_value = "text")]
        format: String,
        #[arg(long)]
        output: Option<PathBuf>,
        #[arg(long)]
        fail_on_regression: bool,
    },
    Baseline {
        #[command(subcommand)]
        command: BaselineCommand,
    },
}

#[derive(Subcommand, Debug)]
enum BaselineCommand {
    Create {
        assessment: PathBuf,
        #[arg(default_value = ".openforge/baseline.json")]
        output: PathBuf,
    },
    Check {
        baseline: PathBuf,
        current: PathBuf,
        #[arg(long)]
        fail_on_regression: bool,
        #[arg(long)]
        require_compatible: bool,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Parser, Debug)]
#[command(
    name = "openforge",
    version,
    about = "Deterministic OSS and platform maturity assessment"
)]
struct LegacyCli {
    #[command(flatten)]
    assess: AssessArgs,
}

fn resolved_policy_path(args: &AssessArgs) -> Result<(Option<PathBuf>, bool)> {
    let Some(profile) = args.profile.as_deref() else {
        return Ok((args.policy.clone(), false));
    };

    let json = openforge::resolve_profile_policy_json(profile, args.policy.as_deref())?;
    let path = env::temp_dir().join(format!("openforge-policy-{}.json", std::process::id()));
    fs::write(&path, json).with_context(|| {
        format!(
            "cannot materialize resolved profile policy: {}",
            path.display()
        )
    })?;
    Ok((Some(path), true))
}

fn run_assess(args: AssessArgs) -> Result<i32> {
    let (policy_path, temporary_policy) = resolved_policy_path(&args)?;
    let result = assessment::assess(
        &args.path,
        &AssessOptions {
            rules: args.rules.as_deref(),
            policy: policy_path.as_deref(),
            run_execution: args.run_execution,
            runtime: args.runtime,
            kube_context: args.kube_context.as_deref(),
            namespace: args.namespace.as_deref(),
            post_restore_spec: args.post_restore_spec.as_deref(),
            web_cache_url: args.web_cache_url.as_deref(),
        },
    );

    if temporary_policy {
        if let Some(path) = &policy_path {
            let _ = fs::remove_file(path);
        }
    }

    let report = result?;
    let json = serde_json::to_string_pretty(&report)?;
    if let Some(output) = &args.output {
        fs::write(output, &json).with_context(|| format!("cannot write {}", output.display()))?;
    }

    match args.format {
        OutputFormat::Text => assessment::print_text(&report),
        OutputFormat::Json => println!("{json}"),
    }

    Ok(
        if args
            .fail_under
            .is_some_and(|threshold| report.overall < threshold)
        {
            2
        } else {
            0
        },
    )
}

fn run_unified(cli: UnifiedCli) -> Result<i32> {
    match cli.command {
        Command::Assess(args) => run_assess(args),
        Command::Compare {
            before,
            after,
            format,
            output,
            fail_on_regression,
        } => openforge::compare_files(
            &before,
            &after,
            &format,
            output.as_deref(),
            fail_on_regression,
        ),
        Command::Baseline { command } => match command {
            BaselineCommand::Create { assessment, output } => {
                openforge::baseline_create(&assessment, &output)?;
                Ok(0)
            }
            BaselineCommand::Check {
                baseline,
                current,
                fail_on_regression,
                require_compatible,
                json,
            } => openforge::baseline_check(
                &baseline,
                &current,
                fail_on_regression,
                require_compatible,
                json,
            ),
        },
    }
}

fn run() -> Result<i32> {
    let args: Vec<String> = env::args().collect();
    let is_subcommand = args
        .get(1)
        .is_some_and(|arg| matches!(arg.as_str(), "assess" | "compare" | "baseline"));

    if is_subcommand {
        run_unified(UnifiedCli::parse_from(args))
    } else {
        run_assess(LegacyCli::parse_from(args).assess)
    }
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
