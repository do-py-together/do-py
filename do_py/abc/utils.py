"""
Utils to support base_model modules.
:date_created: 2018-12-05
:author: Tim Davis
"""

from builtins import object

from do_py.abc.messages import SystemMessages


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
        """
        self.f = f

    def __get__(self, instance, owner):
        return self.f(instance if instance else owner)


def compare_cls(cls_name, other):
    """
    Util to adhere to DRY concept for comparing class names. This is used to make sure abstract classes are
    not instantiated.
    :param cls_name:
    :param other:
    :raises: NotImplementedError
    """
    if cls_name == other:
        raise NotImplementedError(SystemMessages.INSTANTIATION_ERROR)


def already_declared(_cls_ref, attr_name, attrs):
    if getattr(_cls_ref, attr_name, ()):
        for attr in attrs:
            if attr in getattr(_cls_ref, attr_name):
                return attr
