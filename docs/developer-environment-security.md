# Developer Environment Security Standard

Developer workstations, IDEs, extensions, Git hooks and repository-local configuration are part of the OSS supply chain.

## Scope

- VS Code and compatible editors
- IDE extensions and marketplaces
- devcontainers and local images
- Git hooks and repository config
- task runners and local scripts
- `.vscode`, `.devcontainer`, agent configuration and instruction files
- local credentials and cloud contexts

## Rules

- Verify extension publisher/namespace and pin versions for reproducible development environments where practical.
- Treat new extensions, tools and plugins as third-party dependencies.
- Do not install extensions solely because a repository recommends a name; verify publisher identity.
- Pin devcontainer base images by immutable digest where practical.
- Review `Dockerfile`, `devcontainer.json`, editor tasks and workspace commands before execution.
- Treat repository configuration as executable input when it can trigger commands, downloads or hooks.
- Review Git hooks and custom `core.hooksPath` settings before enabling them.
- Do not persist production credentials in developer workspaces.
- Separate local, development, test and production credentials and contexts.
- Do not copy CI/release credentials into local agent environments.

## Repository-local executable files

Changes to the following SHOULD be treated as security-sensitive:

```text
.devcontainer/**
.vscode/**
.git/hooks/**
Makefile
Taskfile*
*.sh
package.json
AGENTS.md
CLAUDE.md
other agent configuration
```

## Verification

For new third-party developer tooling, record publisher/source, version, license, integrity information where available, required network access and whether the tool can execute arbitrary commands.

## Incident response

When a malicious extension/tool is suspected:

```text
stop use
→ isolate credentials
→ revoke exposed sessions/tokens
→ identify affected repositories/workspaces
→ remove/quarantine tool
→ inspect persistence/configuration
→ rotate credentials
→ document and add regression control
```
