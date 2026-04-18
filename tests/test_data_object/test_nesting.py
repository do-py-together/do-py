"""
Test nested DataObject restrictions and compile-time restriction validation.
:date_created: 2018-09-25
"""

import pytest

from do_py import DataObject
from do_py.common import R
from do_py.exceptions import DataObjectError, RestrictionError

from ..data import A


class TestNestedRestrictions:
    def test_nested_restrictions(self):
        class B(DataObject):
            _restrictions = {
                'x': R(1, 2),
                'y': R.INT.with_default(100),
            }

        class C(DataObject):
            _restrictions = {'a': A, 'b': B}

        data_ = {'a': {'id': 1, 'name': 'evil-jenkins', 'status': 0}, 'b': {'x': 1, 'y': 23}}
        c = C(data=data_)
        assert c
        assert c.get('a') == c['a'] == c.a
        assert type(c.a) is A
        assert c.a.id
        assert type(c.b) is B
        assert c.b.x

        # Test nested validation — invalid value for a restricted key
        with pytest.raises((RestrictionError, DataObjectError)):
            c.b.x = 'invalid'

        # Test nested validation — invalid data dict
        with pytest.raises(DataObjectError):
            c.b = {'invalid': 'values'}

        # Test default value behavior
        c_default = C(strict=False)
        assert c_default
        assert c_default.a
        assert type(c_default.a) is A
        assert type(c_default.b) is B
        for k, v in c_default.a.items():
            assert v is None, 'Expected None for key %r, got %r' % (k, v)

    @pytest.mark.parametrize('restrictions', [pytest.param(R(A, type(None)), id='([A, type(None)], None)'), A])
    def test_supported_nested_restrictions_format(self, restrictions):
        class B(DataObject):
            _restrictions = {'a': restrictions}

        class C(DataObject):
            _restrictions = {'b': B}

        c = C(data={'b': {'a': A(data={'id': 1, 'name': 'evil-jenkins', 'status': 0})}})
        assert c
        assert c.b
        assert c.b.a
        assert type(c.b.a) is A

    @pytest.mark.parametrize(
        'restrictions',
        [
            pytest.param((A, None), marks=pytest.mark.xfail(reason="'None' data not allowed for DO"), id='(A, None)'),
            pytest.param(A, marks=pytest.mark.xfail),
        ],
    )
    def test_null_nested_object(self, restrictions):
        class B(DataObject):
            _restrictions = {'a': restrictions}

        b = B(data={'a': None})
        assert b


class TestCompileTimeRestrictions:
    def test_class_namespace_clash(self):
        with pytest.raises(AttributeError):

            class B(DataObject):
                _restrictions = {'x': R.INT.with_default(1)}
                x = None

            B(data={'x': 1})

    @pytest.mark.parametrize(
        'deep',
        [
            pytest.param(True, marks=pytest.mark.xfail(raises=DataObjectError), id='deep'),
            pytest.param(False, id='!deep'),
        ],
    )
    def test_deep_restriction(self, deep):
        restric = {'id': [0, 1, 2], 'x': R.INT.with_default(1), 'y': []}
        if deep:
            restric['deep'] = {'this': [], 'fails': R(1, 2, 3, default=1)}

        class B(DataObject):
            _restrictions = restric

    @pytest.mark.xfail(raises=DataObjectError)
    def test_malformed_restrictions(self):
        class FailsMalformed(DataObject):
            _restrictions = {'malformed': None}

    @pytest.mark.xfail(raises=RestrictionError)
    def test_mixed_restrictions(self):
        class FailsMixed(DataObject):
            _restrictions = {'mixed': R(int, 1, 2)}

    @pytest.mark.parametrize('restriction', [[bool], ([bool], None)])
    @pytest.mark.xfail(raises=DataObjectError)
    def test_legacy_restrictions(self, restriction):
        class FailsLegacy(DataObject):
            _restrictions = {'legacy': restriction}

    @pytest.mark.xfail(raises=RestrictionError)
    def test_int_default(self):
        class FailsIntDefault(DataObject):
            _restrictions = {'int_default': R(default=int)}

    def test_missing_restrictions(self):
        with pytest.raises(AssertionError):

            class B(DataObject):
                pass

            B()

    def test_nesting_dict_restrictions(self):
        with pytest.raises(DataObjectError):

            class B(DataObject):
                _restrictions = {'a': {'x': [], 'y': []}}

            B(data={'a': {'x': 1, 'y': 2}})

    def test_multiple_dataobjs_not_allowed(self):
        class First(DataObject):
            _restrictions = {'id': R.INT}

        class Second(DataObject):
            _restrictions = {'id': R.INT}

        with pytest.raises(DataObjectError):
            type('Mixed', (DataObject,), {'_restrictions': {'id': [First, Second]}, '__module__': 'pytest'})
