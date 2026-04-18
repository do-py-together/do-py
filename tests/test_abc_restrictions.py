"""
:date_created: 2019-08-20
"""

import pytest

from do_py.abc import ABCRestrictionMeta, ABCRestrictions
from do_py.abc.constants import ConstABCR
from do_py.abc.messages import SystemMessages
from do_py.abc.utils import already_declared, compare_cls


@pytest.mark.usefixtures('abc_cleanup')
class TestABCRestrictions:
    """Core tests for the ABCRestrictions.require decorator and ABCRestrictionMeta."""

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


@pytest.mark.usefixtures('abc_cleanup')
class TestABCRestrictionMetaBranches:
    """Test all three branches of ABCRestrictionMeta.__new__: root, node, leaf."""

    def test_root_class_creation(self):
        """Root-type classes define namespace requirements for their children."""
        Root = ABCRestrictions.require('attr_a', 'attr_b')(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        assert Root is not None
        assert getattr(Root, ConstABCR.state) == ConstABCR.root
        assert Root in ABCRestrictionMeta._abc_classes
        assert getattr(Root, ConstABCR.required) == ('attr_a', 'attr_b')

    def test_node_class_creation(self):
        """Node-type classes pass on requirements but cannot be instantiated."""
        Root = ABCRestrictions.require('x')(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        Node = type('Node', (Root,), {ConstABCR.is_abstract: True, '__module__': __name__})
        assert getattr(Node, ConstABCR.state) == ConstABCR.node
        assert Node not in ABCRestrictionMeta._abc_classes

        with pytest.raises(NotImplementedError):
            Node()

    def test_leaf_class_creation(self):
        """Leaf-type classes implement requirements from root and node parents."""
        Root = ABCRestrictions.require('x')(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        Leaf = type('Leaf', (Root,), {'x': 42, '__module__': __name__})
        assert getattr(Leaf, ConstABCR.state) == ConstABCR.leaf
        assert Leaf.x == 42

    def test_leaf_missing_required_attr_from_root(self):
        """Leaf that does not fulfil root requirements must fail."""
        Root = ABCRestrictions.require('x', 'y')(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        with pytest.raises(AssertionError):
            type('BadLeaf', (Root,), {'x': 1, '__module__': __name__})

    def test_leaf_inherits_from_node_and_root(self):
        """Leaf that inherits from both root and node must satisfy all requirements."""
        Root = ABCRestrictions.require('x')(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        Node = type('Node', (Root,), {ConstABCR.is_abstract: True, '__module__': __name__})
        NodeWithReqs = ABCRestrictions.require('y')(Node)
        Leaf = type('Leaf', (NodeWithReqs,), {'x': 1, 'y': 2, '__module__': __name__})
        assert Leaf.x == 1
        assert Leaf.y == 2

    def test_leaf_inherits_attr_from_parent_leaf(self):
        """A leaf can inherit required attrs from another leaf parent."""
        Root = ABCRestrictions.require('x')(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        ParentLeaf = type('ParentLeaf', (Root,), {'x': 10, '__module__': __name__})
        ChildLeaf = type('ChildLeaf', (ParentLeaf,), {'__module__': __name__})
        assert ChildLeaf.x == 10

    def test_leaf_inherits_attr_from_node(self):
        """A leaf can inherit required attrs from a node parent that has them."""
        Root = ABCRestrictions.require('x')(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        Node = type('Node', (Root,), {ConstABCR.is_abstract: True, 'x': 99, '__module__': __name__})
        Leaf = type('Leaf', (Node,), {'__module__': __name__})
        assert Leaf.x == 99


@pytest.mark.usefixtures('abc_cleanup')
class TestUniqueAttributes:
    """Test the system-wide uniqueness enforcement for unique attrs."""

    def test_unique_values_enforced(self):
        """Two leaves cannot share the same value for a unique attribute."""
        Root = ABCRestrictions.require('uid', unique=['uid'])(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        type('LeafA', (Root,), {'uid': 'alpha', '__module__': __name__})
        with pytest.raises(AssertionError, match='alpha'):
            type('LeafB', (Root,), {'uid': 'alpha', '__module__': __name__})

    def test_unique_different_values_ok(self):
        """Two leaves with different unique values should succeed."""
        Root = ABCRestrictions.require('uid', unique=['uid'])(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        LeafA = type('LeafA', (Root,), {'uid': 'one', '__module__': __name__})
        LeafB = type('LeafB', (Root,), {'uid': 'two', '__module__': __name__})
        assert LeafA.uid == 'one'
        assert LeafB.uid == 'two'

    def test_unique_attr_inherited_from_parent_skips_check(self):
        """If the unique attr is not in the leaf's own namespace (inherited), skip uniqueness check."""
        Root = ABCRestrictions.require('uid', unique=['uid'])(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        ParentLeaf = type('ParentLeaf', (Root,), {'uid': 'shared', '__module__': __name__})
        # ChildLeaf inherits 'uid' from ParentLeaf — should not conflict
        ChildLeaf = type('ChildLeaf', (ParentLeaf,), {'__module__': __name__})
        assert ChildLeaf.uid == 'shared'

    def test_redeclaration_same_module_and_name(self):
        """Re-declaring a class with the same module+name (iPython support) should succeed."""
        Root = ABCRestrictions.require('uid', unique=['uid'])(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        type('SameName', (Root,), {'uid': 'val', '__module__': 'test_redecl'})
        # Re-declare with same module+name — should not conflict
        Redeclared = type('SameName', (Root,), {'uid': 'val', '__module__': 'test_redecl'})
        assert Redeclared.uid == 'val'


@pytest.mark.usefixtures('abc_cleanup')
class TestCompileHook:
    """Test that __compile__ is invoked on leaf classes."""

    def test_compile_called_on_leaf(self):
        """If a leaf class defines __compile__, it should be called at class creation."""
        compile_called = []

        Root = ABCRestrictions.require('x')(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )

        def track_compile(cls):
            compile_called.append(cls.__name__)

        Leaf = type('Leaf', (Root,), {'x': 1, '__compile__': classmethod(track_compile), '__module__': __name__})
        assert 'Leaf' in compile_called, '__compile__ was not called on leaf creation'
        assert Leaf.x == 1


@pytest.mark.usefixtures('abc_cleanup')
class TestNestedNew:
    """Test that the nested __new__ wrapper handles all branches."""

    def test_default_new(self):
        """Leaf with no explicit __new__ should use the default path."""
        Root = ABCRestrictions.require('x')(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        Leaf = type('Leaf', (Root,), {'x': 1, '__module__': __name__})
        assert Leaf.x == 1

    def test_callable_new(self):
        """Leaf inheriting from a root with a callable __new__ should invoke it."""
        new_calls = []

        def custom_new(cls, *args, **kwargs):
            new_calls.append(cls.__name__)
            return dict.__new__(cls, *args, **kwargs)

        Root = ABCRestrictions.require('x')(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__new__': custom_new, '__module__': __name__})
        )
        Leaf = type('Leaf', (Root,), {'x': 1, '__module__': __name__})
        assert Leaf.x == 1

    def test_classmethod_new(self):
        """Leaf inheriting from a root with a classmethod __new__ should invoke __func__."""

        def custom_new(cls, *args, **kwargs):
            return dict.__new__(cls, *args, **kwargs)

        Root = ABCRestrictions.require('x')(
            type(
                'Root',
                tuple(),
                {
                    ConstABCR.is_abstract: True,
                    '__new__': classmethod(custom_new),
                    '__module__': __name__,
                },
            )
        )
        Leaf = type('Leaf', (Root,), {'x': 1, '__module__': __name__})
        assert Leaf.x == 1


@pytest.mark.usefixtures('abc_cleanup')
class TestRequireEdgeCases:
    """Edge cases for ABCRestrictions.require."""

    def test_require_unique_must_be_subset(self):
        """unique attrs must be a subset of required attrs."""
        with pytest.raises(AssertionError):
            ABCRestrictions.require('x', unique=['y'])(
                type('Bad', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
            )

    def test_require_unique_invalid_type(self):
        """unique kwarg must be a list or tuple."""
        with pytest.raises(AssertionError):
            ABCRestrictions.require('x', unique='x')(
                type('Bad', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
            )

    def test_require_already_registered_class(self):
        """Cannot apply require to a class that is already an ABC root."""
        Root = ABCRestrictions.require('x')(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        with pytest.raises(AssertionError, match='already defined'):
            ABCRestrictions.require('y')(Root)

    def test_require_on_leaf_fails(self):
        """Cannot apply require to a leaf-state class."""
        Root = ABCRestrictions.require('x')(
            type('Root', tuple(), {ConstABCR.is_abstract: True, '__module__': __name__})
        )
        Leaf = type('Leaf', (Root,), {'x': 1, '__module__': __name__})
        with pytest.raises(AssertionError):
            ABCRestrictions.require('y')(Leaf)


class TestABCUtils:
    """Test utility functions in do_py.abc.utils."""

    def test_compare_cls_same_raises(self):
        cls_id = ('mymodule', 'MyClass')
        with pytest.raises(NotImplementedError, match=SystemMessages.INSTANTIATION_ERROR):
            compare_cls(cls_id, cls_id)

    def test_compare_cls_different_ok(self):
        # Should not raise
        compare_cls(('mod_a', 'A'), ('mod_b', 'B'))

    def test_already_declared_found(self):
        class FakeClass:
            _required_ = ('x', 'y')

        result = already_declared(FakeClass, '_required_', ('y',))
        assert result == 'y'

    def test_already_declared_not_found(self):
        class FakeClass:
            _required_ = ('x', 'y')

        result = already_declared(FakeClass, '_required_', ('z',))
        assert result is None

    def test_already_declared_no_attr(self):
        class FakeClass:
            pass

        result = already_declared(FakeClass, '_required_', ('x',))
        assert result is None
