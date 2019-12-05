import copy

from do_py.abc import ABCRestrictions, SystemMessages, ABCRestrictionMeta, classproperty
from do_py.data_object.restriction import Restriction
from do_py.exceptions import RestrictionError, DataObjectError
from .restricted_dict import RestrictedDictMixin


@ABCRestrictions.require('_restrictions')
class DataObject(RestrictedDictMixin):
    """
    This is an interface to implement into any data-oriented child class. This is designed to support
    very tight coupling with data and its structure from DB. Data structure and value validation is provided.

    Intended Implementation: use the mix-ins derived from this interface (Loadable, Listable, etc.). Only inherit this
    class directly to extend the data validations on DataObject instantiation, i.e. reporting DataObject
    validates account meta.

    It is important to note the difference between the attribute and key namespaces. All values assigned in the key
    namespace will be validated against the _restrictions defined.


    Example:
        Data Structure:
        ____________________________________________________________________
        | id INT(11) | value TEXT | created TIMESTAMP | modified TIMESTAMP |

        Matching _restrictions value:
        _restrictions = {
            'id': ([int], None),
            'value': ([str, unicode], None),
            'created': ([int, long], None),
            'modified': ([int, long], None)
            }


    :attribute _restrictions: dictionary defining data structure and valid values.
    """
    _schema = None

    @classmethod
    def __compile__(cls):
        """
        This enforces restrictions. We do not want users to instantiate this class.
        """
        assert type(cls._restrictions) is dict, SystemMessages.REQUIRED_FOR % ('_restrictions', cls.__name__)
        for k in cls._restrictions:
            if hasattr(cls, k):
                raise AttributeError('"%s" is already defined in class namespace!' % k)
            try:
                cls._restrictions[k] = Restriction.legacy(cls._restrictions[k])
            except RestrictionError as e:
                raise DataObjectError.from_restriction_error(k, cls, e)

    @classmethod
    def _validate_data(cls, _restrictions, d, strict=True):
        """
        Validate data as per Data Object (DO) restrictions.

        Strict vs. Non-strict:
        In strict initialization, data must contain all the keys required by DO _restrictions.
        In non-strict initialization, it is acceptable to have some keys missing per DO _restrictions. For all missing
        keys, the default restriction value is used.

        Keyspace Integrity:
        Keys that are not specified in _restrictions are not allowed in strict or non-strict initializations.

        Data Integrity:
        Data is validated in both strict and non-strict mode.

        :param _restrictions: DO restrictions
        :type _restrictions: dict
        :param d: Data
        :type d: dict
        :param strict: strict vs non-strict initialization.
        :type strict: bool
        :return: Validated data. Some restrictions may further apply data standardization.
        :rtype: dict
        :raises DataObjectError: When a key not defined in _restrictions is passed in.
        :raises DataObjectError: When an invalid value is passed in.
        """
        _dict = dict()
        d = {} if d is None else d
        # NOTE: Unrestricted keys are never allowed.
        for k in list(d.keys()):
            if k not in _restrictions:
                raise DataObjectError.from_unknown_key(k, cls)

        # NOTE: Use default in strict for missing keys in data.
        for k, v in _restrictions.items():
            if k not in d:
                if strict:
                    raise DataObjectError.from_required_key(k, cls)
                else:
                    _dict[k] = v.default
            else:
                try:
                    _dict[k] = v(d[k], strict=strict)
                except RestrictionError as e:
                    raise DataObjectError.from_restriction_error(k, cls, e)

        return _dict

    def __init__(self, data=None, strict=True):
        """
        Initialize DataObject.
        :param data: Initialize to this dictionary.
        :param strict: See Strict vs Non-strict initialization comments in _validate_data.
        """
        self._strict = strict
        super(DataObject, self).__init__(self._validate_data(self._restrictions, data, strict=strict))
        # NOTE: Now that we are done loading, we go back to strict mode
        self._strict = True

    def __call__(self, data=None, strict=True):
        """
        This re-initializes the data object.
        :param data: Initialize to this dictionary.
        :param strict: See Strict vs Non-strict initialization comments in _validate_data.
        """
        self.__init__(data=data, strict=strict)
        return self

    def __setitem__(self, item, value):
        """
        This assigns a value to item in the key namespace. This value will undergo data validation.
        """
        super(DataObject, self).__setitem__(item, self._restrictions[item](value))

    def __copy__(self):
        """
        Supports shallow copy of DataObject. This gives user back plain old python dictionary.

        NOTE: Allowing this is questionable. Any nested objects will be copied by reference, meaning unintended
        mutation may happen.
        :return: Python dict equivalent of the DataObject
        :rtype: dict
        """
        return dict(self)

    # TODO: Needs a test
    def __deepcopy__(self, memodict={}):
        """
        Supports deep copying of DataObject. This gives user back plain old python dictionary.
        :param memodict:
        :type memodict:
        :return: python dictionary representation
        :rtype: dict
        """
        # NOTE: this could be an alternative implementation
        # return self.__class__(data=dict(self))
        memodict[id(self)] = self.__copy__()
        return copy.deepcopy(self.__copy__())

    @classproperty
    def schema(cls):
        """
        Schema of data object is its key structure based on restrictions. Nested data objects are also supported.
        :return: schema
        :rtype: dict
        """
        if not cls._schema:
            s = dict()
            for k, v in cls._restrictions.items():
                if type(v) is ABCRestrictionMeta:
                    s[k] = v.schema
                elif type(v) is tuple and type(v[0]) is ABCRestrictionMeta:
                    s[k] = v[0].schema
                else:
                    s[k] = None
            cls._schema = s
        return cls._schema

    def __dir__(self):
        return super(DataObject, self).__dir__() + list(self._restrictions.keys())
