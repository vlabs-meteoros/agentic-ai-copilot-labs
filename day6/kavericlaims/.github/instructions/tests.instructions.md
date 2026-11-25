---
applyTo: "tests/**/*.py"
description: How we write tests for KaveriClaims
---
# Tests in KaveriClaims

- Use **pytest**: plain functions named `test_...` with plain `assert`. No unittest classes.
- One behaviour per test, named after the rule it checks, for example `test_meal_over_daily_limit_is_capped`.
- Build small inputs inside the test (a few employees, a few claims) instead of reading `data/`.
  Only the golden test and the CLI integration tests read the real data files.
- Take expected values from `specs/policy.md`, not from the code. A test that copies the code's numbers can't find bugs.
- Use `@pytest.mark.parametrize` for tables of examples, and `pytest.raises` for errors.
- Compare money with `pytest.approx` (floats).
- `currency.RATES` is global. Set it with `monkeypatch.setattr(currency, "RATES", {...})` so tests can't affect each other.
- Use `tmp_path` for files a test writes. Never change `tests/golden/` to make a test pass.
