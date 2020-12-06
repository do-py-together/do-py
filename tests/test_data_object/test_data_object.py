"""
Test resource base model.
:date_created: 2018-09-25
"""

import json
from builtins import object

import pytest

from do_py import DataObject
from do_py.common import R
from do_py.exceptions import DataObjectError, RestrictionError
from ..data import A, MyTestException, data, keys, short_data


def our_hasattr(instance, name):
    """

    :param instance:
    :param name:
    :return:
    """
    return name in instance.__dict__


class TestDataObject(object):

    @pytest.mark.parametrize('id, name, status', data)
    def test_init(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        assert a
        assert a.id == id
        assert a.name == name
        assert a.status == status
        assert a['id'] == id
        assert a['name'] == name
        assert a['status'] == status
        assert a(data=a)

    def test_class_namespace(self):
        try:
            class B(DataObject):
                _restrictions = {
                    'x': R.INT.with_default(1)
                    }
                x = None

            B(data={'x': 1})
            raise Exception('Failed to protect namespace clash between _restrictions and cls.x!')
        except AttributeError:
            assert True
        except Exception as e:
            assert False, str(e)

    @pytest.mark.parametrize('deep', [
        pytest.param(True, marks=pytest.mark.xfail(raises=DataObjectError), id='deep'),
        pytest.param(False, id='!deep')
        ])
    def test_deep_restriction(self, deep):
        restric = {
            'id': [0, 1, 2],
            'x': R.INT.with_default(1),
            'y': []
            }
        if deep:
            restric['deep'] = {
                'this': [],
                'fails': R(1, 2, 3, default=1)
                }

        class B(DataObject):
            _restrictions = restric

    @pytest.mark.xfail(raises=DataObjectError)
    def test_malformed_restrictions(self):
        class FailsMalformed(DataObject):
            _restrictions = {
                'malformed': None
                }

    @pytest.mark.xfail(raises=RestrictionError)
    def test_mixed_restrictions(self):
        class FailsMixed(DataObject):
            _restrictions = {
                'mixed': R(int, 1, 2)
                }

    @pytest.mark.parametrize('restriction', [
        [bool],
        ([bool], None)
        ])
    @pytest.mark.xfail(raises=DataObjectError)
    def test_legacy_restrictions(self, restriction):
        class FailsLegacy(DataObject):
            _restrictions = {
                'legacy': restriction
                }

    @pytest.mark.xfail(raises=RestrictionError)
    def test_int_default(self):
        class FailsIntDefault(DataObject):
            _restrictions = {
                'int_default': R(default=int)
                }

    @pytest.mark.parametrize('d, strict, key', [
        pytest.param(True, True, 'extra', marks=pytest.mark.xfail(raises=DataObjectError), id='d-strict-extra'),
        pytest.param(True, True, 'missing', marks=pytest.mark.xfail(raises=DataObjectError), id='d-strict-missing'),
        pytest.param(True, True, None, id='d-strict-None'),
        pytest.param(True, False, 'extra', marks=pytest.mark.xfail(raises=DataObjectError), id='d-!strict-extra'),
        pytest.param(True, False, 'missing', id='d-!strict-missing'),
        pytest.param(True, False, None, id='d-!strict-None'),
        pytest.param(False, True, None, marks=pytest.mark.xfail(raises=DataObjectError), id='!d-strict-None'),
        pytest.param(False, False, None, id='!d-!strict-None')
        ])
    def test_restrictions_runtime(self, d, strict, key):
        restric = {
            'id': R(0, 1, 2),
            'x': R.INT.with_default(1),
            'y': R()
            }

        class B(DataObject):
            _restrictions = restric

        data_ = {
            'id': 0,
            'x': 2,
            'y': 'hi'
            }
        if key == 'extra':
            data_['z'] = None
        elif key == 'missing':
            del data_['x']
        if not d:
            data_ = None
        b = B(data=data_, strict=strict)
        assert b

    def test_nested_restrictions(self):
        class B(DataObject):
            _restrictions = {
                'x': R(1, 2),
                'y': R.INT.with_default(100),
                }

        class C(DataObject):
            _restrictions = {
                'a': A,
                'b': B
                }

        data_ = {
            'a': {
                'id': 1,
                'name': 'evil-jenkins',
                'status': 0
                },
            'b': {
                'x': 1,
                'y': 23
                }
            }
        c = C(data=data_)
        assert c
        assert c.get('a') == c['a'] == c.a
        assert type(c.a) is A
        assert c.a.id
        assert type(c.b) is B
        assert c.b.x

        # Test nested validation
        try:
            c.b.x = 'invalid'
            raise MyTestException('Invalid value assigned to c.b.x!')
        except MyTestException as e:
            assert False, str(e)
        except Exception:
            assert True
        try:
            c.b = {'invalid': 'values'}
            raise MyTestException('Invalid data dict assigned to c.b!')
        except MyTestException as e:
            assert False, str(e)
        except Exception:
            assert True

        # Test default value behavior
        c_default = C(strict=False)
        assert c_default
        assert c_default.a
        assert type(c_default.a) is A
        assert type(c_default.b) is B
        for k, v in c_default.a.items():
            assert v is None, [(k, v) for k, v in c_default.a.items()]

    @pytest.mark.parametrize('restrictions', [
        pytest.param(R(A, type(None)), id='([A, type(None)], None)'),
        A])
    def test_supported_nested_restrictions_format(self, restrictions):
        class B(DataObject):
            _restrictions = {
                'a': restrictions
                }

        class C(DataObject):
            _restrictions = {
                'b': B
                }

        c = C(data={
            'b': {
                'a': A(data={
                    'id': 1,
                    'name': 'evil-jenkins',
                    'status': 0
                    })
                }
            })
        assert c
        assert c.b
        assert c.b.a
        assert type(c.b.a) is A

    @pytest.mark.parametrize('restrictions', [pytest.param((A, None),
                                                           marks=pytest.mark.xfail(
                                                               reason="'None' data not allowed for DO"),
                                                           id='(A, None)'),
                                              pytest.param(A, marks=pytest.mark.xfail)])
    def test_null_nested_object(self, restrictions):
        class B(DataObject):
            _restrictions = {
                'a': restrictions
                }

        b = B(data={'a': None})
        assert b

    def test_missing_restrictions(self):
        try:
            class B(DataObject):
                pass

            B()
            raise MyTestException('Error should have thrown.')
        except MyTestException as e:
            assert False, str(e)
        except Exception:
            assert True

    def test_nesting_dict_restrictions(self):
        try:
            class B(DataObject):
                _restrictions = {
                    'a': {
                        'x': [],
                        'y': []
                        }
                    }

            B(data={'a': {'x': 1, 'y': 2}})
            raise MyTestException('Error should have thrown.')
        except MyTestException as e:
            assert False, str(e)
        except Exception:
            assert True

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_setitem(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        new_id = 10
        a.id = new_id
        assert not our_hasattr(a, 'id'), 'Restricted key should not be in attribute space'
        assert a['id'] == new_id
        assert a.id == new_id

        newer_id = 11
        a['id'] = newer_id
        assert a['id'] == newer_id
        assert a.id == newer_id

        try:
            a['invalid'] = 'something'
            raise MyTestException('Able to assign a value to an unrestricted key!')
        except MyTestException as e:
            assert False, str(e)
        except Exception:
            assert True

        # Attribute space can be freeform, but will not become part of restricted data schema
        a.invalid = 'something'
        assert our_hasattr(a, 'invalid'), 'Attribute not found'
        assert 'invalid' not in a
        assert a.invalid == 'something'
        try:
            _ = a['invalid']
            raise MyTestException('Able to pull out value set in attribute namespace from keyspace!')
        except MyTestException as e:
            assert False, str(e)
        except Exception:
            assert True

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_get(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        assert a.get('id') == a.id == id
        assert a.get('name') == a.name == name
        assert a.get('status') == a.status == status
        try:
            _ = a['nope']
            assert False
        except KeyError:
            assert True
        try:
            _ = a.nope
            assert False
        except AttributeError:
            assert True

    @pytest.mark.parametrize('id, name, status', short_data)
    @pytest.mark.parametrize('key', keys)
    def test_get_2(self, id, name, status, key):
        a = A.create(id=id, name=name, status=status)
        assert a.get(key) is not None

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_clear_pop(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        try:
            a.clear()
            assert False
        except TypeError:
            assert True

        try:
            a.pop('id')
            assert False
        except TypeError:
            assert True

        try:
            a.popitem()
            assert False
        except TypeError:
            assert True

        try:
            del a['id']
            assert False
        except TypeError:
            assert True

        try:
            a.update({'id': 1})
            assert False
        except TypeError:
            assert True

    @pytest.mark.parametrize('complex', [pytest.param(True, marks=pytest.mark.xfail), False])
    def test_str_repr(self, complex):
        from datetime import date, datetime

        class B(DataObject):
            _restrictions = {
                'datetime': R.DATETIME,
                'date': R.DATE,
                'default': R()
                }

        class MyObj(dict):
            pass

        a = B(data={'datetime': datetime.now(), 'date': date.today(), 'default': MyObj if complex else 'hello world'})
        # __repr__ returns JSON
        assert json.loads('%r' % a)
        # __str__ returns string
        assert '%s' % a

    @pytest.mark.parametrize('d, strict', [
        ('valid', True),
        pytest.param('invalid', True, marks=pytest.mark.xfail(reason='Data does not meet restrictions')),
        pytest.param(None, True, marks=pytest.mark.xfail(reason='Data does not meet restrictions')),
        pytest.param('partial', True, marks=pytest.mark.xfail(reason='Partial data not allowed when strict.')),
        ('valid', False),
        pytest.param('invalid', False, marks=pytest.mark.xfail(reason='Data does not meet restrictions')),
        (None, False),
        ('partial', False)
        ])
    def test_strict(self, d, strict):
        if d == 'valid':
            d = {
                'id': short_data[0][0],
                'name': short_data[0][1],
                'status': short_data[0][2]
                }
        elif d == 'invalid':
            d = {
                'id': None,
                'name': None,
                'status': None
                }
        elif d == 'partial':
            d = {
                'id': 1
                }

        a = A(data=d, strict=strict)
        assert a, '__init__ failed!'
        assert a(data=d, strict=strict), '__call__ failed!'

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_attr_restr_mutually_exclusive(self, id, name, status):
        """
        Restriction keys should not be present in attr space. Not key attributes should live in attribute space.
        :return:
        :rtype:
        """
        a = A.create(id=id, name=name, status=status)
        assert not any([our_hasattr(a, e) for e in A._restrictions.keys()])
        assert all([e in a for e in A._restrictions.keys()])
        a.x = 'x'
        a.y = 'y'
        attributes = ['x', 'y']
        assert all([our_hasattr(a, e) for e in attributes])
        assert not any([e in a for e in attributes])

    def test_multiple_dataobjs_not_allowed(self):
        class First(DataObject):
            _restrictions = {'id': R.INT}

        class Second(DataObject):
            _restrictions = {'id': R.INT}

        try:
            type('Mixed',
                 (DataObject,),
                 {
                     '_restrictions': {'id': [First, Second]},
                     '__module__': 'pytest'
                     }
                 )
            raise MyTestException('Mixed Data Objects should not be allowed in restrictions')
        except DataObjectError:
            assert True

    @pytest.mark.parametrize('id, name, status', short_data)
    def test_dir(self, id, name, status):
        inst = A.create(id=id, name=name, status=status)
        for k in A._restrictions:
            assert k in dir(inst)

    def test_schema(self):
        schema = A.schema
        for k in A._restrictions:
            assert k in schema
