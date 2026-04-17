# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - Unreleased

First stable release. The 1.0 milestone reflects a comprehensive repo
modernization; the public API (`DataObject`, `R`, the exception classes)
is unchanged from 0.4.1 in behavior, but several foundational
environmental changes make this a breaking release.

### Breaking

- **Dropped Python 2 support.** The `future` and `past` compatibility
  shims are gone from the codebase. do-py is now a pure Python 3
  library.
- **Minimum Python version raised to 3.10.** Tested against 3.10, 3.11,
  3.12, and 3.13. Python 2.7 and 3.7–3.9 are no longer supported.
- **Removed `future>=0.18` runtime dependency.** do-py now has **zero**
  runtime dependencies.
- **Schema-value output cosmetic change.** `_ListTypeRestriction.schema_value`
  no longer hides the synthetic `newstr`/`newint`/`long` type names
  (those types can't appear anymore). In practice output is identical
  for all real-world restrictions.

### Added

- [PEP 561](https://peps.python.org/pep-0561/) `py.typed` marker so
  type checkers recognize the package (no annotations yet; surface is
  `Any`-typed).
- `__all__` declarations on `do_py/__init__.py`,
  `do_py/exceptions/__init__.py`, and `do_py/utils/__init__.py` to
  formalize the public API.
- `CHANGELOG.md` (this file).

### Changed

- **Build backend:** `setuptools` + `setup.py` + `MANIFEST.in` →
  [hatchling](https://hatch.pypa.io/latest/) via `pyproject.toml`
  ([PEP 621](https://peps.python.org/pep-0621/) metadata).
- **Dependency/env management:** `pipenv` + `Pipfile` → [uv](https://docs.astral.sh/uv/)
  + `pyproject.toml [dependency-groups]` ([PEP 735](https://peps.python.org/pep-0735/)).
  CI install time is roughly **3× faster**.
- **Developer tooling:** `yarn` + `package.json` + `release-it` (Node.js
  toolchain) → [mise](https://mise.jdx.dev) with tasks for install /
  test / lint / format / build / publish / clean.
- **Linter:** `pylint` (17KB `.pylintrc`, unused in CI) →
  [ruff](https://docs.astral.sh/ruff/) configured inline in `pyproject.toml`.
  Ruff also runs as a formatter (`quote-style = "single"` to preserve
  the codebase's existing convention).
- **CI:** GitHub Actions versions bumped to latest (checkout@v4,
  setup-uv@v5, codecov-action@v4). Matrix is now 3.10–3.13 with
  `fail-fast: false`.

### Fixed

- `DataObject.__deepcopy__` and `AbstractRestriction.__deepcopy__`
  had `memodict={}` as a default argument — a classic Python
  mutable-default bug. Now use the idiomatic `memodict=None` sentinel.
- Six exception-translation sites now use `raise X from e` so
  tracebacks preserve the original cause.
- Two `zip()` calls in the test suite now pass `strict=True` to catch
  accidental iterable-length mismatches.
- Broken code example in `README.md`: `Contact._restrictions` was a
  set literal (`{'phone_number'}`) rather than a dict, and the
  `VideoGame({...})` instantiation used keys that didn't exist on the
  class. Rewrote to a valid nested-DataObject example.

### Removed

- `setup.py`, `MANIFEST.in`, `Pipfile`, `Pipfile.lock`.
- `package.json`, `yarn.lock`, `node_modules/`, `.release-it.js`.
- `.pylintrc`, `tests/.coveragerc`.
- Zero-byte leftover `test.json` at repo root.
- `twine` pinned dev dependency (release is now `uv publish`).
- `from builtins import object`, `from future.*`, `from past.*`,
  `with_metaclass(...)`, `IS_PY3`, `newint`/`newstr`/`newlist`,
  `unicode`, `long` — all Python 2 compat shims.

### Infrastructure

- Dropped **~2000 lines** of Node.js dependency metadata from the
  repo (`yarn.lock`, 42 Dependabot vulnerabilities resolved).
- `_config.yml` and other incidental files preserved.

### Migration guide

For end users upgrading from 0.4.1:

- **If you're on Python 3.10+:** no code changes needed. `pip install
  -U do-py`.
- **If you're on Python 2.7 / 3.7 / 3.8 / 3.9:** pin to `do-py==0.4.1`
  or upgrade your interpreter. 0.4.1 remains available on PyPI for
  legacy workloads.
- **If you import Py2-compat internals** (`do_py.common.IS_PY3`,
  `newint`, `newstr` via `do_py.data_object.restriction`): these
  never were public API and are gone. Use native `int` / `str`.

For contributors:

- **Environment:** `mise install && mise run install` (or, without
  mise, `uv sync --group dev`).
- **Tests:** `mise run test` (or `uv run pytest ./tests/`).
- **Lint:** `mise run lint` (or `uv run ruff check do_py tests`).
- **Format:** `mise run format` (or `uv run ruff format do_py tests`).

## [0.4.1] - 2021-11-28

Previous release under the old `package.json`-tracked versioning.
See git history for details.

[1.0.0]: https://github.com/do-py-together/do-py/compare/v0.4.1...v1.0.0
[0.4.1]: https://github.com/do-py-together/do-py/releases/tag/v0.4.1
