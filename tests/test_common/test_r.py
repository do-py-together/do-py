"""

:date_created: 2020-06-28
"""
import pytest

from do_py.common import R


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
