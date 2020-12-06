"""
Test managed restrictions.
:date_created: 2019-03-12
"""
import itertools as it
import pytest
from builtins import map, object, zip

from do_py.common import R
from do_py.data_object.restriction import ManagedRestrictions
from do_py.data_object.validator import Validator


class Name(ManagedRestrictions):
    """
    Manages name. Standardizes data to title case.
    """
    _restriction = R.STR

    def manage(self):
        self.data = self.data.title()


class Age(ManagedRestrictions):
    """
    Manages age. Validates and standardizes data.
    """
    _restriction = R.INT

    def manage(self):
        self.data = round(float(self.data), 1)
        assert 0.0 <= self.data <= 100.0, 'Invalid age'


city_state = {
    'TX': ['Dallas', 'Houston', 'Austin', 'San Antonio'],
    'CA': ['Los Angeles', 'San Francisco', 'San Deigo', 'Sacramento']
    }


class A(Validator):
    _restrictions = {
        'name': Name(),
        'age': Age(),
        'city': R(*[e for e in it.chain.from_iterable(city_state.values())]),
        'state': R(*city_state.keys())
        }

    def _validate(self):
        assert self.city in city_state[self.state], 'Mismatched city and state'


class TestManagedRestrictions(object):

    @pytest.fixture(params=['john smith'])
    def name(self, request):
        return request.param

    @pytest.fixture(params=[10.1, pytest.param(110.5, marks=pytest.mark.xfail(reason='Age out of bounds'))])
    def age(self, request):
        return request.param

    @pytest.fixture(params=[('Austin', 'TX'),
                            pytest.param(('Dallas', 'CA'),
                                         marks=pytest.mark.xfail(reason='Invalid combination'))])
    def city_state(self, request):
        return request.param

    def test_constructor(self, name, age, city_state):
        city, state = city_state
        a = A(data={'name': name, 'age': age, 'city': city, 'state': state})
        assert a.name == name.title()
        assert a.age == round(age, 1)

    @pytest.fixture(params=[21, pytest.param(110.5, marks=pytest.mark.xfail(reason='Age out of bounds'))])
    def new_age(self, request):
        return request.param

    @pytest.fixture(params=['Houston', pytest.param('Los Angeles', marks=pytest.mark.xfail(reason='Invalid city'))])
    def new_city(self, request):
        return request.param

    @pytest.fixture(params=[pytest.param('CA', marks=pytest.mark.xfail(reason='Invalid state'))])
    def new_state(self, request):
        return request.param

    @pytest.mark.parametrize('age', [20])
    @pytest.mark.parametrize('city', ['Dallas'])
    @pytest.mark.parametrize('state', ['TX'])
    def test_setattr(self, name, age, city, state, new_age, new_city, new_state):
        a = A(data={'name': name, 'age': age, 'city': city, 'state': state})
        a.age = new_age
        assert a.age == new_age
        a.city = new_city
        a.state = new_state

    @pytest.mark.parametrize('age', [20])
    @pytest.mark.parametrize('city', ['Dallas'])
    @pytest.mark.parametrize('state', ['TX'])
    def test_setitem(self, name, age, city, state, new_age, new_city, new_state):
        a = A(data={'name': name, 'age': age, 'city': city, 'state': state})
        a['age'] = new_age
        assert a['age'] == new_age
        a['city'] = new_city
        a['state'] = new_state

    @pytest.mark.parametrize('name', ['John Smith'])
    @pytest.mark.parametrize('age', [20])
    @pytest.mark.parametrize('city', ['Dallas'])
    @pytest.mark.parametrize('invalid_city', ['Los Angeles'])
    @pytest.mark.parametrize('valid_city', ['Houston'])
    @pytest.mark.parametrize('state', ['TX'])
    def test_recovery(self, name, age, city, state, valid_city, invalid_city):
        a = A(data={'name': name, 'age': age, 'city': city, 'state': state})
        try:
            a.city = invalid_city
        except Exception:
            pass

        f_attr = lambda kv: getattr(a, kv[0]) == kv[1]
        f_item = lambda kv: a[kv[0]] == kv[1]
        v1 = [city, age, name, state]
        v2 = [valid_city, age, name, state]
        k = ['city', 'age', 'name', 'state']

        for _k, _v, _city in [(k, v1, city), (k, v2, valid_city)]:
            a.city = _city
            assert all([e for e in map(f_attr, zip(_k, _v))]), 'Incorrect attrs'
            assert all([e for e in map(f_item, zip(_k, _v))]), 'Incorrect items'

    @pytest.mark.parametrize('name', ['John Smith'])
    @pytest.mark.parametrize('age', [20])
    @pytest.mark.parametrize('city', ['Dallas'])
    @pytest.mark.parametrize('invalid_city', ['Los Angeles'])
    @pytest.mark.parametrize('state', ['TX'])
    def test_data_corruption_robustness(self, name, age, invalid_city, city, state):
        a = A(data={'name': name, 'age': age, 'city': city, 'state': state})
        assert a.city == city
        try:
            a.city = invalid_city
            assert False
        except Exception:
            assert True

        assert a.city == city
