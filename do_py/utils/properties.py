"""
Property decorators useful for organizing code in a DO.
:date_created: 2020-07-10
"""

import inspect

from builtins import object


class classproperty(object):
    """
    This is a decorator.
    https://stackoverflow.com/questions/3203286/how-to-create-a-read-only-class-property-in-python
    """

    def __init__(self, f):
        """
        f is a method in a class that should be a property. This function will be able to access the attribute from
        class-level. Instances are not required, but the attribute value in the instance is preferred over compile-time.
        :param f:
        :rtype: classmethod
        """
        self.f = f

    def __get__(self, instance, owner):
        return self.f(owner)


class cached_classproperty(object):
    """
    This builds on the same idea as `classproperty`.
    This is a decorator.
    https://stackoverflow.com/questions/3203286/how-to-create-a-read-only-class-property-in-python
    """

    def __init__(self, f):
        """
        f is a method in a class that should be a property. This function will be able to access the attribute from
        class-level. Instances are not required, but the attribute value in the instance is preferred over compile-time.
        :param f:
        :rtype: classmethod
        """
        self.f = f
        self.attr = '_%s' % f.__name__

    def __get__(self, instance, owner):
        if not hasattr(self, self.attr):
            setattr(self, self.attr, self.f(owner))
        return getattr(self, self.attr)


def cached_property(original_property):
    """
    Adds object caching capability to getter property. Value returned by property 'fn' is cached in '_fn' attr. This is
    useful when property is computationally expensive to calculate. By caching the computed value, repeated calls to the
    property become more efficient.

    Example:

    class A(object):
        @cached_property
        def ok(self):
            return 'ok'

    Assume that a call to 'ok' is expensive. The return value of ok will be object level cached the first time it is
    called. Subsequent calls will avoid computation. The trade-off is additional memory consumption due to storage of
    the cached value.

    :param original_property: method intended to be used as property.
    :type original_property: method
    :return: property is object level return value caching.
    :rtype: property
    """
    attr = '_%s' % original_property.__name__

    def worker(self):
        """
        Proxy property that performs object level caching.
        """
        if not hasattr(self, attr):
            setattr(self, attr, original_property(self))
        return getattr(self, attr)

    setattr(worker, '_cached_', True)
    worker.__name__ = original_property.__name__
    worker.__doc__ = original_property.__doc__
    return property(fget=worker)


def is_cached_property(_cached_property):
    """
    Check if a class's property is wrapped by `cached_property`.
    :param _cached_property: The property in question.
    :rtype: bool
    :see: cached_property
    """
    # Get the `fget` method from the property.
    fget = getattr(_cached_property, 'fget', None)
    if fget:
        return getattr(fget, '_cached_', False)
    else:
        return False


def is_classmethod(cls, method):
    """
    Check if a method is a classmethod. Supports Python 2/3.
    :ref: https://stackoverflow.com/questions/19227724/check-if-a-function-uses-classmethod
    :param cls: Class
    :type cls: type
    :param method: Name of the method to check
    :type method: callable
    :rtype: bool
    """
    return inspect.ismethod(method) and hasattr(method, '__self__') and getattr(method, '__self__') is cls


def is_property(attribute):
    """
    Check if a class attribute is of type property.
    :ref: https://stackoverflow.com/questions/17735520/determine-if-given-class-attribute-is-a-property-or-not-python-object
    :param attribute: The class's attribute that will be checked.
    :rtype: bool
    """
    return isinstance(attribute, property)
