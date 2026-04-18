"""
Test DataObject initialization, __call__, and strict/non-strict modes.
:date_created: 2018-09-25
"""

import pytest

from do_py import DataObject
from do_py.common import R
from do_py.exceptions import DataObjectError

from ..data import A, data, short_data


class TestDataObjectInit:
    @pytest.mark.parametrize('id, name, status', data)
    def test_init(self, id, name, status):
        a = A.create(id=id, name=name, status=status)
        assert a, 'A.create returned a falsy value'
        assert a.id == id
        assert a.name == name
        assert a.status == status
        assert a['id'] == id
        assert a['name'] == name
        assert a['status'] == status
        assert a(data=a), '__call__ re-init failed'

    @pytest.mark.parametrize(
        'd, strict, key',
        [
            pytest.param(True, True, 'extra', marks=pytest.mark.xfail(raises=DataObjectError), id='d-strict-extra'),
            pytest.param(True, True, 'missing', marks=pytest.mark.xfail(raises=DataObjectError), id='d-strict-missing'),
            pytest.param(True, True, None, id='d-strict-None'),
            pytest.param(True, False, 'extra', marks=pytest.mark.xfail(raises=DataObjectError), id='d-!strict-extra'),
            pytest.param(True, False, 'missing', id='d-!strict-missing'),
            pytest.param(True, False, None, id='d-!strict-None'),
            pytest.param(False, True, None, marks=pytest.mark.xfail(raises=DataObjectError), id='!d-strict-None'),
            pytest.param(False, False, None, id='!d-!strict-None'),
        ],
    )
    def test_restrictions_runtime(self, d, strict, key):
        restric = {'id': R(0, 1, 2), 'x': R.INT.with_default(1), 'y': R()}

        class B(DataObject):
            _restrictions = restric

        data_ = {'id': 0, 'x': 2, 'y': 'hi'}
        if key == 'extra':
            data_['z'] = None
        elif key == 'missing':
            del data_['x']
        if not d:
            data_ = None
        b = B(data=data_, strict=strict)
        assert b, 'B() returned a falsy value'

    @pytest.mark.parametrize(
        'd, strict',
        [
            ('valid', True),
            pytest.param('invalid', True, marks=pytest.mark.xfail(reason='Data does not meet restrictions')),
            pytest.param(None, True, marks=pytest.mark.xfail(reason='Data does not meet restrictions')),
            pytest.param('partial', True, marks=pytest.mark.xfail(reason='Partial data not allowed when strict.')),
            ('valid', False),
            pytest.param('invalid', False, marks=pytest.mark.xfail(reason='Data does not meet restrictions')),
            (None, False),
            ('partial', False),
        ],
    )
    def test_strict(self, d, strict):
        if d == 'valid':
            d = {'id': short_data[0][0], 'name': short_data[0][1], 'status': short_data[0][2]}
        elif d == 'invalid':
            d = {'id': None, 'name': None, 'status': None}
        elif d == 'partial':
            d = {'id': 1}

        a = A(data=d, strict=strict)
        assert a, '__init__ failed!'
        assert a(data=d, strict=strict), '__call__ failed!'
