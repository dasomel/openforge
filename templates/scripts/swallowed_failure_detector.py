#!/usr/bin/env python3
"""Detect validators whose failure is unconditionally discarded.

The agent engineering audit already reports a false-green when repository instructions demand
deterministic verification and no executable owner exists. This module covers the other half:
an owner exists, runs, and has its verdict thrown away, so the job reports success while the
validator was reporting errors.

The whole difficulty is telling those apart from the many legitimate uses of the same shell
idiom. `grep ... || true` is not a swallowed failure -- grep's non-zero exit means "no match",
which is data. `markdownlint ... || true` is, because markdownlint's non-zero exit is a verdict
about the code. So the detector classifies the *program*, not the idiom, and refuses to guess:
an unrecognized program is never reported. A false positive here would be read as the audit
crying wolf and would cost more trust than the findings are worth.

This is a heuristic scanner, not a shell parser. It reads line-oriented structure and known
command shapes. Where it cannot be confident it stays quiet, and the escape-hatch comment
`# openforge: allow-swallow` exists for the cases it gets wrong.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional

__all__ = ["SwallowedFailure", "scan_repository", "scan_text"]


@dataclass(frozen=True)
class SwallowedFailure:
    """One validator whose non-zero exit cannot reach the caller."""

    path: str
    line: int
    command: str
    pattern: str
    reason: str


# ---------------------------------------------------------------------------
# Command classification
# ---------------------------------------------------------------------------

# Inclusion rule for this table: the program's non-zero exit is a VERDICT about the code, so
# discarding it discards the only signal the check produces. Anything whose non-zero exit is a
# data result (no match, not present, unreachable) belongs in NEVER_VALIDATORS instead.
VALIDATOR_PROGRAMS = frozenset(
    {
        "markdownlint",
        "markdownlint-cli2",
        "yamllint",
        "actionlint",
        "shellcheck",
        "hadolint",
        "tflint",
        "checkov",
        "semgrep",
        "trivy",
        "gitleaks",
        "codeql",
        "bandit",
        "pip-audit",
        "eslint",
        "stylelint",
        "tsc",
        "vitest",
        "jest",
        "pytest",
        "mypy",
        "ruff",
        "flake8",
        "pylint",
        "golangci-lint",
        "staticcheck",
        "govulncheck",
        "clippy-driver",
        "buf",
        "kubeconform",
        "kubeval",
    }
)

# Programs whose verdict depends on the subcommand or flags. Each entry maps a program to the
# argument patterns that make it a validator; anything else from that program stays unknown.
VALIDATOR_SUBCOMMANDS: dict[str, tuple[tuple[str, ...], ...]] = {
    "go": (("test",), ("vet",), ("build",)),
    "cargo": (("test",), ("clippy",), ("build",), ("audit",)),
    "npm": (("test",), ("audit",), ("run", "lint"), ("run", "test"), ("run", "typecheck"),
            ("run", "build"), ("run", "check"), ("run", "verify"), ("run", "ci")),
    "pnpm": (("test",), ("audit",), ("run", "lint"), ("run", "test"), ("run", "typecheck"),
             ("run", "build"), ("run", "check"), ("run", "verify"), ("run", "ci")),
    "yarn": (("test",), ("audit",), ("lint",), ("typecheck",), ("build",), ("check",), ("verify",)),
    "make": (("test",), ("lint",), ("verify",), ("check",), ("build",), ("ci",)),
    "dotnet": (("test",),),
    "mvn": (("verify",), ("test",)),
    "gradle": (("test",), ("check",), ("build",)),
    "bazel": (("test",), ("build",)),
    "terraform": (("validate",),),
    "helm": (("lint",),),
    "conftest": (("test",),),
    "playwright": (("test",),),
    "pre-commit": (("run",),),
    "biome": (("check",), ("ci",), ("lint",)),
    "shfmt": (("-d",), ("-l",)),
    "prettier": (("--check",),),
    "black": (("--check",),),
    "isort": (("--check",), ("--check-only",)),
    "gofmt": (("-l",),),
    "gofumpt": (("-l",),),
    "rustfmt": (("--check",),),
    "ruby": (("-c",),),
    "perl": (("-c",),),
    "php": (("-l",),),
    "node": (("--check",),),
    "bash": (("-n",),),
    "sh": (("-n",),),
    "kubectl": (("apply",),),  # only with --dry-run, checked separately
    "python": (("-m", "pytest"), ("-m", "unittest"), ("-m", "mypy"), ("-m", "ruff"),
               ("-m", "flake8"), ("-m", "black"), ("-m", "compileall")),
    "python3": (("-m", "pytest"), ("-m", "unittest"), ("-m", "mypy"), ("-m", "ruff"),
                ("-m", "flake8"), ("-m", "black"), ("-m", "compileall")),
}

# Programs whose non-zero exit is ordinary data or an expected absence. Neutralizing these is
# idiomatic and correct, and reporting them would bury the real findings.
NEVER_VALIDATORS = frozenset(
    {
        "grep", "rg", "ripgrep", "ag", "ack", "find", "ls", "cat", "head", "tail", "sed", "awk",
        "jq", "yq", "cut", "sort", "uniq", "wc", "tr", "xargs", "tee", "test", "[", "[[", "stat",
        "which", "type", "hash", "command", "pgrep", "pkill", "kill", "rm", "rmdir", "unlink",
        "mkdir", "mv", "cp", "touch", "chmod", "chown", "ln", "tar", "unzip", "zip", "curl",
        "wget", "ping", "nc", "dig", "nslookup", "sleep", "true", "false", "echo", "printf",
        "read", "env", "set", "export", "cd", "pushd", "popd", "source", ".", "diff", "cmp",
        "ps", "df", "du", "free", "uname", "id", "whoami", "journalctl", "dmesg", "open", "say",
        "date", "basename", "dirname", "realpath", "readlink", "mktemp", "sudo",
    }
)

# Subcommands that turn an otherwise-validating program into a data query or a cleanup.
NEVER_VALIDATOR_SUBCOMMANDS: dict[str, frozenset[str]] = {
    "docker": frozenset({"rm", "stop", "kill", "rmi", "network", "volume", "ps", "logs", "inspect"}),
    "kubectl": frozenset({"delete", "get", "describe", "logs", "wait", "rollout", "cordon", "drain",
                          "top", "exec", "port-forward"}),
    "git": frozenset({"rev-parse", "show-ref", "ls-files", "config", "remote", "fetch", "stash",
                      "diff", "log", "branch", "tag", "describe"}),
    "helm": frozenset({"status", "uninstall", "repo", "list", "get"}),
    "npm": frozenset({"ls", "list", "config", "prefix"}),
    "pip": frozenset({"show", "uninstall", "list", "freeze"}),
    "apt-get": frozenset({"remove", "purge"}),
    "brew": frozenset({"list", "uninstall"}),
    "systemctl": frozenset({"status", "is-active", "is-enabled"}),
    "yarn": frozenset({"install", "add", "remove", "why", "info", "cache", "config", "dlx",
                       "node", "npm", "pack", "patch", "plugin", "publish", "up", "workspaces"}),
}

# Wrappers that delegate to the real program; strip them before classifying.
COMMAND_WRAPPERS = frozenset({"sudo", "env", "time", "nice", "ionice", "npx", "uvx", "xvfb-run"})
# Two-token wrappers, e.g. `poetry run pytest`.
COMMAND_WRAPPER_PAIRS = frozenset({("poetry", "run"), ("bundle", "exec"), ("pipx", "run"),
                                   ("nix", "run"), ("uv", "run"), ("rye", "run")})

ENV_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=\S*$")


def _redirects_to_devnull(arguments: list[str]) -> bool:
    """True when the tokens redirect stdout (or all output) to `/dev/null`."""
    for index, token in enumerate(arguments):
        if token in (">", "&>", "1>", ">>", "&>>", "1>>") and index + 1 < len(arguments) \
                and arguments[index + 1] == "/dev/null":
            return True
        if token in (">/dev/null", "&>/dev/null", "1>/dev/null", ">>/dev/null"):
            return True
    return False


def _tokenize(command: str) -> list[str]:
    """Split a command into tokens, dropping quotes. Good enough for reading argv[0..2]."""
    return [token.strip("'\"") for token in command.strip().split()]


def _strip_wrappers(tokens: list[str]) -> list[str]:
    """Remove env assignments and delegating wrappers so argv[0] is the real program."""
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if ENV_ASSIGNMENT_RE.match(token):
            index += 1
            continue
        if token in COMMAND_WRAPPERS:
            index += 1
            continue
        if index + 1 < len(tokens) and (token, tokens[index + 1]) in COMMAND_WRAPPER_PAIRS:
            index += 2
            continue
        break
    return tokens[index:]


def classify_command(command: str) -> bool:
    """Return True only when the command's non-zero exit is a verdict about the code.

    Unknown programs return False. That is the deliberate asymmetry of this detector: the cost
    of a missed finding is one unreported false-green, while the cost of a false positive is a
    downstream repository concluding the whole matrix is noise. The validator table is the part
    that grows.
    """
    tokens = _strip_wrappers(_tokenize(command))
    if not tokens:
        return False

    program = tokens[0].rsplit("/", 1)[-1]
    arguments = tokens[1:]

    # `yq eval ... > /dev/null` is a syntax-check idiom (narwhal's `validate:` target): the
    # output is discarded and only the exit status is read. Without the redirect, yq is a data
    # query like any other NEVER_VALIDATORS entry, so this must stay narrower than the bare
    # program name.
    if program == "yq":
        return _redirects_to_devnull(arguments)

    if program in NEVER_VALIDATORS:
        return False

    never_subcommands = NEVER_VALIDATOR_SUBCOMMANDS.get(program)
    if never_subcommands and arguments and arguments[0] in never_subcommands:
        return False

    if program in VALIDATOR_PROGRAMS:
        return True

    # `kubectl apply` only validates with --dry-run; without it, it mutates a cluster.
    if program == "kubectl":
        return bool(arguments) and arguments[0] == "apply" and any(
            argument.startswith("--dry-run") for argument in arguments
        )

    for expected in VALIDATOR_SUBCOMMANDS.get(program, ()):
        if len(arguments) >= len(expected) and tuple(arguments[: len(expected)]) == expected:
            return True
        # Flag-style markers (`prettier --check`, `gofmt -l`) may appear anywhere in the args.
        if len(expected) == 1 and expected[0].startswith("-") and expected[0] in arguments:
            return True

    return False


# ---------------------------------------------------------------------------
# Shell-level neutralization
# ---------------------------------------------------------------------------

ALLOW_COMMENT_RE = re.compile(r"#\s*openforge:\s*allow-swallow\b")
OR_TRUE_RE = re.compile(r"\|\|\s*true\s*(?:#.*)?$")
OR_NOOP_RE = re.compile(r"\|\|\s*(?::|exit\s+0)\s*(?:#.*)?$")
FAILURE_GUARD_RE = re.compile(
    r"^\s*(?:if\s*!|if\s*\[\[?\s*[\"']?\$(?:\?|\{?[A-Za-z_][A-Za-z0-9_]*\}?)[\"']?\s*(?:-ne|!=)|trap\s)"
)
SET_PLUS_E_RE = re.compile(r"^set\s+\+[a-z]*e")
SET_MINUS_E_RE = re.compile(r"^set\s+-[a-z]*e")
STATUS_READ_RE = re.compile(r"\$\?|\bif\s*!|\|\|\s*exit\b|\bexit\s+\$|\breturn\s+\$|\[\s*\"?\$\{?(?:rc|status|exit_code|ret)\b")

# The "both branches succeed" shape (#91): `cmd && echo ok || echo fail` and its `if/then/else`
# equivalent both print a verdict but always exit 0, because the reporting command (`echo`,
# `printf`) is what determines the visible status. `[^;|]*?` keeps the `then` branch from
# swallowing the `||` that follows it.
AND_OR_ECHO_RE = re.compile(
    r"^(?P<pre>.*?)&&\s*(?:echo|printf)\b[^;|]*?\|\|\s*(?:echo|printf)\b"
)
IF_THEN_ELSE_ECHO_RE = re.compile(
    r"\bif\s+(?P<command>.+?)\s*;\s*then\s+(?:echo|printf)\b.*?;\s*else\s+(?:echo|printf)\b.*?;\s*fi\b"
)
# Propagation the loop/script may still do *after* the echo-branch line -- `exit $fail`,
# `exit "$rc"`, `exit ${status}`. A literal `exit 0`/`exit 1` inside the branches themselves
# does not count: those are the false-green shape, not a fix for it.
# `\$\$?` also matches a Makefile recipe's `$$fail` -- make collapses `$$` to a single `$`
# before the shell ever sees it, so the doubled form is the same propagation in that context.
EXIT_VAR_RE = re.compile(r"\bexit\s+\"?\$\$?\{?[A-Za-z_][A-Za-z0-9_]*\}?\"?")


def _strip_trailing_comment(text: str) -> str:
    """Drop a trailing `# ...` comment, ignoring `#` inside quotes."""
    quote: Optional[str] = None
    for index, character in enumerate(text):
        if quote:
            if character == quote:
                quote = None
        elif character in "'\"":
            quote = character
        elif character == "#" and (index == 0 or text[index - 1].isspace()):
            return text[:index]
    return text


def _command_before_neutralizer(text: str) -> str:
    """Return the command whose status the trailing `|| true` discards.

    A pipeline's exit status is its last element, so `markdownlint ... | tee log || true` still
    discards markdownlint's verdict -- the `tee` is irrelevant. Take the first element of the
    pipeline, and the last element of any `&&`/`;` sequence before it.
    """
    body = _strip_trailing_comment(text)
    body = re.sub(r"\|\|\s*(?:true|:|exit\s+0)\s*$", "", body).strip()
    # The neutralizer applies to the final command of a `&&`/`;` chain.
    for separator in ("&&", ";"):
        parts = _split_outside_quotes(body, separator)
        if len(parts) > 1:
            body = parts[-1].strip()
    # Within a pipeline the first element carries the verdict worth reporting.
    pipeline = _split_outside_quotes(body, "|")
    return pipeline[0].strip() if pipeline else body


def _split_outside_quotes(text: str, separator: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    quote: Optional[str] = None
    index = 0
    while index < len(text):
        character = text[index]
        if quote:
            current.append(character)
            if character == quote:
                quote = None
            index += 1
            continue
        if character in "'\"":
            quote = character
            current.append(character)
            index += 1
            continue
        if text.startswith(separator, index):
            # `||` must not be split as two `|` separators.
            if separator == "|" and text.startswith("||", index):
                current.append(text[index : index + 2])
                index += 2
                continue
            parts.append("".join(current))
            current = []
            index += len(separator)
            continue
        current.append(character)
        index += 1
    parts.append("".join(current))
    return parts


def _has_command_substitution_only(text: str, command: str) -> bool:
    """True when the neutralized command sits inside `$( ... )` rather than standing alone."""
    for match in re.finditer(r"\$\(([^()]*)\)", text):
        if command and command in match.group(1):
            return True
    return False


def _join_continuations(lines: list[str]) -> Iterator[tuple[int, str]]:
    """Yield (1-based line number of the command's FIRST line, joined logical line)."""
    buffer: list[str] = []
    start = 0
    for offset, raw in enumerate(lines, start=1):
        stripped = raw.rstrip("\n")
        if not buffer:
            start = offset
        if stripped.rstrip().endswith("\\"):
            buffer.append(stripped.rstrip()[:-1])
            continue
        buffer.append(stripped)
        yield start, " ".join(part.strip() for part in buffer).strip()
        buffer = []
    if buffer:
        yield start, " ".join(part.strip() for part in buffer).strip()


def _allowed(lines: list[str], index: int) -> bool:
    """Escape hatch: the marker on this line, or alone on the line above."""
    if ALLOW_COMMENT_RE.search(lines[index]):
        return True
    if index > 0:
        previous = lines[index - 1].strip()
        if previous.startswith("#") and ALLOW_COMMENT_RE.search(previous):
            return True
    return False


def _inside_failure_branch(lines: list[str], index: int) -> bool:
    """Heuristic: is this line inside a block that only runs after a failure was detected?

    Looks back a bounded number of lines for `if ! ...`, `if [ $? -ne 0 ]`, `if [ "$rc" -ne 0 ]`
    or a `trap` handler. It does not track block ends, so it errs toward suppressing -- which is
    the safe direction for a detector whose false positives are expensive.
    """
    for offset in range(index, max(-1, index - 12), -1):
        if FAILURE_GUARD_RE.match(lines[offset]):
            return True
    return False


def _last_statement(segment: str) -> str:
    """Return the final `;`-separated statement of `segment`, stripped of loop/recipe noise."""
    parts = _split_outside_quotes(segment, ";")
    candidate = parts[-1].strip() if parts else segment.strip()
    candidate = re.sub(r"^(?:do|then)\s+", "", candidate)
    return candidate.lstrip("@").strip()


def _detect_echo_branch_false_green(stripped: str) -> Optional[str]:
    """Return the validator command when every branch reporting its result also succeeds.

    Covers both `cmd && echo ok || echo fail` and `if cmd; then echo ok; else echo fail; fi`.
    Only the command, not the finding -- callers still run it through `classify_command` and
    the same escape hatches as every other pattern here.
    """
    match = AND_OR_ECHO_RE.match(stripped)
    if match:
        return _last_statement(match.group("pre"))
    match = IF_THEN_ELSE_ECHO_RE.search(stripped)
    if match:
        return match.group("command").strip()
    return None


SHELL_FUNCTION_DEF_RE = re.compile(r"^\s*(?:function\s+)?[A-Za-z_][A-Za-z0-9_]*\s*\(\)\s*\{")


def _block_tail(lines: list[str], start_index: int) -> list[str]:
    """Return the lines from `start_index` (0-based, inclusive) to the end of the enclosing block.

    Used to bound a forward search (e.g. for `exit $rc`-style propagation) to the block the
    line actually belongs to, instead of the rest of the file -- an unrelated `exit` in a later,
    unrelated Makefile target or shell function must not suppress an earlier finding.

    Makefile recipe lines are tab-indented, so a recipe's block ends at the first following line
    that has no leading tab (a new target, a blank line, or EOF). Plain shell content has no such
    convention; a generic indentation cutoff would also stop *inside* the same loop/if (e.g. at a
    `done`/`fi` that dedents relative to a nested branch), which is exactly the same-block case
    that must still suppress. So the boundary there is a new shell function definition (or EOF) --
    a flat, function-less script has no such boundary and keeps searching to EOF, same as before.
    """
    if start_index >= len(lines):
        return []
    start_line = lines[start_index]
    if start_line.startswith("\t"):
        end = start_index + 1
        while end < len(lines) and lines[end].startswith("\t"):
            end += 1
        return lines[start_index:end]
    end = start_index + 1
    while end < len(lines):
        if SHELL_FUNCTION_DEF_RE.match(lines[end]):
            break
        end += 1
    return lines[start_index:end]


def scan_text(text: str, path: str, *, line_offset: int = 0, in_failure_step: bool = False) -> list[SwallowedFailure]:
    """Scan shell-ish text for neutralized validators.

    `line_offset` maps the first line of `text` onto its absolute line number in the containing
    file, so findings from a YAML `run:` block point at the workflow file.
    """
    findings: list[SwallowedFailure] = []
    lines = text.splitlines()
    if in_failure_step:
        return findings

    set_plus_e_at: Optional[int] = None
    pending_set_plus_e: list[tuple[int, str]] = []
    pending_echo_branch: list[tuple[int, str]] = []

    logical = list(_join_continuations(lines))
    for start, joined in logical:
        index = start - 1
        stripped = joined.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if SET_PLUS_E_RE.match(stripped):
            set_plus_e_at = index
        elif SET_MINUS_E_RE.match(stripped):
            # `set -e` restores fail-fast, so anything before it was not actually unguarded.
            set_plus_e_at = None
            pending_set_plus_e.clear()

        neutralizer = None
        if OR_TRUE_RE.search(stripped):
            neutralizer = "or-true"
        elif OR_NOOP_RE.search(stripped):
            neutralizer = "or-noop"

        if neutralizer:
            command = _command_before_neutralizer(stripped)
            if (
                command
                and classify_command(command)
                and not _has_command_substitution_only(stripped, command)
                and not _allowed(lines, index)
                and not _inside_failure_branch(lines, index)
            ):
                findings.append(
                    SwallowedFailure(
                        path=path,
                        line=start + line_offset,
                        command=command[:200],
                        pattern=neutralizer,
                        reason="validator exit status is discarded, so a failing check still reports success",
                    )
                )
            continue

        echo_branch_command = _detect_echo_branch_false_green(stripped)
        if (
            echo_branch_command
            and classify_command(echo_branch_command)
            and not _allowed(lines, index)
            and not _inside_failure_branch(lines, index)
        ):
            # The exit-propagating fix (`exit $fail` after the loop) can only be seen by
            # looking forward, unlike every other pattern here -- defer the finding until the
            # rest of the script has been read.
            pending_echo_branch.append((start, echo_branch_command))

        if set_plus_e_at is not None and classify_command(stripped) and not _allowed(lines, index):
            pending_set_plus_e.append((start, stripped))

    for start, command in pending_echo_branch:
        tail = "\n".join(_block_tail(lines, start - 1))
        if EXIT_VAR_RE.search(tail):
            continue
        findings.append(
            SwallowedFailure(
                path=path,
                line=start + line_offset,
                command=command[:200],
                pattern="echo-branch",
                reason="every branch that reports the validator's result also exits 0, "
                "so a failing check still reports success",
            )
        )

    if pending_set_plus_e:
        tail = "\n".join(lines[pending_set_plus_e[0][0] :])
        if not STATUS_READ_RE.search(tail):
            for start, command in pending_set_plus_e:
                findings.append(
                    SwallowedFailure(
                        path=path,
                        line=start + line_offset,
                        command=command[:200],
                        pattern="unchecked-set-plus-e",
                        reason="`set +e` is in effect and the validator's exit status is never read",
                    )
                )

    return findings


# ---------------------------------------------------------------------------
# File-type scanners
# ---------------------------------------------------------------------------

RUN_KEY_RE = re.compile(r"^(?P<indent>\s*)(?:-\s+)?run:\s*(?P<inline>.*)$")
CONTINUE_ON_ERROR_RE = re.compile(r"^\s*(?:-\s+)?continue-on-error:\s*true\s*$")
STEP_IF_FAILURE_RE = re.compile(r"^\s*(?:-\s+)?if:\s*.*\b(?:failure|always)\(\)")
BLOCK_SCALAR_RE = re.compile(r"^[|>][-+]?\d*$")


LIST_ITEM_RE = re.compile(r"^(?P<indent>\s*)-\s+\S")


def _step_blocks(lines: list[str]) -> Iterator[tuple[int, int, int]]:
    """Yield (start, end, indent) for each YAML sequence item that looks like a job step.

    Step keys must be read within the step that owns them. An earlier version probed a fixed
    window of lines around each `run:`, which attributed one step's `continue-on-error: true`
    to its neighbours -- kube-ready-box's informational benchmark step made two unrelated steps
    look neutralized. A sequence item runs until the next `-` at the same indentation or the
    first line that dedents out of the list.
    """
    items: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        match = LIST_ITEM_RE.match(line)
        if match:
            items.append((index, len(match.group("indent"))))

    for position, (start, indent) in enumerate(items):
        end = len(lines)
        for probe in range(start + 1, len(lines)):
            line = lines[probe]
            if not line.strip():
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent < indent:
                end = probe
                break
            if current_indent == indent and LIST_ITEM_RE.match(line):
                end = probe
                break
        yield start, end, indent


JOB_STEPS_KEY_RE = re.compile(r"^(?P<indent>\s*)steps:\s*$")


def _job_level_continue_on_error(lines: list[str]) -> list[range]:
    """Line ranges covered by a job-level `continue-on-error: true`.

    A job-level setting neutralizes every step inside it, so it has to be read as well as the
    per-step one. The job header is the nearest preceding key that is less indented than its
    own `steps:`; anything between the two at the job's key indentation belongs to the job.
    """
    covered: list[range] = []
    for index, line in enumerate(lines):
        match = JOB_STEPS_KEY_RE.match(line)
        if not match:
            continue
        steps_indent = len(match.group("indent"))

        header = 0
        for probe in range(index - 1, -1, -1):
            probe_line = lines[probe]
            if not probe_line.strip():
                continue
            probe_indent = len(probe_line) - len(probe_line.lstrip())
            if probe_indent < steps_indent:
                header = probe
                break

        if any(CONTINUE_ON_ERROR_RE.match(lines[probe]) for probe in range(header, index)):
            end = len(lines)
            for probe in range(index + 1, len(lines)):
                probe_line = lines[probe]
                if not probe_line.strip():
                    continue
                if len(probe_line) - len(probe_line.lstrip()) < steps_indent:
                    end = probe
                    break
            covered.append(range(index, end))
    return covered


def _workflow_steps(lines: list[str]) -> Iterator[tuple[int, list[str], bool, bool]]:
    """Yield (first script line index, script lines, continue_on_error, if_failure) per `run:`.

    Written against line structure rather than a YAML parser: OpenForge installs no
    dependencies in CI, and the audit must run on a bare checkout.
    """
    job_level = _job_level_continue_on_error(lines)
    for block_start, block_end, indent in _step_blocks(lines):
        block = lines[block_start:block_end]
        continue_on_error = any(CONTINUE_ON_ERROR_RE.match(line) for line in block) or any(
            block_start in covered for covered in job_level
        )
        if_failure = any(STEP_IF_FAILURE_RE.match(line) for line in block)

        for offset, line in enumerate(block):
            match = RUN_KEY_RE.match(line)
            if not match:
                continue
            inline = match.group("inline").strip()
            run_indent = len(line) - len(line.lstrip())

            if inline and not BLOCK_SCALAR_RE.match(inline):
                yield block_start + offset, [inline], continue_on_error, if_failure
                continue

            script: list[str] = []
            script_start = block_start + offset
            body_indent: Optional[int] = None
            for probe in range(offset + 1, len(block)):
                body_line = block[probe]
                if not body_line.strip():
                    script.append("")
                    continue
                current_indent = len(body_line) - len(body_line.lstrip())
                if body_indent is None:
                    if current_indent <= run_indent:
                        break
                    body_indent = current_indent
                    script_start = block_start + probe
                if current_indent < body_indent:
                    break
                script.append(body_line[body_indent:])
            if script:
                yield script_start, script, continue_on_error, if_failure


MAKE_RECIPE_RE = re.compile(r"^\t\s*-\s*(?P<command>\S.*)$")


def scan_makefile(text: str, path: str) -> list[SwallowedFailure]:
    """Detect make's own swallow: a recipe line prefixed with `-` ignores the command's status."""
    findings: list[SwallowedFailure] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = MAKE_RECIPE_RE.match(line)
        if not match:
            continue
        command = _strip_trailing_comment(match.group("command")).strip()
        if not command or not classify_command(command) or _allowed(lines, index):
            continue
        findings.append(
            SwallowedFailure(
                path=path,
                line=index + 1,
                command=command[:200],
                pattern="or-true",
                reason="make's `-` recipe prefix ignores the command's exit status",
            )
        )
    findings.extend(scan_text(text, path))
    return findings


FENCE_RE = re.compile(r"^\s*```")
SHELL_FENCE_RE = re.compile(r"^\s*```\s*(bash|sh|shell|zsh|console|shell-session)?\s*$", re.I)


def scan_markdown(text: str, path: str) -> list[SwallowedFailure]:
    """Scan fenced code blocks only.

    Prose must never be pattern-matched: a standard that *describes* `|| true` as an
    anti-pattern would otherwise report itself.
    """
    findings: list[SwallowedFailure] = []
    lines = text.splitlines()
    inside = False
    block: list[str] = []
    block_start = 0
    for index, line in enumerate(lines):
        if FENCE_RE.match(line):
            if inside:
                findings.extend(scan_text("\n".join(block), path, line_offset=block_start))
                block = []
                inside = False
            else:
                inside = True
                block_start = index + 1
            continue
        if inside:
            block.append(line)
    if inside and block:
        findings.extend(scan_text("\n".join(block), path, line_offset=block_start))
    return findings


# ---------------------------------------------------------------------------
# Repository traversal
# ---------------------------------------------------------------------------

SKIP_DIRECTORIES = frozenset({".git", "node_modules", "__pycache__", ".venv", "venv",
                              ".pytest_cache", ".mypy_cache", "vendor", "dist", "build"})
INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", "CODING_STANDARDS.md")
COMMAND_DIRECTORIES = (".claude/commands/", ".agents/commands/")
MAKEFILE_NAMES = frozenset({"Makefile", "makefile", "GNUmakefile"})
SHELL_SUFFIXES = frozenset({".sh", ".bash"})
SHEBANG_RE = re.compile(r"^#!.*\b(?:bash|sh|zsh|dash|ksh)\b")
MAX_SHEBANG_DEPTH = 4


def _read(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError, ValueError):
        return None


def _walk(root: Path) -> Iterator[Path]:
    stack = [root]
    while stack:
        directory = stack.pop()
        try:
            entries = sorted(directory.iterdir(), key=lambda item: item.name)
        except OSError:
            continue
        for entry in entries:
            try:
                if entry.is_dir():
                    if entry.name not in SKIP_DIRECTORIES:
                        stack.append(entry)
                elif entry.is_file():
                    yield entry
            except OSError:
                continue


def _is_agent_command_markdown(relative: str) -> bool:
    """True for a Markdown file anywhere under an agent command directory.

    Nesting is included because a namespaced command (`.claude/commands/db/migrate.md`) is a
    verification recipe like any other. The prefixes carry a trailing slash, so a sibling
    directory such as `.claude/commandsfoo/` does not match.
    """
    return any(relative.startswith(prefix) for prefix in COMMAND_DIRECTORIES)


SCRIPT_KEY_RE_TEMPLATE = r'"{}"\s*:'


def _scan_package_json(text: str, path: str) -> list[SwallowedFailure]:
    """Scan a root `package.json`'s `scripts` values through the same classifier as shell text.

    `pyproject.toml` and `Cargo.toml` are deliberately not handled here: unlike `scripts`
    values, their build/test entries are not inline shell one-liners, so there is no
    comparable stdlib-parseable shell surface worth the added false-positive risk.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    # A bare array, number or null is valid JSON, so a successful decode does not mean an
    # object came back. This scanner runs over third-party repositories in CI, where one odd
    # manifest must not take the whole audit down with it.
    if not isinstance(data, dict):
        return []
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        return []

    lines = text.splitlines()
    scripts_key_line = next((i for i, line in enumerate(lines) if re.search(r'"scripts"\s*:', line)), None)
    fallback_line = scripts_key_line + 1 if scripts_key_line is not None else 1
    # Look only below the `scripts` key: a dependency sharing a script's name
    # (`"test": "^1.0.0"` in devDependencies) sits earlier and would claim the line number.
    search_from = scripts_key_line + 1 if scripts_key_line is not None else 0

    findings: list[SwallowedFailure] = []
    for name, command in scripts.items():
        if not isinstance(command, str):
            continue
        key_re = re.compile(SCRIPT_KEY_RE_TEMPLATE.format(re.escape(name)))
        line_no = next(
            (i + 1 for i, line in enumerate(lines) if i >= search_from and key_re.search(line)),
            fallback_line,
        )
        findings.extend(scan_text(command, path, line_offset=line_no - 1))
    return findings


def scan_repository(root: Path) -> list[SwallowedFailure]:
    """Scan a repository working tree. Deterministic, and never raises on unreadable files."""
    root = Path(root)
    findings: list[SwallowedFailure] = []

    for path in _walk(root):
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            continue
        name = path.name
        depth = relative.count("/")

        text: Optional[str] = None
        if relative.startswith(".github/workflows/") and path.suffix in {".yml", ".yaml"}:
            text = _read(path)
            if text is not None:
                findings.extend(_scan_workflow_text(text, relative))
            continue

        if relative == "package.json":
            text = _read(path)
            if text is not None:
                findings.extend(_scan_package_json(text, relative))
            continue

        if name in MAKEFILE_NAMES or path.suffix == ".mk":
            text = _read(path)
            if text is not None:
                findings.extend(scan_makefile(text, relative))
            continue

        if path.suffix in SHELL_SUFFIXES:
            text = _read(path)
            if text is not None:
                findings.extend(scan_text(text, relative))
            continue

        if name in INSTRUCTION_FILES or (name == "SKILL.md" and (
            relative.startswith(".agents/skills/") or relative.startswith(".claude/skills/")
        )) or (path.suffix == ".md" and _is_agent_command_markdown(relative)):
            text = _read(path)
            if text is not None:
                findings.extend(scan_markdown(text, relative))
            continue

        if not path.suffix and depth <= MAX_SHEBANG_DEPTH:
            text = _read(path)
            if text and SHEBANG_RE.match(text.splitlines()[0] if text.splitlines() else ""):
                findings.extend(scan_text(text, relative))

    findings.sort(key=lambda finding: (finding.path, finding.line, finding.pattern))
    return findings


def _scan_workflow_text(text: str, path: str) -> list[SwallowedFailure]:
    findings: list[SwallowedFailure] = []
    lines = text.splitlines()
    for script_start, script, continue_on_error, if_failure in _workflow_steps(lines):
        if if_failure:
            # The step runs only after something already failed; its commands are diagnostics.
            continue
        script_text = "\n".join(script)
        findings.extend(scan_text(script_text, path, line_offset=script_start))
        if continue_on_error:
            for offset, line in enumerate(script):
                command = _strip_trailing_comment(line).strip()
                if not command or not classify_command(command):
                    continue
                if _allowed(lines, min(script_start + offset, len(lines) - 1)):
                    continue
                findings.append(
                    SwallowedFailure(
                        path=path,
                        line=script_start + offset + 1,
                        command=command[:200],
                        pattern="continue-on-error",
                        reason="step declares continue-on-error, so the validator cannot fail the job",
                    )
                )
    return findings


def main() -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()

    findings = scan_repository(Path(arguments.path).resolve())
    if arguments.json:
        print(json.dumps([finding.__dict__ for finding in findings], indent=2))
    else:
        for finding in findings:
            print(f"{finding.path}:{finding.line} [{finding.pattern}] {finding.command}")
        print(f"swallowed validator findings: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
