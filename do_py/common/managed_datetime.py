"""
Houses the commonly used managed restriction, MgdDatetime.
:date_created: 2020-06-28
"""

from datetime import date, datetime

from do_py.common import R
from do_py.data_object.restriction import ManagedRestrictions
from do_py.exceptions import RestrictionError


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
