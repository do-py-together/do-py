"""
:date_created: 2020-06-28
"""

from builtins import object

import pytest

from do_py.common import R


class TestR(object):

    @pytest.mark.parametrize('attr', [r for r in dir(R) if not r.startswith('__')])
    def test_r_constants(self, attr):
        assert getattr(R, attr)

    @pytest.mark.parametrize('args, kwargs', [
        ([], {}),
        ([int], {}),
        ([int], {'default': 1}),
        ])
    def test_r_creation(self, args, kwargs):
        assert R(*args, **kwargs)
