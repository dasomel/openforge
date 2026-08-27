use anyhow::{Context, Result};
use clap::{Args, Parser, Subcommand};
use std::{env, path::PathBuf, process::{Command, ExitCode}};

#[derive(Parser, Debug)]
#[command(name = "openforge-cli", version, about = "Unified OpenForge command frontend")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    Assess(Passthrough),
    Compare(Passthrough),
    Baseline {
        #[command(subcommand)]
        command: BaselineCommand,
    },
}

#[derive(Subcommand, Debug)]
enum BaselineCommand {
    Create(Passthrough),
    Check(Passthrough),
}

#[derive(Args, Debug)]
#[command(trailing_var_arg = true, allow_hyphen_values = true)]
struct Passthrough {
    #[arg(num_args = 0..)]
    args: Vec<String>,
}

fn sibling_binary(name: &str) -> Result<PathBuf> {
    let current = env::current_exe().context("cannot resolve current executable")?;
    let dir = current.parent().context("cannot resolve executable directory")?;
    let candidate = dir.join(name);
    if candidate.exists() {
        Ok(candidate)
    } else {
        Ok(PathBuf::from(name))
    }
}

fn run_child(binary: &str, args: &[String]) -> Result<i32> {
    let status = Command::new(sibling_binary(binary)?)
        .args(args)
        .status()
        .with_context(|| format!("cannot execute {binary}"))?;
    Ok(status.code().unwrap_or(1))
}

fn run() -> Result<i32> {
    let cli = Cli::parse();
    match cli.command {
        Commands::Assess(input) => run_child("openforge", &input.args),
        Commands::Compare(input) => {
            let mut args = vec!["compare".to_string()];
            args.extend(input.args);
            run_child("openforge", &args)
        }
        Commands::Baseline { command } => match command {
            BaselineCommand::Create(input) => {
                let mut args = vec!["create".to_string()];
                args.extend(input.args);
                run_child("openforge-baseline", &args)
            }
            BaselineCommand::Check(input) => {
                let mut args = vec!["check".to_string()];
                args.extend(input.args);
                run_child("openforge-baseline", &args)
            }
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
