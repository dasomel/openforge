use anyhow::{Context, Result};
use clap::{Args, Parser, Subcommand};
use std::{
    env,
    path::{Path, PathBuf},
    process::{Command, ExitCode},
};

#[derive(Parser, Debug)]
#[command(
    name = "openforge-cli",
    version,
    about = "Unified OpenForge command frontend"
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    Assess(Passthrough),
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

#[derive(Args, Debug)]
#[command(trailing_var_arg = true, allow_hyphen_values = true)]
struct Passthrough {
    #[arg(num_args = 0..)]
    args: Vec<String>,
}

fn sibling_binary(name: &str) -> Result<PathBuf> {
    let current = env::current_exe().context("cannot resolve current executable")?;
    let dir = current
        .parent()
        .context("cannot resolve executable directory")?;
    let candidate = dir.join(name);
    if candidate.exists() {
        Ok(candidate)
    } else {
        Ok(PathBuf::from(name))
    }
}

fn run_assess(args: &[String]) -> Result<i32> {
    let status = Command::new(sibling_binary("openforge")?)
        .args(args)
        .status()
        .context("cannot execute openforge assessment engine")?;
    Ok(status.code().unwrap_or(1))
}

fn run() -> Result<i32> {
    let cli = Cli::parse();
    match cli.command {
        Commands::Assess(input) => run_assess(&input.args),
        Commands::Compare {
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
        Commands::Baseline { command } => match command {
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
                Path::new(&baseline),
                Path::new(&current),
                fail_on_regression,
                require_compatible,
                json,
            ),
        },
    }
}

fn main() -> ExitCode {
    match run() {
        Ok(code) => ExitCode::from(code as u8),
        Err(error) => {
            eprintln!("openforge-cli: {error:#}");
            ExitCode::FAILURE
        }
    }
}
