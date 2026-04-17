"""
Test DataObject item/attribute access: __getattr__, __setitem__, __setattr__, get, dir.
:date_created: 2018-09-25
"""

import json

import pytest

from do_py import DataObject
from do_py.common import R

from ..data import A, keys, short_data


def our_hasattr(instance, name):
    """Check if *name* lives in the instance's own ``__dict__``."""
    return name in instance.__dict__


class TestSetItem:
    @pytest.mark.parametrize('id, name, status', short_data)
    def test_setitem_via_attr(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        a.id = 10
        assert not our_hasattr(a, 'id'), 'Restricted key should not be in attribute space'
        assert a['id'] == 10
        assert a.id == 10

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_setitem_via_bracket(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        a['id'] = 11
        assert a['id'] == 11
        assert a.id == 11

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_setitem_unrestricted_key_raises(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        with pytest.raises(KeyError):
            a['invalid'] = 'something'

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_attr_space_freeform(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        a.invalid = 'something'
        assert our_hasattr(a, 'invalid'), 'Attribute not found'
        assert 'invalid' not in a
        assert a.invalid == 'something'
        with pytest.raises(KeyError):
            _ = a['invalid']


class TestGet:
    @pytest.mark.parametrize('id, name, status', short_data)
    def test_get_methods(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        assert a.get('id') == a.id == id
        assert a.get('name') == a.name == name
        assert a.get('status') == a.status == status

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_bracket_missing_raises_key_error(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        with pytest.raises(KeyError):
            _ = a['nope']

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_attr_missing_raises_attribute_error(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        with pytest.raises(AttributeError):
            _ = a.nope

    @pytest.mark.parametrize('id, name, status', short_data)
    @pytest.mark.parametrize('key', keys)
    def test_get_not_none(self, id, name, status, key):
        a = A.create(id=id, name=name, status=status)
        assert a.get(key) is not None


class TestMutatingOpsBlocked:
    @pytest.mark.parametrize('id, name, status', short_data)
    def test_clear(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        with pytest.raises(TypeError):
            a.clear()

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_pop(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        with pytest.raises(TypeError):
            a.pop('id')

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_popitem(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        with pytest.raises(TypeError):
            a.popitem()

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_delitem(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        with pytest.raises(TypeError):
            del a['id']

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_update(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        with pytest.raises(TypeError):
            a.update({'id': 1})


class TestAttrRestrMutuallyExclusive:
    @pytest.mark.parametrize('id, name, status', short_data)
    def test_attr_restr_mutually_exclusive(self, id, name, status):
        """Restriction keys should not be in attr space. Non-key attributes should live in attribute space."""
        a = A.create(id=id, name=name, status=status)
        assert not any([our_hasattr(a, e) for e in A._restrictions.keys()])
        assert all([e in a for e in A._restrictions.keys()])
        a.x = 'x'
        a.y = 'y'
        attributes = ['x', 'y']
        assert all([our_hasattr(a, e) for e in attributes])
        assert not any([e in a for e in attributes])


class TestDir:
    @pytest.mark.parametrize('id, name, status', short_data)
    def test_dir_includes_restrictions(self, id, name, status):
        inst = A.create(id=id, name=name, status=status)
        for k in A._restrictions:
            assert k in dir(inst), 'Restriction key %r missing from dir()' % k
        assert 'create' in dir(inst), 'classmethod "create" missing from dir()'


class TestStrRepr:
    @pytest.mark.parametrize('complex', [pytest.param(True, marks=pytest.mark.xfail), False])
    def test_str_repr(self, complex):
        from datetime import date, datetime

        class B(DataObject):
            _restrictions = {'datetime': R.DATETIME, 'date': R.DATE, 'default': R()}

        class MyObj(dict):
            pass

        a = B(data={'datetime': datetime.now(), 'date': date.today(), 'default': MyObj if complex else 'hello world'})
        assert json.loads('%r' % a), '__repr__ did not produce valid JSON'
        assert '%s' % a, '__str__ produced empty string'

    def test_schema(self):
        schema = A.schema
        for k in A._restrictions:
            assert k in schema, 'Key %r missing from schema' % k
