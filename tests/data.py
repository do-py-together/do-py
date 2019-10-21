import pytest

from do import DataObject


class A(DataObject):
    _restrictions = {
        'id': ([int], None),
        'name': ([str, unicode], None),
        'status': ([0, 1, 2], None)
        }

    @classmethod
    def create(cls, **kwargs):
        return cls(data=kwargs)


data = [(1, 'pulseM', 0),
        (2, 'speetra', 2),
        pytest.mark.xfail((2, True, 2)),
        pytest.mark.xfail((2, 'pulseM', 3))]
short_data = [data[0]]
keys = ['id', 'name', 'status', pytest.mark.xfail('random')]
key_values = [('id', 1), ('name', 'yay'), ('status', 1),
              pytest.mark.xfail(('random', 'random'))]


class MyTestException(Exception):
    pass
