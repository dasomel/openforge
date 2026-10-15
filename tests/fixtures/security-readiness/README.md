# Security-readiness fixtures

Every file here is a SYNTHETIC TEST FIXTURE for `tests/test_security_readiness.py`. The repository
`example/synthetic-repo`, its findings, the documented exception, and the re-scan correlation are
invented to exercise validation rules. They are not observations and must never be copied into
`portfolio/`. `valid-synthetic.json` passes (exception expires 2099-12-31); each `invalid-*.json`
breaks exactly one rule.

`synthetic-scorecard-v5.json` is a SYNTHETIC raw Scorecard v5 output for `example/synthetic-repo`, used by `tests/test_import_scorecard.py` together with `valid-synthetic.json`. It is not an observation of any repository.
