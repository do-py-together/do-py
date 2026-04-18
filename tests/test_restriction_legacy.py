"""
Test Restriction.legacy edge cases and error message formatting.
:date_created: 2026-04-17
"""

import pytest

from do_py import DataObject, R
from do_py.data_object.restriction import (
    AbstractRestriction,
    ManagedRestrictions,
    Restriction,
    _DataObjectRestriction,
    _ListNoRestriction,
    _ListTypeRestriction,
    _ListValueRestriction,
    _MgdRestRestriction,
    _NullableDataObjectRestriction,
)
from do_py.exceptions import DataObjectError, RestrictionError


class SampleDO(DataObject):
    _restrictions = {'x': R.INT}


class SampleMgdRest(ManagedRestrictions):
    _restriction = R.STR

    def manage(self):
        pass


class TestRestrictionLegacy:
    """Test Restriction.legacy delegation paths."""

    def test_already_abstract_restriction_passthrough(self):
        """An existing AbstractRestriction should be returned as-is."""
        r = R.INT
        assert isinstance(r, AbstractRestriction)
        result = Restriction.legacy(r)
        assert result is r

    def test_managed_restrictions_instance(self):
        """ManagedRestrictions instance should be wrapped in _MgdRestRestriction."""
        mgd = SampleMgdRest()
        result = Restriction.legacy(mgd)
        assert isinstance(result, _MgdRestRestriction)

    def test_abc_restriction_meta(self):
        """ABCRestrictionMeta class should produce _DataObjectRestriction."""
        result = Restriction.legacy(SampleDO)
        assert isinstance(result, _DataObjectRestriction)

    def test_list_of_values(self):
        """Plain list of values should produce _ListValueRestriction."""
        result = Restriction.legacy([1, 2, 3])
        assert isinstance(result, _ListValueRestriction)

    def test_list_of_types_raises(self):
        """List of types in legacy format should raise RestrictionError."""
        with pytest.raises(RestrictionError):
            Restriction.legacy([int, float])

    def test_tuple_raises(self):
        """Legacy tuple format should raise RestrictionError."""
        with pytest.raises(RestrictionError):
            Restriction.legacy(([int], None))

    def test_set_raises(self):
        """Unsupported types like set should raise RestrictionError."""
        with pytest.raises(RestrictionError):
            Restriction.legacy({1, 2, 3})

    def test_empty_list(self):
        """Empty list should produce _ListNoRestriction."""
        result = Restriction.legacy([])
        assert isinstance(result, _ListNoRestriction)


class TestRestrictionFactory:
    """Test Restriction.__new__ dispatch paths."""

    def test_empty_list_produces_no_restriction(self):
        r = Restriction([], default=None)
        assert isinstance(r, _ListNoRestriction)

    def test_type_list_produces_list_type(self):
        r = Restriction([int, float])
        assert isinstance(r, _ListTypeRestriction)

    def test_value_list_produces_list_value(self):
        r = Restriction([1, 2, 3])
        assert isinstance(r, _ListValueRestriction)

    def test_do_produces_data_object_restriction(self):
        r = Restriction(SampleDO)
        assert isinstance(r, _DataObjectRestriction)

    def test_nullable_do_produces_nullable(self):
        r = Restriction([SampleDO, type(None)])
        assert isinstance(r, _NullableDataObjectRestriction)

    def test_type_default_raises(self):
        """A type as default value should raise."""
        with pytest.raises(RestrictionError):
            Restriction([int], default=int)


class TestRestrictionWithDefault:
    """Test the with_default method."""

    def test_with_default(self):
        r = R.INT
        r2 = r.with_default(42)
        assert r2.default == 42
        assert r.default is None  # Original unchanged


class TestErrorMessages:
    """Test error message factory methods produce well-formatted messages."""

    def test_data_object_error_unknown_key(self):
        e = DataObjectError.from_unknown_key('bad_key', SampleDO)
        assert 'bad_key' in str(e)
        assert 'SampleDO' in str(e)

    def test_data_object_error_required_key(self):
        e = DataObjectError.from_required_key('missing_key', SampleDO)
        assert 'missing_key' in str(e)
        assert 'SampleDO' in str(e)

    def test_data_object_error_from_restriction_error(self):
        inner = RestrictionError('inner error')
        e = DataObjectError.from_restriction_error('key', SampleDO, inner)
        assert 'key' in str(e)
        assert 'SampleDO' in str(e)
        assert 'inner error' in str(e)

    def test_restriction_error_bad_data(self):
        e = RestrictionError.bad_data('bad_val', [int, float])
        assert 'bad_val' in str(e)

    def test_restriction_error_mixed_value_and_type(self):
        e = RestrictionError.from_mixed_value_and_type([int, 1])
        assert 'Mixed' in str(e) or 'mixed' in str(e).lower()

    def test_restriction_error_unsupported(self):
        e = RestrictionError.from_unsupported({1, 2})
        assert 'Malformed' in str(e) or 'set' in str(e)

    def test_restriction_error_invalid_default(self):
        e = RestrictionError.from_invalid_default_value(int)
        assert 'int' in str(e)

    def test_restriction_error_dataobj_in_rstr_list(self):
        e = RestrictionError.from_dataobj_in_rstr_list([SampleDO, int])
        assert 'DataObject' in str(e)

    def test_restriction_error_unsupported_dataobj_in_rstr_list(self):
        e = RestrictionError.from_unsupported_dataobj_in_rstr_list([SampleDO, int])
        assert 'DataObject' in str(e)
