"""
Tests for restrictions.
:date_created: 2019-05-10
:author: AJ
"""

from copy import deepcopy

import pytest

from do.exceptions import DataObjectError, RestrictionError
from do import DataObject
from do.data_object.restriction import ManagedRestrictions, _DataObjectRestriction, \
    _ListTypeRestriction, _ListValueRestriction, _MgdRestRestriction, Restriction, AbstractRestriction, \
    SingletonRestriction, _NullableDataObjectRestriction


class MgdRest(ManagedRestrictions):
    _restriction = ([], None)

    def manage(self):
        if self.data == 'bad':
            raise RestrictionError.bad_data(self.data, '')


class A(DataObject):
    _restrictions = {
        'x': ([int], None)
        }


class B(DataObject):
    _restrictions = {
        'x': ([1, 2, 3], None)
        }


class C(DataObject):
    _restrictions = {
        'v': ([1, 2, 3], None),
        'w': ([float, int], None),
        'x': [B, type(None)],
        'y': A,
        'z': MgdRest(),
        }


class TestRestriction(object):

    # def test_es_restrictions_override(self):
    #     r = {'type': 'text'}
    #
    #     class D(A):
    #         es_restrictions = {
    #             'x': r
    #             }
    #
    #     class E(DataObject):
    #         _restrictions = {
    #             'd': D
    #             }
    #
    #     assert E._restrictions['d'].es_restrictions == {'x': r}

    # @pytest.mark.parametrize('restriction', [
    #     pytest.param([int, float], marks=pytest.mark.xfail(reason='Ambiguous for ES restrictions',
    #                                                        raises=RestrictionError))])
    # def test_ambiguous_es_restriction(self, restriction):
    #     x = _ListTypeRestriction(restriction)
    #     assert x.es_restrictions, 'Failed'

    # @pytest.mark.parametrize('parent', [AbstractRestriction, SingletonRestriction])
    # def test_es_restriction(self, parent):
    #     try:
    #         parent(([int, float])).es_restrictions
    #         assert False
    #     except NotImplementedError:
    #         assert True

    def test_restriction_types(self):
        assert type(C._restrictions['v']) is _ListValueRestriction
        # assert C._restrictions['v'].es_restrictions == {'type': 'keyword'}
        assert type(C._restrictions['w']) is _ListTypeRestriction
        # NOTE: This is tested somewhere else. Int and float combination is ambiguous for ElasticSearch.
        # assert C._restrictions['w'].es_restrictions == {'type': 'keyword'}
        assert type(C._restrictions['x']) is _NullableDataObjectRestriction
        # assert C._restrictions['x'].es_restrictions == {'properties': {'x': {'type': 'keyword'}}}
        assert type(C._restrictions['y']) is _DataObjectRestriction
        # assert C._restrictions['y'].es_restrictions == {'properties': {'x': {'type': 'integer'}}}
        assert type(C._restrictions['z']) is _MgdRestRestriction
        # assert C._restrictions['z'].es_restrictions is None

    @pytest.mark.parametrize('data', [
        1, 2, 3, pytest.param(4, marks=pytest.mark.xfail(reason='Bad data', raises=RestrictionError))
        ])
    def test_list_values(self, data):
        assert C._restrictions['v'](data)

    @pytest.mark.parametrize('data', [
        1, 2.0, pytest.param('x', marks=pytest.mark.xfail(reason='Bad data', raises=RestrictionError))
        ])
    def test_list_types(self, data):
        assert C._restrictions['w'](data)

    @pytest.mark.parametrize('data', [
        1, 2, pytest.param(4, marks=pytest.mark.xfail(reason='Bad data', raises=DataObjectError))
        ])
    def test_do1(self, data):
        assert C._restrictions['x'](B(data={'x': data}))

    @pytest.mark.parametrize('data', [
        1, 2, pytest.param('x', marks=pytest.mark.xfail(reason='Bad data', raises=DataObjectError))
        ])
    def test_do2(self, data):
        assert C._restrictions['y'](A(data={'x': data}))

    @pytest.mark.parametrize('data', [
        'good', pytest.param('bad', marks=pytest.mark.xfail(reason='Bad data', raises=RestrictionError))
        ])
    def test_mr(self, data):
        assert C._restrictions['z'](data)

    @pytest.mark.parametrize('restriction', [
        pytest.param([A, B], marks=pytest.mark.xfail(reason='Two DOs', raises=RestrictionError)),
        pytest.param([int, 1], marks=pytest.mark.xfail(reason='Mixed types', raises=RestrictionError)),
        pytest.param([A, int, float], marks=pytest.mark.xfail(reason='DOs mixed with other types',
                                                              raises=RestrictionError)),
        pytest.param({A, int, float}, marks=pytest.mark.xfail(reason='Syntax error', raises=RestrictionError)),
        pytest.param(([A], int), marks=pytest.mark.xfail(reason='Default value error', raises=RestrictionError)),
                  ])
    def test_restriction_error(self, restriction):
        Restriction.legacy(restriction)

    @pytest.mark.parametrize('instance', [
        pytest.param(C._restrictions['v'],  # ListValue
                     marks=pytest.mark.xfail(reason='Singleton reuses memory locations')),
        pytest.param(C._restrictions['w'],  # ListType
                     marks=pytest.mark.xfail(reason='Singleton reuses memory locations')),
        pytest.param(C._restrictions['x'],  # NullableDO
                     marks=pytest.mark.xfail(reason='Singleton reuses memory locations')),
        pytest.param(C._restrictions['y'],  # DO
                     marks=pytest.mark.xfail(reason='Singleton reuses memory locations')),
        C._restrictions['z'],  # MgdRestr is not Singleton
        ])
    def test_deep_copy(self, instance):
        instance_copy = deepcopy(instance)
        assert instance == instance_copy
        assert id(instance_copy) != id(instance)
        assert isinstance(instance_copy, instance.__class__)

    def test_singleton(self):
        class Singletons(DataObject):
            _restrictions = {
                'v': ([1, 2, 3], None),
                'w': ([float, int], None),
                'x': [B, type(None)],
                'y': A,
                }

        for k in Singletons._restrictions:
            assert id(Singletons._restrictions[k]) == id(C._restrictions[k])
