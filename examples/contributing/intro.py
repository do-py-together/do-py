"""
Introduction.
At its most basic level, a DataObject is built of something called a restricted dict mixin. A `RestrictedDictMixin` is
simply a class that inherits from python dict type. This just allows for certain parts of the built-in python dictionary
to be excluded to help prevent unwanted things from occurring. In this class it just takes several of the built-in
functions and turns them off.
"""
from do_py.abc import ABCRestrictions
from do_py.data_object import RestrictedDictMixin


@ABCRestrictions.require('_restrictions')
class DataObject(RestrictedDictMixin):
    """
    You will notice that in this DataObject there is an ABCRestrictions
    decorator, this simply states that the **_restrictions** attribute
    **must be present** in the DataObject. This is just a way of using a decorator
    to require certain items be present in the class. This helps to promote strictness
    so that a class cannot even be created without the proper attributes.
    """
