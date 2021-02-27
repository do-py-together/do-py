"""
WIP

Examples for
1) Basic inheritance.
2) Compile-time validations using __compile__.
"""
from do_py import DataObject


class ParentClass(DataObject):
    """

    """
    _is_abstract_ = True


class ChildClass(ParentClass):
    """

    """
