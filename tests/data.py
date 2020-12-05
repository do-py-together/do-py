import pytest

from do_py import DataObject
from do_py.common import R


class A(DataObject):
    _restrictions = {
        'id': R.INT,
        'name': R.STR,
        'status': R(0, 1, 2)
        }

    @classmethod
    def create(cls, **kwargs):
        return cls(data=kwargs)


data = [
    (1, 'pulseM', 0),
    (2, 'speetra', 2),
    pytest.param(2, True, 2, marks=pytest.mark.xfail),
    pytest.param(2, 'pulseM', 3, marks=pytest.mark.xfail)
    ]
short_data = [data[0]]
keys = [
    'id',
    'name',
    'status',
    pytest.param('random', marks=pytest.mark.xfail)
    ]
key_values = [
    ('id', 1),
    ('name', 'yay'),
    ('status', 1),
    pytest.param('random', 'random', marks=pytest.mark.xfail)
    ]


class MyTestException(Exception):
    pass
