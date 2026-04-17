# Contributing

At its most basic level, a DataObject is built of something called a restricted dict mixin. A `RestrictedDictMixin` is
simply a class that inherits from python dict type. This just allows for certain parts of the built-in python dictionary
to be excluded to help prevent unwanted things from occurring. In this class it just takes several of the built-in
functions and turns them off.

## Development Setup

This project uses [mise](https://mise.jdx.dev) to manage the Python interpreter and
[uv](https://docs.astral.sh/uv/) for dependency management and builds.

### Environment

```bash
# One-time: install mise (https://mise.jdx.dev/installing-mise.html)
# Then, inside the repo:
mise install         # Installs Python and uv per mise.toml
mise run install     # uv sync --group dev
```

If you'd rather not use mise, uv alone is sufficient:

```bash
uv sync --group dev
```

### Testing

```bash
mise run test        # or: uv run pytest ./tests/
```

Code coverage reports for master, branches, and PRs are posted in
[CodeCov](https://codecov.io/gh/do-py-together/do-py).

### Linting

```bash
mise run lint        # or: uv run ruff check do_py tests
mise run format      # or: uv run ruff format do_py tests
```

Ruff config lives in `[tool.ruff]` in `pyproject.toml`. CI runs
`ruff check` on every PR.

### Building

```bash
mise run build       # uv build  -> sdist + wheel in ./dist
```

### Releasing

Releases are published to PyPI automatically via GitHub Actions using
[OIDC trusted publishing](https://docs.pypi.org/trusted-publishers/) —
no API tokens are stored in the repo.

To cut a release:

1. Bump `[project].version` in `pyproject.toml` on a PR, get it merged
   to `master`.
2. Update `CHANGELOG.md` with the release date and notes on the same
   PR (or a follow-up).
3. On GitHub, go to **Releases → Draft a new release**.
4. Create a new tag `vX.Y.Z` (matching the version in `pyproject.toml`)
   targeting `master`.
5. Fill in release notes (use the CHANGELOG section as a starting
   point) and click **Publish release**.
6. The `.github/workflows/release.yml` workflow runs automatically,
   builds sdist + wheel with `uv build`, and uploads to PyPI.

The release workflow verifies that the git tag matches
`pyproject.toml`'s version before publishing, so a mismatch will fail
fast instead of shipping wrong metadata.

If you need to publish locally (e.g. to TestPyPI) you can still run
`mise run publish` with a PyPI API token in `UV_PUBLISH_TOKEN`.

## Developer Notes

This section attempts to explain the inner workings of DataObject at a high level. Our intent is to assist anyone that
wants to develop on top of Do-Py and contribute to this project. More details can be found within the docstrings of our
files, classes, and functions.

```python
from do_py.abc import ABCRestrictions
from do_py.data_object import RestrictedDictMixin


@ABCRestrictions.require('_restrictions')
class DataObject(RestrictedDictMixin):
    """
    You will notice that in this DataObject there is an ABCRestrictions
    decorator, this simply states that the **_restrictions** attribute
    **must be present** in the DataObject. This is just a way of using a decorator
    to require certain items be present in the class. This helps to promote strictness
    so that a class cannot even be created without the proper attributes.
    """
```

### The `__init__` method.

A DataObject has a special '****init****' function that is responsible for a few things. It grabs the setting for
strict, and calls the `validate_data` function on itself. This is a very important function. Notice that we pass
validate_data 3 variables (not counting cls).

**d** stands for data in this case. This variable takes the data we pass in as a dictionary upon instantiation.

Finally, we have the variable **strict.** This is only used if the user wants to use strict=False instantiation.

Now we arrive at the validate_data function. If no data was passed in, we use an empty dictionary. Next we make sure we
have no unaccounted keys in the data that were not declared inside the _restrictions dictionary. We then check if the
keys inside the _restrictions dictionary belong to the data. An error will be raised in this case, unless strict=False.
In this case the default value for the restriction will be used and added to the **_dict** attribute. Once all the keys
have been checked they will all be inside the **_dict** assuming that there we no errors. Finally, we return _dict. So
whenever a DataObject is instantiated, you will receive a return containing a dictionary of all the data.

```python
from do_py import DataObject
from do_py.exceptions import DataObjectError, RestrictionError


# Below is the __init__ function for DataObject as well as its dependent validate data
def __init__(self, data=None, strict=True):
    self._strict = strict
    super(DataObject, self).__init__(self._validate_data(self._restrictions, data, strict=strict))
    # NOTE: Now that we are done loading, we go back to strict mode
    self._strict = True


@classmethod
def _validate_data(cls, _restrictions, d, strict=True):
    _dict = dict()
    d = {} if d is None else d
    # NOTE: Unrestricted keys are never allowed.
    for k in list(d.keys()):
        if k not in _restrictions:
            raise DataObjectError.from_unknown_key(k, cls)

    # NOTE: Use default in strict for missing keys in data.
    for k, v in _restrictions.items():
        if k not in d:
            if strict:
                raise DataObjectError.from_required_key(k, cls)
            else:
                _dict[k] = v.default
        else:
            try:
                _dict[k] = v(d[k], strict=strict)
            except RestrictionError as e:
                raise DataObjectError.from_restriction_error(k, cls, e)

    return _dict
```
