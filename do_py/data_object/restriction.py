"""
Data Object Restrictions.
:date_created: 2019-05-13
"""

import copy
from abc import ABCMeta, abstractmethod, abstractproperty

from six import with_metaclass

from ..abc import ABCRestrictionMeta
from ..exceptions import RestrictionError


class AbstractRestriction(tuple):
    """
    Manage restriction syntax. Pull allowed and default values for the tuple syntax.

    E.g.
    For ([int], None), allowed = [int] and default = None

    Syntax:
    Restrictions are typically declared as tuples. The first item in the restriction is allowed. The second item is
    the default value. See specific restriction for more details.

    allowed:
    Data restrictions are captured as allowed. See specific restriction for more details.

    default:
    Every restriction provides a default value. If not explicitly specified, it is implicitly set to None.
    """
    _default = None
    _allowed = None

    def __init__(self, *args, **kwargs):
        """
        default and allowed are provided as tuple.
        """
        if len(self) > 1:
            self._default = self[1]

        self._allowed = self[0]

    def __call__(self, data, **kwargs):
        """
        Execute data validation. See specific restriction for more details.
        """

    @property
    def allowed(self):
        return self._allowed

    @property
    def default(self):
        return self._default

    def __copy__(self):
        return tuple(self)

    def __deepcopy__(self, memodict={}):
        memodict[id(self)] = self.__copy__()
        _r = copy.deepcopy(self.__copy__())
        return self.__class__(_r[0], default=_r[1])


def is_immutable(obj):
    return any(isinstance(obj, x) for x in [bool, int, float, tuple, str, frozenset, type(None)])


class SingletonRestriction(AbstractRestriction):
    """
    This is an interface for Restriction type to use singleton structure. The objective is to use pre-defined
    restrictions and reduce the memory footprint of DataObject declarations.
    """
    _cache = {}

    def __new__(cls, restriction_tuple):
        try:
            rt1 = restriction_tuple[1] if is_immutable(restriction_tuple[1]) else frozenset(restriction_tuple[1])
            # cls.__name__ supports restriction inheritance, i.e. _NullableDataObjectRestriction
            hashable = (cls.__name__, frozenset(restriction_tuple[0]), rt1)
        except TypeError:
            # DataObjects are not iterable, so frozenset throws TypeError
            hashable = (cls.__name__, restriction_tuple[0])
        if hashable in cls._cache:
            return cls._cache[hashable]
        else:
            cls._cache[hashable] = super(SingletonRestriction, cls).__new__(cls, restriction_tuple)
            return cls._cache[hashable]


class _ListTypeRestriction(SingletonRestriction):
    """
    Manage restriction of syntax ([type], None)

    Syntax:
    This uses standard tuple syntax.

    allowed:
    allowed is declared as a list of types.

    default:
    None if not specified.

    Validation:
    The type of supplied data must be an item in the allowed list.

    E.g.:

    class A(DataObject):
        _restrictions = {
            'x': ([int, float], None)
            }

    Here, x can be numbers like 1, 1.0, -3, etc.
    Good for some data like pulsechecks sent (x >= 0).
    """

    def __new__(cls, allowed, default=None, **kwargs):
        return super(_ListTypeRestriction, cls).__new__(cls, (allowed, default))

    def __init__(self, *args, **kwargs):
        super(_ListTypeRestriction, self).__init__()
        if len([e for e in self._allowed if type(e) is ABCRestrictionMeta]) != 0:
            raise RestrictionError.from_dataobj_in_rstr_list(self._allowed)

        if not all([isinstance(r, type) for r in self._allowed]):
            raise RestrictionError.from_mixed_value_and_type(self._allowed)

    def __call__(self, data, **kwargs):
        if type(data) not in self._allowed:
            raise RestrictionError.bad_data(type(data), self._allowed)
        return data


class _ListValueRestriction(SingletonRestriction):
    """
    Manage restriction of syntax ([values], None)

    Syntax:
    This uses standard tuple syntax.

    allowed:
    allowed is declared as a list of values.

    default:
    None if not specified.

    Validation:
    Supplied data must be an item in the allowed list.

    E.g.:

    class A(DataObject):
        _restrictions = {
            'x': ([1, 2, 3], None)
            }

    Here, x can be numbers like 1, 2 and 3. However, numbers like 1.0, -3, etc are not allowed. Typically, this is
    more restrictive than _ListTypeRestriction.

    Good choice for some data such as Review ratings (1 <= ratings <= 5).
    """

    def __new__(cls, allowed, default=None, **kwargs):
        return super(_ListValueRestriction, cls).__new__(cls, (allowed, default))

    def __call__(self, data, **kwargs):
        if data not in self._allowed:
            raise RestrictionError.bad_data(data, self._allowed)
        return data


class _ListNoRestriction(SingletonRestriction):
    """
    Manage restriction of syntax ([], None)

    Syntax:
    Empty list for allowed.

    allowed:
    allowed is declared as an empty list.

    default:
    None if not specified.

    Validation:
    Any data is allowed. This is the most flexible restriction.

    E.g.:

    class A(DataObject):
        _restrictions = {
            'x': ([], None)
            }

    Here, x can be primitive data types like numbers, strings, boolean, etc.
    It can also be more complex data such as dict, list, set, classes, instances, etc.

    Good choice for data where no validation is necessary.
    """

    def __new__(cls, allowed, default=None, **kwargs):
        return super(_ListNoRestriction, cls).__new__(cls, (allowed, default))

    def __init__(self, *args, **kwargs):
        super(_ListNoRestriction, self).__init__()
        assert isinstance(self._allowed, list) and len(self._allowed) == 0, 'Complain'

    def __call__(self, data, **kwargs):
        return data


class _MgdRestRestriction(AbstractRestriction):
    """
    Manages restriction of type ManagedRestrictions.

    Syntax:
    Specified as an instance of ManagedRestrictions class. See example below.

    allowed:
    allowed is an instance of ManagedRestrictions class.

    default:
    None by default. User can take-over default management in their implementation of ManagedRestrictions.

    Validation:
    Validation is defined by user in ManagedRestrictions class, more specifically, manage method.

    E.g.:

    class ManagedX(ManagedRestrictions):
        _restriction = ([int, float], None)

        def manage(self):
            assert self.data % 2, 'Even numbers not allowed'

    class A(DataObject):
        _restrictions = {
            'x': ManagedX()
            }

    In this example, we allow odd numbers for x. Even numbers are not allowed.
    Good choice for custom data validation.

    For more information on ManagedRestrictions, see ManagedRestrictions class.
    """

    def __new__(cls, allowed, default=None, **kwargs):
        return super(_MgdRestRestriction, cls).__new__(cls, (allowed, default))

    def __call__(self, data, **kwargs):
        return self._allowed(data)


class _DataObjectRestriction(SingletonRestriction):
    """
    Manages restriction of type DataObject.

    Syntax:
    Specified as a class refence to a DO. See example below.

    allowed:
    allowed is a class reference to a DO.

    default:
    None by default.

    Validation:
    Validation is performed by the DataObject.

    E.g.:

    class B(DataObject):
        _restrictions = {
            'x': ([int, float], None)
            }

    class A(DataObject):
        _restrictions = {
            'b': B
            }

    In this example, the value of key 'b' in A._restrictions will be validated by class B, which is also a DataObject.
    Complex data requires data nesting. This typically requires nested DOs, which is supported by this restriction.
    """

    def __new__(cls, allowed, default=None, **kwargs):
        default = allowed(strict=False)
        return super(_DataObjectRestriction, cls).__new__(cls, (allowed, default))

    def __call__(self, data, strict=True, **kwargs):
        if type(data) is self._allowed:
            return data
        elif strict and not isinstance(data, dict):
            raise RestrictionError.bad_data(data, self._allowed)
        return self._allowed(data=data, strict=strict)

    @property
    def dataobj(self):
        return self.allowed


class _NullableDataObjectRestriction(_DataObjectRestriction):
    """
    Manage restriction of type [DataObject, type(None)].

    Syntax:
    Specified as a list containing a class reference to a DO and type(None). See example below.

    allowed:
    allowed is a list containing a class reference to a DO and type(None).

    default:
    None by default.

    Validation:
    Validation is performed by the DataObject. None is allowed.

    E.g.:

    class B(DataObject):
        _restrictions = {
            'x': ([int, float], None)
            }

    class A(DataObject):
        _restrictions = {
            'b': [B, type(None)]
            }

    In this example, the value of key 'b' in A._restrictions will be validated by class B, which is also a DataObject.
    A value of None is also allowed for 'b'.
    """

    def __call__(self, data, **kwargs):
        if data is None:
            return data
        return super(_NullableDataObjectRestriction, self).__call__(data, **kwargs)


class Restriction(object):
    """
    Restriction factory which manages restriction delegation.
    """

    def __new__(cls, allowed, default=None, **kwargs):
        """
        :param allowed: Allowed per restrictions.
        :type allowed: list or ManagedRestrictions or ABCRestrictionMeta
        :param default: Default value.
        """
        if type(default) is type:
            raise RestrictionError.from_invalid_default_value(default)
        if isinstance(allowed, ManagedRestrictions):
            return _MgdRestRestriction(allowed, default=default, **kwargs)
        elif type(allowed) is list:
            if len(allowed) == 0:
                return _ListNoRestriction(allowed, default=default, **kwargs)
            elif len(allowed) == 2 and ABCRestrictionMeta in [type(e) for e in allowed]:
                if type(None) not in allowed:
                    raise RestrictionError.from_unsupported_dataobj_in_rstr_list(allowed)
                return _NullableDataObjectRestriction(allowed[1 - allowed.index(type(None))], default=default, **kwargs)
            elif any([isinstance(r, type) for r in allowed]):
                return _ListTypeRestriction(allowed, default=default, **kwargs)
            else:
                return _ListValueRestriction(allowed, default=default, **kwargs)
        elif type(allowed) is ABCRestrictionMeta:
            return _DataObjectRestriction(allowed, default=default, **kwargs)
        else:
            raise RestrictionError.from_unsupported(allowed)

    def __init__(cls, allowed, default=None, **kwargs):
        """
        Dummy init to support classmethod(s)
        """

    @classmethod
    def legacy(cls, declaration):
        """
        Support of legacy tuple syntax.

        Legacy syntax:
        In current usage of DataObjects, restrictions declarations do not use the specific restriction classes. E.g.,
        ([int, float], None)

        Restriction class syntax:
        The example above can be also be declared using restriction class, i.e.,
        _ListTypeRestriction([int, float], default=None)

        Vision:
        2019-06-06:
        As of this day, the plan is to expose the restrictions classes using simplied syntax. Example,

            R([int, float], default=1)

        Also, there is a plan to collect the most common restrictions into a STL (standard template library). Example,

            In STL,

            R_int = R([int, float])

            In user code,

            class A(DataObject):
                _restrictions = {
                    'x': R_int
                    }

        :param declaration: Legacy tuple syntax
        :type declaration: tuple or list or ManagedRestrictions or ABCRestrictionMeta
        """
        if isinstance(declaration, AbstractRestriction):
            # NOTE: This is already a restriction instance, so nothing to do here.
            return declaration
        if type(declaration) is tuple:
            return cls(declaration[0], default=declaration[1])
        else:
            return cls(declaration)


class ManagedRestrictions(object, with_metaclass(ABCMeta)):
    """
    Useful for managing complex data validations for restrictions in DataObject. E.g.
    1. Regular expression validation such as review URL matches expected template.
    2. Phone number validation and standardization such that number is in ISO format and is SMS enabled.

    DataObject understands that restrictions can be mapped to classes inherited from ManagedRestrictions. When
    DataObject encounters a ManagedRestriction, a call to manage method is made. Managed restriction value is stored in
    data attribute.

    Example:
    A toy example to demonstrate usage. 'name' is a key for Contact and it is managed by Name class. Functionally, the
    Name class ensures that key 'name' is always in title case.

    class Name(ManagedRestrictions):
        _restriction = ([str, unicode], None)

        def manage(self):
            # validation
            assert self.data, 'Invalid name'
            # standardization
            self.data = self.data.title()

    class Contact(DataObject):
        _restrictions: {
            'name': Name(),
            }

    :attribute manage: users must implement validation/standardization logic in manage
    """
    data = None

    def __init__(self):
        self._restriction = Restriction.legacy(self._restriction)

    @abstractproperty
    def _restriction(self):
        """
        Specify restriction for the key this class manages. Follow the same format as _restrictions in DataObject.
        """

    @abstractmethod
    def manage(self):
        """
        Data management logic is handled in this method. This can be used to standardize and/or validate data. Users of
        this class must implement this method. The value to manage can be found in self.data. It is best practice to
        raise exception if data fails validation.
        """

    @property
    def default(self):
        """
        Expose restriction default.
        """
        return self._restriction.default

    def __call__(self, value, strict=True):
        """
        Entry point for data management. DataObject will trigger a call to __call__ when it encounters a managed
        restriction.
        :param value: Data value that needs to be managed
        :param strict: Validation strictness.
        :return: Standardized data
        """
        data_copy = copy.deepcopy(self.data)
        try:
            self.data = value
            if strict:
                self.manage()
        except Exception:
            self.data = data_copy
            raise

        return self.data

    def __eq__(self, other):
        return self._restriction == other._restriction
