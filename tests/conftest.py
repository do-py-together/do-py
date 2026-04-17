"""
Shared fixtures for the do-py test suite.
"""

import pytest

from do_py.abc import ABCRestrictionMeta


@pytest.fixture()
def abc_cleanup():
    """
    Snapshot and restore ABCRestrictionMeta global state so that test-created
    classes never leak into other tests.
    """
    original_classes = set(ABCRestrictionMeta._abc_classes)
    original_uniques = {k: list(v) for k, v in ABCRestrictionMeta._unique_attrs.items()}
    yield
    ABCRestrictionMeta._abc_classes = original_classes
    ABCRestrictionMeta._unique_attrs = {k: list(v) for k, v in original_uniques.items()}
