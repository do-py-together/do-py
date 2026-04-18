"""
Test Validator edge cases: rollback on failure, strict=False, repeated failures.
:date_created: 2026-04-17
"""

import pytest

from do_py.common import R
from do_py.data_object.validator import Validator


class RangeValidator(Validator):
    """low must be <= high."""

    _restrictions = {'low': R.INT, 'high': R.INT}

    def _validate(self):
        assert self.low <= self.high, 'low must be <= high'


class TestValidatorRollback:
    """Verify state is restored after failed validation."""

    def test_setitem_rollback_on_failure(self):
        v = RangeValidator({'low': 1, 'high': 10})
        with pytest.raises(AssertionError):
            v['low'] = 20  # Would violate low <= high
        assert v.low == 1, 'State was not restored after failed setitem'
        assert v.high == 10

    def test_setattr_rollback_on_failure(self):
        v = RangeValidator({'low': 1, 'high': 10})
        with pytest.raises(AssertionError):
            v.high = 0  # Would violate low <= high
        assert v.high == 10, 'State was not restored after failed setattr'
        assert v.low == 1

    def test_setitem_success_after_rollback(self):
        """After a failed mutation, a valid mutation should succeed."""
        v = RangeValidator({'low': 1, 'high': 10})
        with pytest.raises(AssertionError):
            v.low = 20
        # Now a valid change should work fine
        v.low = 5
        assert v.low == 5

    def test_non_validated_key_still_triggers_validate(self):
        """Even setting a key that isn't directly checked should trigger _validate."""
        v = RangeValidator({'low': 1, 'high': 10})
        # Setting high to a value that violates the constraint
        with pytest.raises(AssertionError):
            v['high'] = 0
        assert v.high == 10


class TestValidatorStrictness:
    """Test strict vs non-strict initialization."""

    def test_strict_true_validates(self):
        """strict=True should call _validate."""
        with pytest.raises(AssertionError):
            RangeValidator({'low': 10, 'high': 1})

    def test_strict_false_skips_validate(self):
        """strict=False should NOT call _validate, allowing invalid data through."""
        v = RangeValidator(strict=False)
        assert v is not None
        # All values should be None (defaults)
        assert v.low is None
        assert v.high is None


class TestValidatorRepeatedFailures:
    """Verify object remains consistent after multiple sequential failures."""

    def test_multiple_failures_preserve_state(self):
        v = RangeValidator({'low': 1, 'high': 10})
        for bad_low in [20, 30, 40, 50]:
            with pytest.raises(AssertionError):
                v.low = bad_low
        assert v.low == 1, 'State corrupted after repeated failures'
        assert v.high == 10

    def test_alternating_success_and_failure(self):
        v = RangeValidator({'low': 1, 'high': 10})
        v.low = 3
        assert v.low == 3
        with pytest.raises(AssertionError):
            v.low = 20
        assert v.low == 3
        v.high = 5
        assert v.high == 5
        with pytest.raises(AssertionError):
            v.high = 2
        assert v.high == 5


class TestValidatorNotInstantiable:
    """Validator itself is abstract and cannot be directly instantiated."""

    def test_direct_instantiation_fails(self):
        with pytest.raises(NotImplementedError):
            Validator()
