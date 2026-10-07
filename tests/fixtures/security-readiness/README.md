# Security-readiness fixtures

Every file here is a SYNTHETIC TEST FIXTURE for `tests/test_security_readiness.py`. The repository
`example/synthetic-repo`, its findings, the documented exception, and the re-scan correlation are
invented to exercise validation rules. They are not observations and must never be copied into
`portfolio/`. `valid-synthetic.json` passes (exception expires 2099-12-31); each `invalid-*.json`
breaks exactly one rule.
