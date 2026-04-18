"""
:date_created: 2020-06-28
"""

from datetime import date, datetime

import pytest

from do_py import R
from do_py.common.managed_datetime import MgdDatetime
from do_py.exceptions import RestrictionError

test_dt_instance_epoch = datetime.fromtimestamp(0).replace(microsecond=0)
test_dt_instance = datetime(year=2019, month=9, day=25, hour=10, minute=0, second=0).replace(microsecond=0)
test_dt_instance_now = datetime.now().replace(microsecond=0)
test_date_instance_now = datetime.now().replace(microsecond=0).date()


class TestMgdDatetime:
    """
    Test the instantiation and usages of the managed datetime object.
    """

    @pytest.mark.parametrize(
        'dt_obj, nullable, expected_restriction',
        [
            (datetime, False, R.DATETIME),
            (datetime, True, R.NULL_DATETIME),
            (date, False, R.DATE),
            (date, True, R.NULL_DATE),
            pytest.param(None, True, None, marks=pytest.mark.xfail(raises=AssertionError)),
        ],
    )
    @pytest.mark.parametrize('default_key', ['to', 'from', None])
    def test_restriction(self, dt_obj, nullable, expected_restriction, default_key):
        """
        The correct restriction should be used depending on dt_obj and nullable.
        """
        instance = MgdDatetime(dt_obj=dt_obj, default_key=default_key, nullable=nullable)
        if instance._restriction != expected_restriction:
            raise Exception('instance._restriction != expected_restriction')

    @pytest.mark.parametrize(
        'input, output',
        [
            (test_dt_instance, test_dt_instance),
            (test_dt_instance.isoformat(), test_dt_instance),
            (None, test_dt_instance_epoch),
        ],
    )
    def test_from_datetime(self, input, output):
        """
        :type input: datetime or str or None
        :type output: datetime
        """
        instance = MgdDatetime.from_from_datetime()
        assert output == instance(input)

    @pytest.mark.parametrize(
        'input, output',
        [
            (test_date_instance_now, test_date_instance_now),
            (test_date_instance_now.isoformat(), test_date_instance_now),
            (None, test_dt_instance_epoch.date()),
        ],
    )
    def test_from_date(self, input, output):
        """
        :type input: date or str or None
        :type output: date
        """
        instance = MgdDatetime.from_from_date()
        assert instance(input) == output

    @pytest.mark.parametrize(
        'input, output',
        [
            (test_dt_instance_now, test_dt_instance_now),
            (test_dt_instance_now.isoformat(), test_dt_instance_now),
        ],
    )
    def test_to_datetime(self, input, output):
        """
        :type input: datetime or str or None
        :type output: datetime
        """
        instance = MgdDatetime.from_to_datetime()
        assert instance(input) == output

    @pytest.mark.parametrize(
        'input, output',
        [
            (test_date_instance_now, test_date_instance_now),
            (test_date_instance_now.isoformat(), test_dt_instance_now.date()),
            (None, test_date_instance_now),
        ],
    )
    def test_to_date(self, input, output):
        """
        Test the classmethod `datetime` validates date ISO format properly and handles None.
        :type input: datetime or str
        :type output: datetime or None
        """
        instance = MgdDatetime.from_to_date()
        assert output == instance(input)

    @pytest.mark.parametrize(
        'input, output',
        [
            (test_dt_instance_now, test_dt_instance_now),
            (test_dt_instance_now.isoformat(), test_dt_instance_now),
            pytest.param(test_date_instance_now, None, marks=pytest.mark.xfail(raises=RestrictionError)),
            pytest.param(
                test_date_instance_now.isoformat(),
                test_dt_instance_now,
                marks=pytest.mark.xfail(raises=RestrictionError),
            ),
            pytest.param(None, None, marks=pytest.mark.xfail(raises=RestrictionError)),
        ],
    )
    def test_datetime(self, input, output):
        """
        Test the classmethod `datetime` validates date ISO format properly and handles None.
        :type input: datetime or str or date
        :type output: datetime or None
        """
        instance = MgdDatetime.datetime()
        assert instance(input) == output

    @pytest.mark.parametrize(
        'input, output',
        [
            (test_dt_instance_now, test_dt_instance_now),
            (test_dt_instance_now.isoformat(), test_dt_instance_now),
            pytest.param(test_date_instance_now, None, marks=pytest.mark.xfail(raises=RestrictionError)),
            pytest.param(
                test_date_instance_now.isoformat(),
                test_dt_instance_now,
                marks=pytest.mark.xfail(raises=RestrictionError),
            ),
            pytest.param(None, None),
        ],
    )
    def test_null_datetime(self, input, output):
        """
        Test the classmethod `null_datetime` validates date ISO format properly and handles None.
        :type input: datetime or str or date
        :type output: datetime or None
        """
        instance = MgdDatetime.null_datetime()
        assert instance(input) == output

    @pytest.mark.parametrize(
        'input, output',
        [
            (test_date_instance_now, test_date_instance_now),
            (test_date_instance_now.isoformat(), test_date_instance_now),
            pytest.param(test_dt_instance_now, None, marks=pytest.mark.xfail(raises=RestrictionError)),
            pytest.param(
                test_dt_instance_now.isoformat(),
                test_date_instance_now,
                marks=pytest.mark.xfail(raises=RestrictionError),
            ),
            pytest.param(None, None, marks=pytest.mark.xfail(raises=RestrictionError)),
        ],
    )
    def test_date(self, input, output):
        """
        Test the classmethod `date` validates date ISO format properly and handles None.
        :type input: date or str or datetime
        :type output: date or None
        """
        instance = MgdDatetime.date()
        assert instance(input) == output

    @pytest.mark.parametrize(
        'input, output',
        [
            (test_date_instance_now, test_date_instance_now),
            (test_date_instance_now.isoformat(), test_date_instance_now),
            pytest.param(test_dt_instance_now, None, marks=pytest.mark.xfail(raises=RestrictionError)),
            pytest.param(
                test_dt_instance_now.isoformat(),
                test_date_instance_now,
                marks=pytest.mark.xfail(raises=RestrictionError),
            ),
            (None, None),
        ],
    )
    def test_null_date(self, input, output):
        """
        Test the classmethod `null_date` validates date ISO format properly and handles None.
        :type input: date or str or datetime
        :type output: date or None
        """
        instance = MgdDatetime.null_date()
        assert instance(input) == output


class TestMgdDatetimeMalformedStrings:
    """Test that malformed ISO strings raise RestrictionError via the manage() path."""

    @pytest.mark.parametrize(
        'bad_input',
        [
            'not-a-date',
            '2020-13-45',
            '2020/01/01',
            'hello world',
            '12345',
            '',
        ],
    )
    def test_malformed_datetime_string(self, bad_input):
        """Malformed string should raise RestrictionError from strptime ValueError."""
        instance = MgdDatetime.datetime()
        with pytest.raises(RestrictionError):
            instance(bad_input)

    @pytest.mark.parametrize(
        'bad_input',
        [
            'not-a-date',
            '2020-13-45',
            '2020/01/01',
            '',
        ],
    )
    def test_malformed_date_string(self, bad_input):
        """Malformed date string should raise RestrictionError."""
        instance = MgdDatetime.date()
        with pytest.raises(RestrictionError):
            instance(bad_input)


class TestMgdDatetimeDefaultKeyNone:
    """Test behavior when default_key is None and data is None."""

    def test_datetime_no_default_none_input(self):
        """With no default_key and non-nullable, None should fail restriction."""
        instance = MgdDatetime(dt_obj=datetime, default_key=None, nullable=False)
        with pytest.raises(RestrictionError):
            instance(None)

    def test_datetime_no_default_nullable_none_input(self):
        """With no default_key but nullable, None should pass through."""
        instance = MgdDatetime(dt_obj=datetime, default_key=None, nullable=True)
        result = instance(None)
        assert result is None

    def test_date_no_default_nullable_none_input(self):
        """With no default_key but nullable date, None should pass through."""
        instance = MgdDatetime(dt_obj=date, default_key=None, nullable=True)
        result = instance(None)
        assert result is None


class TestMgdDatetimeInvalidInit:
    """Test that invalid constructor args are rejected."""

    def test_invalid_dt_obj(self):
        """dt_obj must be date or datetime."""
        with pytest.raises(AssertionError):
            MgdDatetime(dt_obj=str)

    def test_invalid_default_key(self):
        """default_key must be None, 'from', or 'to'."""
        with pytest.raises(AssertionError):
            MgdDatetime(dt_obj=datetime, default_key='invalid')


class TestMgdDatetimeMicrosecondStripping:
    """Verify that microseconds are stripped for datetime results."""

    def test_microseconds_stripped(self):
        """datetime results should have microsecond=0."""
        dt_with_micro = datetime(2020, 1, 1, 12, 0, 0, 123456)
        instance = MgdDatetime.datetime()
        result = instance(dt_with_micro)
        assert result.microsecond == 0


class TestMgdDatetimeCrossTypeInputs:
    """Test edge cases: passing wrong type (date to datetime(), datetime to date())."""

    def test_date_instance_to_datetime_restriction_fails(self):
        """Passing a date object to a datetime restriction should fail."""
        instance = MgdDatetime.datetime()
        with pytest.raises(RestrictionError):
            instance(test_date_instance_now)

    def test_datetime_instance_to_date_restriction_fails(self):
        """Passing a datetime object to a date restriction should fail."""
        instance = MgdDatetime.date()
        with pytest.raises(RestrictionError):
            instance(test_dt_instance_now)

    def test_date_isoformat_to_datetime_restriction_fails(self):
        """A date-format ISO string should fail when datetime is expected (too short)."""
        instance = MgdDatetime.datetime()
        with pytest.raises(RestrictionError):
            instance(test_date_instance_now.isoformat())

    def test_datetime_isoformat_to_date_restriction_fails(self):
        """A datetime-format ISO string should fail when date is expected (too long)."""
        instance = MgdDatetime.date()
        with pytest.raises(RestrictionError):
            instance(test_dt_instance_now.isoformat())

    def test_from_from_date_with_datetime_string(self):
        """from_from_date should reject a datetime-format ISO string."""
        instance = MgdDatetime.from_from_date()
        with pytest.raises(RestrictionError):
            instance(test_dt_instance_now.isoformat())

    def test_from_from_datetime_with_date_string(self):
        """from_from_datetime should reject a date-format ISO string."""
        instance = MgdDatetime.from_from_datetime()
        with pytest.raises(RestrictionError):
            instance(test_date_instance_now.isoformat())
