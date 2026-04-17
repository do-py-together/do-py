"""
:date_created: 2019-08-20
"""

import pytest

from do_py.abc import ABCRestrictionMeta, ABCRestrictions
from do_py.abc.constants import ConstABCR


@pytest.fixture()
def _abc_cleanup():
    """
    Snapshot and restore ABCRestrictionMeta global state so that test-created
    classes never leak into other tests.
    """
    original_classes = set(ABCRestrictionMeta._abc_classes)
    original_uniques = {k: list(v) for k, v in ABCRestrictionMeta._unique_attrs.items()}
    yield
    ABCRestrictionMeta._abc_classes = original_classes
    ABCRestrictionMeta._unique_attrs = {k: list(v) for k, v in original_uniques.items()}


@pytest.mark.usefixtures('_abc_cleanup')
class TestABCRestrictions:
    @pytest.mark.parametrize('def_new', [False, True])
    def test_require_decorator(self, def_new):
        def __new__():
            pass

        class MyMeta(type):
            pass

        namespace = {'__module__': __name__}
        if def_new:
            namespace['__new__'] = classmethod(__new__)

        namespace[ConstABCR.is_abstract] = True

        RestrictedOk = ABCRestrictions.require('x')(type('RestrictedOk', tuple(), namespace))
        assert RestrictedOk, 'ABCRestrictions.require failed to return a class'
        assert type(RestrictedOk) is ABCRestrictionMeta, 'Failed to apply ABCRestrictionMeta'
        assert RestrictedOk in ABCRestrictionMeta.abc_classes

        # Leaf without required attribute must fail
        with pytest.raises(AssertionError):
            type('InvalidSubOk', (RestrictedOk,), {})

        SubOk = type('SubOk', (RestrictedOk,), {'x': 1, '__module__': __name__})
        assert SubOk, 'Leaf class creation failed'
        assert SubOk.x == 1

        MiddleLayerOk = type('MiddleLayerOk', (RestrictedOk,), {ConstABCR.is_abstract: True, '__module__': __name__})
        assert MiddleLayerOk, 'Node class creation failed'
        assert 'x' not in MiddleLayerOk.__dict__

        # Re-requiring on a reserved namespace must fail
        with pytest.raises(AssertionError):
            ABCRestrictions.require('x')(MiddleLayerOk)

        UniqueOk = ABCRestrictions.require('y', unique=['y'])(MiddleLayerOk)
        UniqueSubOk = type('AdditionalSubOk', (UniqueOk,), {'x': 1, 'y': 2, '__module__': __name__})
        assert UniqueSubOk, 'Leaf with additional unique attr failed'
        assert UniqueSubOk.x == 1
        assert UniqueSubOk.y == 2

        # Duplicate unique value must fail
        with pytest.raises(AssertionError):
            type('AdditionalSubOk2', (UniqueOk,), {'x': 1, 'y': 2, '__module__': __name__})

        # Reserved unique attribute namespace must fail
        with pytest.raises(AssertionError):
            ABCRestrictions.require('y', unique=['y'])(MiddleLayerOk)

        # Metaclass ambiguity must fail
        with pytest.raises(Exception, match='[Mm]etaclass'):
            _cls = MyMeta('AdditionSubBad', (), namespace)
            ABCRestrictions.require('x')(_cls)

    @pytest.mark.parametrize('parent_class', sorted(ABCRestrictionMeta.abc_classes.keys(), key=lambda x: x.__name__))
    def test_not_instantiable(self, parent_class):
        with pytest.raises(NotImplementedError):
            parent_class()
