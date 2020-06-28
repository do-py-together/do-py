"""
Commonly used restrictions.
:date_created: 2020-06-28
"""

from datetime import date, datetime

from do_py.exceptions import RestrictionError

from do_py.data_object.restriction import ManagedRestrictions

from do_py.abc import classproperty

from do_py.data_object import Restriction
from future.moves import builtins


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


class MgdDatetime(ManagedRestrictions):
    """
    Managed from and to date/datetime restrictions. It follows the following logic:

                                        From                        To
    None                                Epoch date(time)            Epoch date(time)
    Valid Datetime/Date instance        Do nothing                  Do nothing
    Everything else                     Parse as ISO date(time)     Parse as ISO date(time)

    Note:
        The default value will not be set properly in `strict=False` initializations that are missing the relevant key.
        This is due to strictness impacting ManagedRestrictions execution; the `manage` method does not execute on
        `strict=False`. Since this implementation sets the default in this method, the abstraction fails to
    Example:
        class A(DataObject):
            _restrictions = {
                'from_date': MgdDatetime.from_from_date()
                }

        A(strict=False)  # {"from_date": null}
        A(data={'from_date': None}, strict=False)  # {"from_date": "1969-12-31"}
        A({'from_date': None})  # {"from_date": "1969-12-31"}
    """
    dt_obj = None
    _restriction = R()
    _parse_dt_fmt = {
        datetime: '%Y-%m-%dT%H:%M:%S',
        date: '%Y-%m-%d'
        }
    defaults = {
        'from': lambda dt: dt.fromtimestamp(0),
        'to': lambda dt: dt.now() if dt is datetime else dt.today()
        }

    def __init__(self, dt_obj=None, default_key=None, nullable=False, *args, **kwargs):
        """
        :param dt_obj: Initialize the restriction as date or datetime.
        :type dt_obj: Type[Union[datetime, date]]
        :param default_key: Manages "from" or "to"
        :type default_key: str
        """
        assert dt_obj in self._parse_dt_fmt, 'Invalid "dt_obj"(=%s)' % dt_obj
        assert default_key is None or default_key in self.defaults, 'Invalid "default_key"(=%s)' % default_key
        self.dt_obj = dt_obj
        self.default_key = default_key
        self.nullable = nullable
        self._restriction = R.DATETIME if self.dt_obj is datetime else R.DATE
        super(MgdDatetime, self).__init__(*args, **kwargs)

    def manage(self):
        """
        Implements the logic outlined in class docstring.
        Uses datetime.strptime by design to be more strict on the string parsing for ISO format.
        """
        if self.data is None:
            if self.default_key:
                self.data = self.defaults[self.default_key](self.dt_obj)
            elif not self.nullable:
                raise RestrictionError.bad_data(self.data, self._restriction.allowed)
        elif type(self.data) not in [datetime, date]:
            self.data = datetime.strptime(self.data, self._parse_dt_fmt[self.dt_obj])
            if self.dt_obj is date:
                self.data = self.data.date()

        if self.dt_obj is datetime:
            self.data = self.data.replace(microsecond=0)

    @classmethod
    def from_from_date(cls):
        """
        Create a MgdDatetime instance for validating a `from_date` restriction.
        This will validate a DATE format, not DATETIME.
        :rtype: MgdDatetime
        """
        return cls(dt_obj=date, default_key='from')

    @classmethod
    def from_to_date(cls):
        """
        Create a MgdDatetime instance for validating a `to_date` restriction.
        This will validate a DATE format, not DATETIME.
        :rtype: MgdDatetime
        """
        return cls(dt_obj=date, default_key='to')

    @classmethod
    def from_from_datetime(cls):
        """
        Create a MgdDatetime instance for validating a `from_datetime` restriction.
        This will validate a DATETIME format, not DATE.
        :rtype: MgdDatetime
        """
        return cls(dt_obj=datetime, default_key='from')

    @classmethod
    def from_to_datetime(cls):
        """
        Create a MgdDatetime instance for validating a `to_datetime`
        This will validate a DATETIME format, not DATE.
        :rtype: MgdDatetime
        """
        return cls(dt_obj=datetime, default_key='to')

    @classmethod
    def datetime(cls):
        """
        Create MgdDatetime instance for validating and standardizing a DATETIME format.
        :rtype: MgdDatetime
        """
        return cls(dt_obj=datetime)

    @classmethod
    def date(cls):
        """
        Create MgdDatetime instance for validating and standardizing a DATE format.
        :rtype: MgdDate
        """
        return cls(dt_obj=date)

    @classmethod
    def null_date(cls):
        """
        Create MgdDatetime instance for validating and standardizing a DATE format that is nullable.
        :rtype: MgdDate
        """
        return cls(dt_obj=date, nullable=True)


class ManagedFloat(ManagedRestrictions):
    """
    Force float.
    """
    _restriction = R.FLOAT

    def __init__(self, nullable=False):
        self.nullable = nullable
        super(ManagedFloat, self).__init__()

    def manage(self):
        """
        Cast all numbers to float.
        """
        assert self.data is not None or self.nullable, 'Invalid type NoneType for ManagedFloat.'
        if self.data is not None:
            self.data = float(self.data)
