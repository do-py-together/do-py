"""
Dynamic restrictions for a DataObject.
"""
from do_py import DataObject, R
from do_py.abc import ABCRestrictionMeta
from do_py.utils.properties import cached_property


class DynamicClassGenerator(DataObject):
    """
    Generate a class that is inheritable by a DO that requires dynamic restrictions.
    :restriction independent_key: The key that the dynamic restriction depends on.
    :restriction dependent_key: The key where the restriction is dynamic.
    """
    _restrictions = {
        'independent_key': R.STR,
        'dependent_key': R.STR,
        'dynamic_restrictions': R()
        }

    @property
    def update_fn_name(self):
        """
        :rtype: str
        """
        return '_update_%s_restriction' % self.dependent_key

    @cached_property
    def dynamic_class(self):
        """
        Create a class dynamically which inherits from DataObject, but also contains the required attributes to
        create dynamic restrictions for the dependent key.
        :rtype: type(DataObject)
        """

        def update_restriction(instance_self):
            """
            Update the dynamic restriction. This function will live inside the instance of the
            class under the name declared in `update_fn_name`.
            """
            restriction = self.dynamic_restrictions[instance_self[self.independent_key]]
            # Update the restriction.
            instance_self._restrictions[self.dependent_key] = restriction
            # Validate the data with the new restriction.
            instance_self._restrictions[self.dependent_key](instance_self[self.dependent_key])

        attributes = {
            '_is_abstract_': True,
            '__module__': self.__class__.__module__,
            self.update_fn_name: update_restriction,
            }

        # Create the class using ABCRestrictionMeta as the metaclass and inheriting from DataObject.
        instance = ABCRestrictionMeta('dynamic_%s_mixin' % self.dependent_key, (DataObject,), attributes)

        # Methods that require the use of super must be attached after instantiation.
        instance.__init__ = self.init_method
        instance.__setitem__ = self.setitem_method
        instance.__compile__ = self.compile_classmethod
        return self.dynamic_class

    @cached_property
    def init_method(self):
        """
        The init method needs to call the update restriction method after init is done.
        :rtype: types.Callable
        """

        def __init__(instance_self, data, **init_kwargs):
            super(self.dynamic_class, instance_self).__init__(data, **init_kwargs)
            getattr(instance_self, self.update_fn_name)()

        return __init__

    @cached_property
    def setitem_method(self):
        """
        Generate the set item method which overrides the parent's. When either the dependent or independent keys
        are updated, we must run the update restriction method.
        :rtype: types.Callable
        """

        def __setitem__(instance_self, item_key, item_value):
            response = super(self.dynamic_class, instance_self).__setitem__(item_key, item_value)
            if item_key in [self.independent_key, self.dependent_key]:
                getattr(instance_self, self.update_fn_name)()
            return response

        return __setitem__

    @cached_property
    def compile_classmethod(self):
        """
        Generate the classmethod that will be used for compilation.
        1) We need to validate that the independent and dependent keys must exist in the restrictions.
        :rtype: classmethod
        """

        def __compile__(cls):
            super(self.dynamic_class, cls).__compile__()
            assert self.independent_key in cls._restrictions, \
                '%s.%s required in restrictions for dynamic restrictions.' % (cls.__name__, self.independent_key)
            assert self.dependent_key in cls._restrictions, \
                '%s.%s required in restrictions for dynamic restrictions.' % (cls.__name__, self.dependent_key)

        return classmethod(__compile__)


def dynamic_restriction_mixin(independent_key, dependent_key, **kwargs):
    """
    Create a mixin class that a DO class can inherit from in order to
    :param independent_key: The key that the dynamic restriction depends on.
    :type independent_key: str
    :param dependent_key: The key where the restriction is dynamic.
    :type dependent_key: str
    :param kwargs: The dynamic
    :rtype: type(DataObject)
    """
    return DynamicClassGenerator({
        'independent_key': independent_key,
        'dependent_key': dependent_key,
        'dynamic_restrictions': kwargs,
        }).dynamic_class
