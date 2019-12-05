"""
Custom Abstract Base Classes to implement Restrictions. Developed for DataObject concept.
:date_created: 2018-12-05
"""

from builtins import object

from .constants import ConstABCR
from .messages import SystemMessages
from .utils import already_declared, classproperty, compare_cls


class ABCRestrictionMeta(type):
    """
    """
    _abc_classes = set()
    _unique_attrs = dict()

    @classproperty
    def abc_classes(cls):
        """
        To support parametrizing unit tests.
        :return:
        """
        return {k: getattr(k, ConstABCR.required, ()) for k in cls._abc_classes}

    def __new__(mcs, cls_name, parents, namespace):
        """

        :param cls_name:
        :param parents:
        :param namespace:
        :return:
        """
        assert '__module__' in namespace, SystemMessages.REQUIRED_FOR % ('__module__', 'ABCRestrictionsMeta')

        def nested_new(fn_new):
            def this_new(this_cls, *args, **kwargs):
                # Default abstract class check
                if getattr(this_cls, ConstABCR.state, None) != ConstABCR.leaf:
                    compare_cls((this_cls.__module__, this_cls.__name__), (namespace['__module__'], cls_name))

                if fn_new:
                    # Run explicitly defined __new__
                    assert callable(fn_new) or hasattr(fn_new, '__func__'), \
                        'Failed to decipher how to run nested __new__ for %s' % this_cls
                    if callable(fn_new):
                        return fn_new(this_cls, *args, **kwargs)
                    elif hasattr(fn_new, '__func__'):
                        return fn_new.__func__(this_cls, *args, **kwargs)
                else:
                    # Run default __new__
                    for p_ in parents:
                        if hasattr(p_, '__new__'):
                            p_.__new__(this_cls, *args, **kwargs)  # Unsure if trashing returned instance is a problem
                    return dict.__new__(this_cls, *args, **kwargs)

            return this_new

        namespace[ConstABCR.new] = nested_new(namespace.get(ConstABCR.new))

        if ConstABCR.required in namespace:
            # Root-type and Node-type classes define namespace requirements for its children.
            assert namespace.get(ConstABCR.state, ConstABCR.root) in ConstABCR.restrictions_allowed, \
                'Invalid class type=%s' % namespace.get(ConstABCR.state, ConstABCR.root)
            namespace[ConstABCR.state] = namespace.get(ConstABCR.state, ConstABCR.root)

            cls = type.__new__(mcs, cls_name, parents, namespace)
            mcs._abc_classes.add(cls)
        elif namespace.get(ConstABCR.is_abstract):
            # Node-style classes pass on requirements from roots to children of nodes. This class cannot be initialized.
            # Extra functionality can be added by explicitly declaring __new__
            namespace[ConstABCR.state] = ConstABCR.node
            cls = type.__new__(mcs, cls_name, parents, namespace)
        else:
            # Leaf-type classes implement requirements defined from Root and Node-type classes
            namespace[ConstABCR.state] = ConstABCR.leaf

            roots = []
            nodes = []
            leaves = []
            all_parents = {k for k in list(parents) + sum([p.mro() for p in parents], [])}
            for c in all_parents:
                if getattr(c, ConstABCR.state, None) == ConstABCR.root:
                    roots.append(c)
                elif getattr(c, ConstABCR.state, None) == ConstABCR.node:
                    nodes.append(c)
                elif getattr(c, ConstABCR.state, None) == ConstABCR.leaf:
                    leaves.append(c)

            # Validate that all required attributes from this class's roots are fulfilled in one of the following:
            #   1. This leaf's namespace
            #   2. One of its leaf-style parents' namespaces
            #   3. One of its node-style parents' namespaces
            required_attrs = set(sum([getattr(p, ConstABCR.required, ()) for p in roots + nodes], ()))
            for attr in required_attrs:
                # Check that the required attribute is defined in this class or a leaf that is a parent of this class.
                assert any([hasattr(p, attr) for p in leaves + nodes]) or attr in namespace, \
                    SystemMessages.REQUIRED_FOR % (attr, cls_name)

            # Validate that the value given to a unique attribute is unique system-wide for that attribute.
            unique_attrs = set(sum([getattr(p, ConstABCR.unique, ()) for p in roots + nodes], ()))
            for attr in unique_attrs:
                for leaf in mcs._unique_attrs.get(attr, []):
                    if attr not in namespace:
                        # This means the unique attr should be fulfilled in a leaf or node parent. Uniqueness check was
                        # already done at that level, so we can skip.
                        continue

                    if (namespace['__module__'], cls_name) == (leaf.__module__, leaf.__name__):
                        # Re-declaring the class... This supports iPython.
                        mcs._unique_attrs[attr].remove(leaf)
                        continue

                    assert namespace[attr] != getattr(leaf, attr), \
                        'Unique value "%s" has already been declared in class %s' % (namespace[attr], leaf.__name__)

            cls = type.__new__(mcs, cls_name, parents, namespace)

            # Register this class against the unique_attrs it fulfills for other leaves to be able to value check.
            for attr in unique_attrs:
                if attr not in mcs._unique_attrs:
                    mcs._unique_attrs[attr] = []
                assert hasattr(cls, attr), SystemMessages.REQUIRED_FOR % (attr, cls_name)
                mcs._unique_attrs[attr].append(cls)

            # Run optional compile-time validation function
            if hasattr(cls, '__compile__'):
                cls.__compile__()

        return cls


class ABCRestrictions(object):
    """
    ABCRestrictionMeta implementation via decorators.
    """

    @classmethod
    def require(cls, *required_attrs, **kwargs):
        """
        Decorator to attach requirements on the attribute namespace and declare the class as an abstract class.
        :param required_attrs:
        :param unique: subset of required_attrs that are required to have unique values system-wide
        :return: decorated class
        :raises: NotImplementedError if __new__ or __metaclass__ already defined.
        :raises: AssertionError if class reference already registered. (namespace clash)
        :raises: AssertionError if class is already declared as a Leaf-type class.
        :raises: AssertionError if a required attribute is already declared in a parent.
        """

        def worker(cls_ref):
            """

            :param cls_ref:
            :return:
            """
            assert cls_ref not in ABCRestrictionMeta.abc_classes, SystemMessages.CLASS_ALREADY_DEFINED
            assert getattr(cls_ref, ConstABCR.state, ConstABCR.root) in ConstABCR.restrictions_allowed, \
                SystemMessages.RESTRICTIONS_ALLOWED

            # Manipulate the namespace of the declared class so that metaclass handles it properly
            namespace = dict(cls_ref.__dict__)
            namespace.pop('__dict__', None)
            namespace.pop('__weakref__', None)

            # Check if required attributes passed in are new
            r = already_declared(cls_ref, ConstABCR.required, required_attrs)
            assert not r, SystemMessages.ATTRIBUTE_ALREADY_DECLARED % ('Required', r,
                                                                       "%s's parents" % cls_ref.__name__)
            namespace[ConstABCR.required] = required_attrs + getattr(cls_ref, ConstABCR.required, ())

            # Check if uniqueness requirements are declared for some attributes
            if kwargs.get('unique'):
                # Validate unique passed in properly
                unique = kwargs['unique']
                assert type(unique) in [list, tuple], 'Invalid type "%s" for parameter "unique"' % unique
                assert all([e in required_attrs for e in unique]), 'Unique attributes must be in required attributes!'

                # Validate unique attributes are new across all abc_classes
                for abc_cls in ABCRestrictionMeta.abc_classes:
                    u = already_declared(abc_cls, ConstABCR.unique, unique)
                    assert not u, SystemMessages.ATTRIBUTE_ALREADY_DECLARED % ('Unique', u, abc_cls.__name__)
                namespace[ConstABCR.unique] = tuple(unique) + getattr(cls_ref, ConstABCR.unique, ())
            return ABCRestrictionMeta(cls_ref.__name__, cls_ref.__bases__, namespace)

        return worker
