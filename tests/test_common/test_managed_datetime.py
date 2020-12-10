"""
:date_created: 2020-06-28
"""
from builtins import object

import pytest
from datetime import datetime

from do_py.common.managed_datetime import MgdDatetime
from do_py.exceptions import RestrictionError


test_dt_instance_epoch = datetime.fromtimestamp(0).replace(microsecond=0)
test_dt_instance = datetime(year=2019, month=9, day=25, hour=10, minute=0, second=0).replace(microsecond=0)
test_dt_instance_now = datetime.now().replace(microsecond=0)
test_date_instance_now = datetime.now().replace(microsecond=0).date()


class TestMgdDatetime(object):

    @pytest.mark.parametrize('input, output', [(test_dt_instance, test_dt_instance),
                                               (test_dt_instance.isoformat(), test_dt_instance),
                                               (None, test_dt_instance_epoch)
                                               ])
    def test_from_datetime(self, input, output):
        instance = MgdDatetime.from_from_datetime()
        assert output == instance(input)

    @pytest.mark.parametrize('input, output', [(test_dt_instance.date(), test_dt_instance.date()),
                                               (test_dt_instance.date().isoformat(), test_dt_instance.date()),
                                               (None, test_dt_instance_epoch.date())
                                               ])
    def test_from_date(self, input, output):
        instance = MgdDatetime.from_from_date()
        assert output == instance(input)

    @pytest.mark.parametrize('input, output', [(test_dt_instance_now, test_dt_instance_now),
                                               (test_dt_instance_now.isoformat(), test_dt_instance_now),
                                               # This creates race condition.
                                               # (None, test_dt_instance_now)
                                               ])
    def test_to_datetime(self, input, output):
        instance = MgdDatetime.from_to_datetime()
        assert output == instance(input)

    @pytest.mark.parametrize('input, output', [(test_dt_instance_now.date(), test_dt_instance_now.date()),
                                               (test_dt_instance_now.date().isoformat(), test_dt_instance_now.date()),
                                               (None, test_dt_instance_now.date())
                                               ])
    def test_from_date(self, input, output):
        instance = MgdDatetime.from_to_date()
        assert output == instance(input)

    @pytest.mark.parametrize('input, output', [(test_dt_instance_now, test_dt_instance_now),
                                               (test_dt_instance_now.isoformat(), test_dt_instance_now),
                                               pytest.param(None, None,
                                                            marks=pytest.mark.xfail(raises=RestrictionError)
                                                            )
                                               ])
    def test_datetime(self, input, output):
        instance = MgdDatetime.datetime()
        assert output == instance(input)

    @pytest.mark.parametrize('input, output', [(test_date_instance_now, test_date_instance_now),
                                               (test_date_instance_now.isoformat(), test_date_instance_now),
                                               pytest.param(None, None,
                                                            marks=pytest.mark.xfail(raises=RestrictionError)
                                                            )
                                               ])
    def test_date(self, input, output):
        instance = MgdDatetime.date()
        assert output == instance(input)

    @pytest.mark.parametrize('input, output', [(test_date_instance_now, test_date_instance_now),
                                               (test_date_instance_now.isoformat(), test_date_instance_now),
                                               (None, None)
                                               ])
    def test_null_date(self, input, output):
        """
        Test the classmethod null_date validates date ISO format properly and handles None.
        :type input:
        :type output:
        """
        instance = MgdDatetime.null_date()
        assert output == instance(input)
