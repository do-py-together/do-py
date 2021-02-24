"""
:date_created: 2020-06-28
"""
from datetime import date, datetime

import pytest
from builtins import object

from do_py import R
from do_py.common.managed_datetime import MgdDatetime
from do_py.exceptions import RestrictionError


test_dt_instance_epoch = datetime.fromtimestamp(0).replace(microsecond=0)
test_dt_instance = datetime(year=2019, month=9, day=25, hour=10, minute=0, second=0).replace(microsecond=0)
test_dt_instance_now = datetime.now().replace(microsecond=0)
test_date_instance_now = datetime.now().replace(microsecond=0).date()


class TestMgdDatetime(object):
    """
    Test the instantiation and usages of the managed datetime object.
    """

    @pytest.mark.parametrize('dt_obj, nullable, expected_restriction', [
        (datetime, False, R.DATETIME),
        (datetime, True, R.NULL_DATETIME),
        (date, False, R.DATE),
        (date, True, R.NULL_DATE),
        pytest.param(None, True, None, marks=pytest.mark.xfail(raises=AssertionError))
        ])
    @pytest.mark.parametrize('default_key', [
        'to',
        'from',
        None
        ])
    def test_restriction(self, dt_obj, nullable, expected_restriction, default_key):
        """
        The correct restriction should be used depending on dt_obj and nullable.
        """
        instance = MgdDatetime(dt_obj=dt_obj, default_key=default_key, nullable=nullable)
        assert instance._restriction == expected_restriction

    @pytest.mark.parametrize('input, output', [
        (test_dt_instance, test_dt_instance),
        (test_dt_instance.isoformat(), test_dt_instance),
        (None, test_dt_instance_epoch)
        ])
    def test_from_datetime(self, input, output):
        """
        :type input: datetime or str or None
        :type output: datetime
        """
        instance = MgdDatetime.from_from_datetime()
        assert output == instance(input)

    @pytest.mark.parametrize('input, output', [
        (test_date_instance_now, test_date_instance_now),
        (test_date_instance_now.isoformat(), test_date_instance_now),
        (None, test_dt_instance_epoch.date())
        ])
    def test_from_date(self, input, output):
        """
        :type input: date or str or None
        :type output: date
        """
        instance = MgdDatetime.from_from_date()
        assert instance(input) == output

    @pytest.mark.parametrize('input, output', [
        (test_dt_instance_now, test_dt_instance_now),
        (test_dt_instance_now.isoformat(), test_dt_instance_now),
        # This creates race condition.
        # pytest.param(None, test_dt_instance_now, marks=pytest.mark.xfail(raises=RestrictionError))
        ])
    def test_to_datetime(self, input, output):
        """
        :type input: datetime or str or None
        :type output: datetime
        """
        instance = MgdDatetime.from_to_datetime()
        assert instance(input) == output

    @pytest.mark.parametrize('input, output', [
        (test_date_instance_now, test_date_instance_now),
        (test_date_instance_now.isoformat(), test_dt_instance_now.date()),
        (None, test_date_instance_now)
        ])
    def test_to_date(self, input, output):
        """
        Test the classmethod `datetime` validates date ISO format properly and handles None.
        :type input: datetime or str
        :type output: datetime or None
        """
        instance = MgdDatetime.from_to_date()
        assert output == instance(input)

    @pytest.mark.parametrize('input, output', [
        (test_dt_instance_now, test_dt_instance_now),
        (test_dt_instance_now.isoformat(), test_dt_instance_now),
        pytest.param(test_date_instance_now, None, marks=pytest.mark.xfail(raises=RestrictionError)),
        pytest.param(test_date_instance_now.isoformat(), test_dt_instance_now,
                     marks=pytest.mark.xfail(raises=ValueError)),
        pytest.param(None, None, marks=pytest.mark.xfail(raises=RestrictionError))
        ])
    def test_datetime(self, input, output):
        """
        Test the classmethod `datetime` validates date ISO format properly and handles None.
        :type input: datetime or str or date
        :type output: datetime or None
        """
        instance = MgdDatetime.datetime()
        assert instance(input) == output

    @pytest.mark.parametrize('input, output', [
        (test_dt_instance_now, test_dt_instance_now),
        (test_dt_instance_now.isoformat(), test_dt_instance_now),
        pytest.param(test_date_instance_now, None, marks=pytest.mark.xfail(raises=RestrictionError)),
        pytest.param(test_date_instance_now.isoformat(), test_dt_instance_now,
                     marks=pytest.mark.xfail(raises=ValueError)),
        pytest.param(None, None)
        ])
    def test_null_datetime(self, input, output):
        """
        Test the classmethod `null_datetime` validates date ISO format properly and handles None.
        :type input: datetime or str or date
        :type output: datetime or None
        """
        instance = MgdDatetime.null_datetime()
        assert instance(input) == output

    @pytest.mark.parametrize('input, output', [
        (test_date_instance_now, test_date_instance_now),
        (test_date_instance_now.isoformat(), test_date_instance_now),
        pytest.param(test_dt_instance_now, None, marks=pytest.mark.xfail(raises=RestrictionError)),
        pytest.param(test_dt_instance_now.isoformat(), test_date_instance_now,
                     marks=pytest.mark.xfail(raises=ValueError)),
        pytest.param(None, None, marks=pytest.mark.xfail(raises=RestrictionError))
        ])
    def test_date(self, input, output):
        """
        Test the classmethod `date` validates date ISO format properly and handles None.
        :type input: date or str or datetime
        :type output: date or None
        """
        instance = MgdDatetime.date()
        assert instance(input) == output

    @pytest.mark.parametrize('input, output', [
        (test_date_instance_now, test_date_instance_now),
        (test_date_instance_now.isoformat(), test_date_instance_now),
        pytest.param(test_dt_instance_now, None, marks=pytest.mark.xfail(raises=RestrictionError)),
        pytest.param(test_dt_instance_now.isoformat(), test_date_instance_now,
                     marks=pytest.mark.xfail(raises=ValueError)),
        (None, None)
        ])
    def test_null_date(self, input, output):
        """
        Test the classmethod `null_date` validates date ISO format properly and handles None.
        :type input: date or str or datetime
        :type output: date or None
        """
        instance = MgdDatetime.null_date()
        assert instance(input) == output
