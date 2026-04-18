"""
Test RestrictedDictMixin behavior accessed through DataObject.
:date_created: 2026-04-17
"""

import json

import pytest

from do_py import DataObject, R


class Simple(DataObject):
    _restrictions = {'x': R.INT, 'y': R.STR}


class TestRestrictedDictRepr:
    """Test __repr__ returns valid JSON."""

    def test_repr_is_valid_json(self):
        s = Simple({'x': 1, 'y': 'hello'})
        result = json.loads(repr(s))
        assert result['x'] == 1
        assert result['y'] == 'hello'


class TestRestrictedDictStr:
    """Test __str__ format."""

    def test_str_contains_class_name(self):
        s = Simple({'x': 1, 'y': 'hello'})
        result = str(s)
        assert 'Simple' in result


class TestRestrictedDictDir:
    """Test __dir__ excludes unsupported operations."""

    def test_dir_excludes_mutating_ops(self):
        s = Simple({'x': 1, 'y': 'hello'})
        d = dir(s)
        for excluded in ['clear', 'pop', 'popitem', 'update', '__delitem__']:
            assert excluded not in d, '%s should be excluded from dir()' % excluded

    def test_dir_includes_restriction_keys(self):
        s = Simple({'x': 1, 'y': 'hello'})
        d = dir(s)
        assert 'x' in d
        assert 'y' in d


class TestRestrictedDictSetattr:
    """Test __setattr__ routing between key namespace and attribute namespace."""

    def test_setattr_restricted_key_routes_to_keyspace(self):
        s = Simple({'x': 1, 'y': 'hello'})
        s.x = 42
        assert s['x'] == 42
        assert 'x' not in s.__dict__

    def test_setattr_non_restricted_routes_to_attr(self):
        s = Simple({'x': 1, 'y': 'hello'})
        s.custom = 'value'
        assert s.custom == 'value'
        assert 'custom' in s.__dict__
        assert 'custom' not in s


class TestRestrictedDictGetattr:
    """Test __getattr__ behavior."""

    def test_getattr_restricted_key(self):
        s = Simple({'x': 1, 'y': 'hello'})
        assert s.x == 1
        assert s.y == 'hello'

    def test_getattr_missing_raises_attribute_error(self):
        s = Simple({'x': 1, 'y': 'hello'})
        with pytest.raises(AttributeError, match='nonexistent'):
            _ = s.nonexistent

    def test_getattr_raises_attribute_error_not_key_error(self):
        """__getattr__ should convert KeyError to AttributeError."""
        s = Simple({'x': 1, 'y': 'hello'})
        with pytest.raises(AttributeError):
            _ = s.nope
