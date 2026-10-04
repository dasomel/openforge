# OpenForge research evidence

This repository follows [the Research Evidence Collection Standard](../docs/research-evidence.md). Durable prospective records belong in `evidence/YYYY-MM.jsonl`; historical sources stay at their original paths and are registered in the [legacy evidence catalog](../portfolio/legacy-evidence-catalog.json).

Run `python3 scripts/research/record-evidence.py --task 'make test' --event-type test -- make test` to capture an observed command, then `make research-check` before publishing. Use `RESEARCH_EVIDENCE_DIR` for a disposable run. Keep failures and partial outcomes; do not estimate missing metrics. Existing schema exceptions, if any, are hash-pinned in `evidence/known-invalid.json` and must not be rewritten.
