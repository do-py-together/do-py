"""
Commonly used restrictions.
:date_created: 2020-06-28
"""

from datetime import date, datetime

from future.moves import builtins

from do_py.abc import classproperty
from do_py.data_object import Restriction


class R(object):
    """
    The definition of a restriction for DataObjects:
    1. Allowed types or values.
       This is required for all restrictions and sets a strong standard for value and type checking.
       Value checks are not limited to a particular data type.
    2. Optionally, a default value for a restriction may be defined. This allows us to initiate DataObjects without
       providing data for this key/restriction.
       The primary use case for default values is to fill in gaps in data, i.e. front-end requests, 3rd party APIs, etc.

    Syntax:
        R(<restriction 1>, <restriction 2>, ..., default=<default value>)
        *args for R define either the types or values allowed (types and values may NOT be mixed).
        The keyword `default` defines the optional default value for the restriction.

    Usages:
        R(int, float)  # Allows integers and floats data. No default provided.
        R('hello', 'world')  # Allows the strings 'hello' and 'world' to be used as data values. No default provided.
        R(int, float, default=1)  # Again, allows integers and floats, but 1 is default value when no data is provided.

    Example:
        class A(DataObject):
            _restrictions = {
                'x': R(int),
                'y': R(int, default=12)
                }

        a = A(strict=False)
        a  # {'x': null, 'y': 12}
    """

    def __new__(cls, *args, **kwargs):
        """
        :rtype: Restriction
        """
        return Restriction(list(args), **kwargs)

    def __init__(self, *args, **kwargs):
        """
        :param args: Values or types for restriction definition
        :param kwargs: optional arguments for restriction instantiation
        :keyword default: default restriction value
        """

    def __call__(self, *args, **kwargs):
        """
        Dummy to support classproperty
        """

    @classproperty
    def INT(cls):
        """
        Shortcut for an int restriction.
        :rtype: Restriction
        """
        return cls(int, builtins.int)

    @classproperty
    def FLOAT(cls):
        """
        Shortcut for a float restriction.
        :rtype: Restriction
        """
        return cls(float, builtins.float)

    @classproperty
    def STR(cls):
        """
        Shortcut for string restriction.
        :rtype: Restriction
        """
        return cls(str, unicode, builtins.str)

    @classproperty
    def NULL_INT(cls):
        """
        Shortcut for a nullable int restriction.
        :rtype: Restriction
        """
        return cls(int, builtins.int, type(None))

    @classproperty
    def NULL_FLOAT(cls):
        """
        Shortcut for a nullable float restriction.
        :rtype: Restriction
        """
        return cls(float, builtins.float, type(None))

    @classproperty
    def NULL_STR(cls):
        """
        Shortcut for a nullable strinng restriction.
        :rtype: Restriction
        """
        return cls(str, unicode, builtins.str, type(None))

    @classproperty
    def LIST(cls):
        """
        Shortcut for a list restriction.
        :rtype: Restriction
        """
        return cls(list)

    @classproperty
    def SET(cls):
        """
        Shortcut for a set restriction.
        :rtype: Restriction
        """
        return cls(set)

    @classproperty
    def NULL_LIST(cls):
        """
        Shortcut for a nullable list restriction.
        :rtype: Restriction
        """
        return cls(list, type(None))

    @classproperty
    def BOOL(cls):
        """
        Shortcut for a bool restriction.
        :rtype: Restriction
        """
        return cls(bool)

    @classproperty
    def DATETIME(cls):
        """
        Shortcut for a datetime.datetime restriction.
        :rtype: Restriction
        """
        return cls(datetime)

    @classproperty
    def DATE(cls):
        """
        Shortcut for a datetime.date restriction.
        :rtype: Restriction
        """
        return cls(date)

    @classproperty
    def NULL_DATETIME(cls):
        """
        Shortcut for a nullable datetime.datetime restriction.
        :rtype: Restriction
        """
        return cls(datetime, type(None))

    @classproperty
    def NULL_DATE(cls):
        """
        Shortcut for a nullable datetime.date restriction.
        :rtype: Restriction
        """
        return cls(date, type(None))

    @classproperty
    def BOOL_INT(cls):
        """
        Unlike the rest of the helpers, this is not a type restriction
            but a value restriction that represents bool as an integer of values 0 and 1.
        :rtype: Restriction
        """
        return cls(0, 1)

    @classproperty
    def LONG_INT(cls):
        """
        Shortcut for a long int restriction.
        :rtype: Restriction
        """
        return cls(int, long, builtins.int)

    @classproperty
    def NULL_LONG_INT(cls):
        """
        Shortcut for a nullable long int restriction.
        :rtype: Restriction
        """
        return cls(int, long, builtins.int, type(None))
