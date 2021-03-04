"""
Using restrictions.

Restrictions are written using `do_py.R`. `R` allows developers to define custom value restrictions as well as type
restrictions using the special shortcuts. Here are a few examples of how you can write value restrictions and type
restrictions using the type short-cuts.
"""
from do_py import DataObject, R


class TypeShorCuts(DataObject):
    """
    All of the restrictions written for this DataObject us R's type shortcuts.
    """
    _restrictions = {
        # integer
        'int': R.INT,
        'nullable_int': R.NULL_INT,
        # string
        'str': R.STR,
        'nullable_str': R.NULL_STR,
        # bool
        'bool': R.BOOL,
        # date and datetime
        'date': R.DATE,
        'nullable_date': R.NULL_DATE,
        'datetime': R.DATETIME,
        'nullable_datetime': R.NULL_DATETIME,
        # other (these are rarely used(aqw
        'set': R.SET,
        'list': R.LIST,
        }


class ValueRestrictions(DataObject):
    """
    All of the restrictions for this class are value restrictions.
    :restriction integers: This allows for numbers 1, 2, and 3.
    :restriction integers_and_none: This allows for numbers 1, 2, and 3, but also `None`.
    :restriction strings: This allows for numbers 'hello', 'hi', and 'sup'.
    :restriction strings_and_none: This allows for numbers 'hello', 'hi', and 'sup', but also `None`.
    """
    _restrictions = {
        # number values
        'integers': R(1, 2, 3),
        'integers_and_none': R(1, 2, 3, None),
        # string values
        'strings': R('hello', 'hi', 'sup'),
        'strings_and_none': R('hello', 'hi', 'sup', None),
        }
