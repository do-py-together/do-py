"""
:date_created: 2019-08-20
"""

from builtins import object, str

import pytest

from do_py.abc import ABCRestrictionMeta, ABCRestrictions
from do_py.abc.constants import ConstABCR
from .data import MyTestException


class TestABCRestrictions(object):

    @pytest.mark.parametrize('def_new', [False, True])
    def test_require_decorator(self, def_new):
        def __new__():
            pass

        class MyMeta(type):
            pass

        teardown_classes = []  # Append to this everytime we ".require" decorate a class

        namespace = {'__module__': __name__}
        if def_new:
            namespace['__new__'] = classmethod(__new__)

        namespace[ConstABCR.is_abstract] = True

        RestrictedOk = ABCRestrictions.require('x')(type('RestrictedOk', tuple(), namespace))
        teardown_classes.append(RestrictedOk)
        assert RestrictedOk
        assert type(RestrictedOk) is ABCRestrictionMeta, 'Failed to apply ABCRestrictionMeta'
        assert RestrictedOk in ABCRestrictionMeta.abc_classes
        try:
            type('InvalidSubOk', (RestrictedOk,), {})
            raise Exception('Compile time validation failed!')
        except AssertionError:
            assert True
        SubOk = type('SubOk', (RestrictedOk,), {'x': 1, '__module__': __name__})
        assert SubOk
        assert SubOk.x == 1

        MiddleLayerOk = type('MiddleLayerOk', (RestrictedOk,), {ConstABCR.is_abstract: True,
                                                                '__module__': __name__})
        assert MiddleLayerOk
        assert 'x' not in MiddleLayerOk.__dict__

        # Additional and unique requirements
        try:
            ABCRestrictions.require('x')(MiddleLayerOk)
            raise MyTestException('Able to re-require a reserved namespace!')
        except MyTestException as e:
            assert False, str(e)
        except Exception:
            assert True

        UniqueOk = ABCRestrictions.require('y', unique=['y'])(MiddleLayerOk)
        teardown_classes.append(UniqueOk)
        UniqueSubOk = type('AdditionalSubOk', (UniqueOk,), {'x': 1, 'y': 2, '__module__': __name__})
        teardown_classes.append(UniqueSubOk)
        assert UniqueSubOk
        assert UniqueSubOk.x == 1
        assert UniqueSubOk.y == 2

        try:
            type('AdditionalSubOk2', (UniqueOk,), {'x': 1, 'y': 2, '__module__': __name__})
            raise MyTestException('Value check on unique attribute failed!')
        except MyTestException as e:
            assert False, str(e)
        except Exception:
            assert True

        # Reserved unique attribute namespace
        try:
            ABCRestrictions.require('y', unique=['y'])(MiddleLayerOk)
            raise MyTestException('Able to require uniqueness on a reserved namespace!')
        except MyTestException as e:
            assert False, str(e)
        except Exception:
            assert True

        # Teardown  # TODO: Support teardown on test failure too
        for cls in teardown_classes:
            if cls in ABCRestrictionMeta._abc_classes:
                ABCRestrictionMeta._abc_classes.remove(cls)
            for a in ABCRestrictionMeta._unique_attrs:
                if cls in ABCRestrictionMeta._unique_attrs[a]:
                    ABCRestrictionMeta._unique_attrs[a].remove(cls)

    @pytest.mark.parametrize('parent_class', sorted(ABCRestrictionMeta.abc_classes.keys(), key=lambda x: x.__name__))
    def test_not_instantiable(self, parent_class):
        try:
            obj = parent_class()
            assert False
        except NotImplementedError:
            assert True
        except Exception:
            assert False
