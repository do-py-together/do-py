"""
Utils to support base_model modules.
:date_created: 2018-12-05
:author: Tim Davis
"""

from do_py.abc.messages import SystemMessages


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
