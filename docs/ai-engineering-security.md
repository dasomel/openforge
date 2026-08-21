# AI-Assisted Engineering Security Standard

AI coding agents, LLM tools and generated instructions are engineering inputs with execution authority. They must not be treated as trusted merely because they originate from an issue, repository, document or model.

## 1. Untrusted AI input

Treat the following as untrusted data by default:

- issues, PR descriptions and comments
- repository README and instruction files
- generated documentation and test fixtures
- external repositories and dependencies
- tool output, logs and retrieved documents

Instructions embedded in untrusted content MUST NOT override repository security, authorization or approval policy.

## 2. Agent permissions

- Give agents the minimum filesystem, shell, network, Git and credential permissions required for the task.
- Prefer ephemeral workspaces and isolated execution environments.
- Do not expose production credentials, long-lived publish tokens or unrelated SSH keys to general coding agents.
- Separate read-only analysis from mutation and release operations.
- High-impact operations require explicit human approval.

## 3. Shell and tool execution

- Validate commands structurally before execution where practical.
- Prefer allowlisted commands and restricted argument schemas over unrestricted shell execution.
- Do not allow natural-language output alone to authorize destructive operations.
- Treat command output as untrusted context.
- Network-enabled tools SHOULD use an allowlist and bounded timeouts.

## 4. Repository and workflow changes

AI-generated changes to the following require normal or elevated human review:

```text
.github/workflows/**
.github/actions/**
package manifests and lockfiles
Dockerfile / container build files
release and publishing scripts
security / OIDC configuration
RBAC / IAM configuration
```

AI agents MUST NOT bypass branch protection, required reviews or release approval.

## 5. Dependency changes

Dependency additions or upgrades proposed by agents follow the same dependency cooling, provenance, integrity and rollback rules as human-authored changes.

An agent recommendation is not evidence of package trust.

## 6. Prompt injection

- External documents, issues, logs and tool results may contain prompt injection.
- Separate policy/instructions from data/context.
- Use explicit trust labels for retrieved content.
- Never allow retrieved text to redefine permissions, approval requirements or execution targets.
- Include prompt-injection scenarios in security regression suites.

## 7. Release and publish boundary

AI agents MUST NOT receive unrestricted package publish, production deployment or security-administration authority.

Where agent-assisted release is supported:

```text
Agent proposal
→ validation
→ policy/security gates
→ human approval
→ isolated release job
→ publish
```

## 8. Evidence and reproducibility

Record, where practical:

- agent/tool identity and version
- model/provider identity when relevant
- repository revision
- prompt/instruction policy version
- tool calls or execution summary
- dependency changes
- human approval
- final artifact identity

## 9. Negative tests

Projects using AI-assisted engineering SHOULD maintain tests for:

- prompt injection from issues and documents
- malicious repository instructions
- unauthorized shell/tool execution
- secret access attempts
- unsafe workflow modification
- malicious dependency suggestion
- cross-project or cross-environment access
