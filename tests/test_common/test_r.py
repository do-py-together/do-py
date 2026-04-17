"""
:date_created: 2020-06-28
"""

import pytest

from do_py.common import R
from do_py.data_object.restriction import AbstractRestriction


class TestR:
    @pytest.mark.parametrize('attr', [r for r in dir(R) if not r.startswith('__')])
    def test_r_constants(self, attr):
        assert getattr(R, attr)

    @pytest.mark.parametrize(
        'args, kwargs',
        [
            ([], {}),
            ([int], {}),
            ([int], {'default': 1}),
        ],
    )
    def test_r_creation(self, args, kwargs):
        assert R(*args, **kwargs)


class TestRShortcuts:
    """Verify each R shortcut returns a valid restriction with correct behavior."""

    @pytest.mark.parametrize(
        'shortcut, valid_value, invalid_value',
        [
            ('INT', 42, 'not_int'),
            ('FLOAT', 3.14, 'not_float'),
            ('STR', 'hello', 123),
            ('BOOL', True, 'not_bool'),
            ('LIST', [1, 2], 'not_list'),
            ('SET', {1, 2}, 'not_set'),
        ],
    )
    def test_type_shortcut(self, shortcut, valid_value, invalid_value):
        """Each type shortcut should accept the correct type and reject others."""
        restriction = getattr(R, shortcut)
        assert isinstance(restriction, AbstractRestriction), '%s did not return an AbstractRestriction' % shortcut
        # Valid value should pass
        result = restriction(valid_value)
        assert result == valid_value
        # Invalid value should raise
        from do_py.exceptions import RestrictionError

        with pytest.raises(RestrictionError):
            restriction(invalid_value)

    @pytest.mark.parametrize(
        'shortcut, none_allowed',
        [
            ('NULL_INT', True),
            ('NULL_FLOAT', True),
            ('NULL_STR', True),
            ('NULL_LIST', True),
            ('NULL_DATETIME', True),
            ('NULL_DATE', True),
            ('NULL_LONG_INT', True),
        ],
    )
    def test_nullable_shortcut_accepts_none(self, shortcut, none_allowed):
        """Nullable shortcuts should accept None."""
        restriction = getattr(R, shortcut)
        assert isinstance(restriction, AbstractRestriction)
        result = restriction(None)
        assert result is None

    @pytest.mark.parametrize(
        'shortcut',
        ['INT', 'FLOAT', 'STR', 'BOOL', 'LIST', 'SET'],
    )
    def test_non_nullable_rejects_none(self, shortcut):
        """Non-nullable shortcuts should reject None."""
        from do_py.exceptions import RestrictionError

        restriction = getattr(R, shortcut)
        with pytest.raises(RestrictionError):
            restriction(None)

    def test_bool_int(self):
        """BOOL_INT should accept 0 and 1 only."""
        from do_py.exceptions import RestrictionError

        r = R.BOOL_INT
        assert r(0) == 0
        assert r(1) == 1
        with pytest.raises(RestrictionError):
            r(2)

    def test_long_int(self):
        """LONG_INT should behave identically to INT in Python 3."""
        r = R.LONG_INT
        assert r(42) == 42

    def test_null_long_int(self):
        """NULL_LONG_INT should accept int and None."""
        r = R.NULL_LONG_INT
        assert r(42) == 42
        assert r(None) is None
