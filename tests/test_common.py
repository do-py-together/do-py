"""
:date_created: 2019-07-25
"""

from datetime import datetime

import pytest
from do_py import DataObject

from do_py.exceptions import RestrictionError

from do_py.data_object.common import MgdDatetime, R
from do_py.data_object.restriction import ESR


class TestR(object):
    def test_r_constants(self):
        for attr in [r for r in dir(R) if not r.startswith('__')]:
            assert getattr(R, attr)

    @pytest.mark.parametrize('args, kwargs', [
        ([], {}),
        ([int], {}),
        ([int], {'default': 1}),
        ])
    def test_r_creation(self, args, kwargs):
        assert R(*args, **kwargs)


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


class TestESR(object):
    """
    Tests the util ESR, the compilation of ElasticSearch's mapping declaration structure at restriction level.
    """

    def test_constants(self):
        """
        Tests the static mapping values housed in ESR.
        """
        for attr in [r for r in dir(ESR) if not r.startswith('__')]:
            assert getattr(ESR, attr)

    @pytest.fixture(params=[True, pytest.param(False, marks=pytest.mark.xfail(raises=RestrictionError))])
    def data_object(self, request):
        """
        :rtype: DataObject
        """
        class SampleDO(DataObject):
            _restrictions = {
                'x': R.INT
                }
            es_restrictions = {
                'x': ESR.INT
                }

        class BadSampleDO(DataObject):
            _restrictions = {
                'x': R.INT
                }

        return SampleDO({'x': 1}) if request.param else BadSampleDO

    def test_object(self, data_object):
        """
        Tests the dynamic mapping value creation from a DataObject for nested object mappings.
        :type data_object: DataObject
        """
        assert ESR.OBJECT(data_object)

    def test_nested(self, data_object):
        """
        Tests the dynamic mapping value creation from a DataObject for nested (object list) mappings.
        :type data_object: DataObject
        """
        assert ESR.NESTED(data_object)
