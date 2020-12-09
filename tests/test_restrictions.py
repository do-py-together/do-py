"""
Tests for restrictions.
:date_created: 2019-05-10
:author: AJ
"""

from builtins import object
from copy import deepcopy

import pytest
from datetime import date, datetime

from do_py import DataObject
from do_py.common import R
from do_py.data_object.restriction import AbstractRestriction, ManagedRestrictions, SingletonRestriction, \
    _DataObjectRestriction, _ListTypeRestriction, _ListValueRestriction, _MgdRestRestriction, \
    _NullableDataObjectRestriction
from do_py.exceptions import DataObjectError, RestrictionError


class MgdRest(ManagedRestrictions):
    _restriction = R()

    def manage(self):
        if self.data == 'bad':
            raise RestrictionError.bad_data(self.data, '')


class SampleA(DataObject):
    _restrictions = {
        'x': R.INT
        }


class SampleB(DataObject):
    _restrictions = {
        'x': [1, 2, 3]
        }


class SampleC(DataObject):
    _restrictions = {
        'v': [1, 2, 3],
        'w': R.NULL_FLOAT,
        'x': R(SampleB, type(None)),
        'y': SampleA,
        'z': MgdRest(),
        }


class TestRestriction(object):

    def test_es_restrictions_override(self):
        r = {'type': 'text'}

        class SampleD(SampleA):
            es_restrictions = {
                'x': r
                }

        class SampleE(DataObject):
            _restrictions = {
                'd': SampleD
                }

        assert SampleE._restrictions['d'].es_restrictions == {'x': r}

    @pytest.mark.parametrize('restriction', [
        pytest.param([int, float], marks=pytest.mark.xfail(reason='Ambiguous for ES restrictions',
                                                           raises=RestrictionError))])
    def test_ambiguous_es_restriction(self, restriction):
        x = _ListTypeRestriction(restriction)
        assert x.es_restrictions, 'Failed'

    @pytest.mark.parametrize('parent', [AbstractRestriction, SingletonRestriction])
    def test_es_restriction(self, parent):
        restriction_tuple = ([int, type(None)], None)
        try:
            _ = parent(restriction_tuple).es_restrictions
            assert False
        except NotImplementedError:
            assert True

    @pytest.mark.parametrize('allowed, default', [(int, 1),
                                                  (float, 1.1),
                                                  (bool, True),
                                                  (date, date.today()),
                                                  (datetime, datetime.now()),
                                                  (dict, {'x': 1}),
                                                  (dict, SampleA(data={'x': 1})),
                                                  (list, [1, 2]),
                                                  (set, {1, 2}),
                                                  (str, 'A'),
                                                  (tuple, (1, 2))
                                                  ])
    def test_init_and_caching(self, allowed, default):
        instance_1 = R(allowed, default=default)
        assert instance_1
        instance_2 = R(allowed, default=default)
        assert id(instance_1) == id(instance_2)

    def test_restriction_types(self):
        assert type(SampleC._restrictions['v']) is _ListValueRestriction
        assert SampleC._restrictions['v'].es_restrictions == {'type': 'keyword'}
        assert type(SampleC._restrictions['w']) is _ListTypeRestriction
        # NOTE: This is tested somewhere else. Int and float combination is ambiguous for ElasticSearch.
        # assert C._restrictions['w'].es_restrictions == {'type': 'keyword'}
        assert type(SampleC._restrictions['x']) is _NullableDataObjectRestriction
        assert SampleC._restrictions['x'].es_restrictions == {'properties': {'x': {'type': 'keyword'}}}
        assert type(SampleC._restrictions['y']) is _DataObjectRestriction
        assert SampleC._restrictions['y'].es_restrictions == {'properties': {'x': {'type': 'integer'}}}
        assert type(SampleC._restrictions['z']) is _MgdRestRestriction
        assert SampleC._restrictions['z'].es_restrictions is None

    @pytest.mark.parametrize('data', [
        1, 2, 3, pytest.param(4, marks=pytest.mark.xfail(reason='Bad data', raises=RestrictionError))
        ])
    def test_list_values(self, data):
        assert SampleC._restrictions['v'](data)

    @pytest.mark.parametrize('data', [
        2.0, None, pytest.param('x', marks=pytest.mark.xfail(reason='Bad data', raises=RestrictionError))
        ])
    def test_list_types(self, data):
        assert SampleC._restrictions['w'](data) == data

    @pytest.mark.parametrize('data', [
        1, 2, pytest.param(4, marks=pytest.mark.xfail(reason='Bad data', raises=DataObjectError))
        ])
    def test_do1(self, data):
        assert SampleC._restrictions['x'](SampleB(data={'x': data}))

    @pytest.mark.parametrize('data', [
        1, 2, pytest.param('x', marks=pytest.mark.xfail(reason='Bad data', raises=DataObjectError))
        ])
    def test_do2(self, data):
        assert SampleC._restrictions['y'](SampleA(data={'x': data}))

    @pytest.mark.parametrize('data', [
        'good', pytest.param('bad', marks=pytest.mark.xfail(reason='Bad data', raises=RestrictionError))
        ])
    def test_mr(self, data):
        assert SampleC._restrictions['z'](data)

    @pytest.mark.parametrize('allowed, default', [
        pytest.param([SampleA, SampleB], None, marks=pytest.mark.xfail(reason='Two DOs', raises=RestrictionError)),
        pytest.param([int, 1], None, marks=pytest.mark.xfail(reason='Mixed types', raises=RestrictionError)),
        pytest.param([SampleA, int, float], None, marks=pytest.mark.xfail(reason='DOs mixed with other types',
                                                                          raises=RestrictionError)),
        pytest.param({SampleA, int, float}, None,
                     marks=pytest.mark.xfail(reason='Syntax error', raises=RestrictionError)),
        pytest.param([SampleA], int, marks=pytest.mark.xfail(reason='Default value error', raises=RestrictionError)),
        ])
    def test_restriction_error(self, allowed, default):
        assert R(*allowed, default=default)

    @pytest.mark.parametrize('instance', [
        pytest.param(SampleC._restrictions['v'],  # ListValue
                     marks=pytest.mark.xfail(reason='Singleton reuses memory locations')),
        pytest.param(SampleC._restrictions['w'],  # ListType
                     marks=pytest.mark.xfail(reason='Singleton reuses memory locations')),
        pytest.param(SampleC._restrictions['x'],  # NullableDO
                     marks=pytest.mark.xfail(reason='Singleton reuses memory locations')),
        pytest.param(SampleC._restrictions['y'],  # DO
                     marks=pytest.mark.xfail(reason='Singleton reuses memory locations')),
        SampleC._restrictions['z'],  # MgdRestr is not Singleton
        ])
    def test_deep_copy(self, instance):
        instance_copy = deepcopy(instance)
        assert instance == instance_copy
        assert id(instance_copy) != id(instance)
        assert isinstance(instance_copy, instance.__class__)

    def test_singleton(self):
        class Singletons(DataObject):
            _restrictions = {
                'v': R(1, 2, 3),
                'x': R(SampleB, type(None)),
                'y': SampleA
                }

        for k in Singletons._restrictions:
            assert id(Singletons._restrictions[k]) == id(SampleC._restrictions[k])
