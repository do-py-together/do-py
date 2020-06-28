"""

:date_created: 2020-06-28
"""
import pytest

from do_py import DataObject
from do_py.common import R
from do_py.data_object.restriction import ESR
from do_py.exceptions import RestrictionError


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
