"""
Dynamic restrictions for a DataObject.
:date_created: 2020-07-10
:author: Gian Brazzini
"""
import copy

from do_py import DataObject, R
from do_py.abc import ABCRestrictionMeta
from do_py.data_object.restriction import ManagedRestrictions, _ListValueRestriction
from do_py.utils.properties import cached_property


class DynamicRestrictions(ManagedRestrictions):
    """
    A dict that contains the dynamic restrictions where the key is the independent
    key's value and the value is the dependent key's restriction.
    """
    _restriction = R()

    def manage(self):
        """
        Validate that the list is not empty and that the format is correct.
        """
        assert self.data, 'Missing dynamic restrictions, dict cannot be empty.'
        for value in self.data.values():
            assert DataObject in value.mro(), 'Dynamic restrictions depend each value being a DataObject.'


class DynamicClassGenerator(DataObject):
    """
    Generate a class that is inheritable by a DO that requires dynamic restrictions.
    :restriction independent_key: The key that the dynamic restriction depends on.
    :restriction dependent_key: The key where the restriction is dynamic.
    :restriction dynamic_restrictions: See `DynamicRestrictions` ManagedList.
    """
    _restrictions = {
        'independent_key': R.STR,
        'dependent_key': R.STR,
        'dynamic_restrictions': DynamicRestrictions()
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
            # Set the dynamic in the instance so that we can verify the data.
            super(self.dynamic_class, instance_self).__setitem__(self.dependent_key, instance_self[self.dependent_key])

        attributes = {
            '_is_abstract_': True,
            '__module__': self.__class__.__module__,
            self.update_fn_name: update_restriction,
            }

        # Create the class using ABCRestrictionMeta as the metaclass and inheriting from DataObject.
        return ABCRestrictionMeta('dynamic_%s_mixin' % self.dependent_key, (DataObject,), attributes)

    @cached_property
    def init_method(self):
        """
        The init method needs to call the update restriction method after init is done.
        :rtype: types.Callable
        """

        def __init__(instance_self, data, **init_kwargs):
            # Each instance is required to have a copy of the restrictions, otherwise the restrictions are shared by
            # reference.
            instance_self._restrictions = copy.deepcopy(instance_self._restrictions)
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
        The following validations are made:
        1) The independent and dependent keys must exist in the restrictions.
        2) The independent restriction is a list value restriction.
        3) All values for the independent restrictions are accounted for in the dynamic restrictions.
        :rtype: classmethod
        """

        def __compile__(cls):
            super(self.dynamic_class, cls).__compile__()

            # Validate that the independent and dependent keys must exist in the restrictions.
            assert self.independent_key in cls._restrictions, \
                '%s.%s required in restrictions for dynamic restrictions.' % (cls.__name__, self.independent_key)
            assert self.dependent_key in cls._restrictions, \
                '%s.%s required in restrictions for dynamic restrictions.' % (cls.__name__, self.dependent_key)

            # Validate that the independent restriction is a list value restriction.
            independent_key_restriction = cls._restrictions[self.independent_key]
            assert isinstance(independent_key_restriction, _ListValueRestriction), \
                'The independent key must be of type `_ListValueRestriction`.'

            # Validate that all values for the independent restrictions are accounted for in the dynamic restrictions.
            assert len(independent_key_restriction[0]) == len(self.dynamic_restrictions), \
                'All restrictions must be accounted for when creating dynamic restrictions.'
            for value in independent_key_restriction[0]:
                assert value in self.dynamic_restrictions, 'Missing dynamic restriction for value "%s".' % value

        return classmethod(__compile__)

    @cached_property
    def mixin(self):
        """
        The finished product for the generated class mixin. It had to be done in two
            properties due to the method dependency noted below.
        :rtype: type(DataObject)
        """
        # Methods that require the use of super must be attached after instantiation.
        self.dynamic_class.__init__ = self.init_method
        self.dynamic_class.__setitem__ = self.setitem_method
        self.dynamic_class.__compile__ = self.compile_classmethod
        return self.dynamic_class


def dynamic_restriction_mixin(independent_key, dependent_key, **kwargs):
    """
    Create a mixin class that a DO class can inherit to enable dynamic restrictions.
    See `DynamicClassGenerator` for further instruction.
    :param independent_key: The key that the dynamic restriction depends on.
    :param dependent_key: The key where the restriction is dynamic.
    :param kwargs: The dynamic restrictions.
    :rtype: type(DataObject)
    """
    return DynamicClassGenerator({
        'independent_key': independent_key,
        'dependent_key': dependent_key,
        'dynamic_restrictions': kwargs,
        }).mixin
