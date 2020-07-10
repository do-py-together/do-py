"""
Test the property decorators and related utils.
"""
from do_py.utils.properties import cached_property, is_cached_property, is_classmethod, is_instancemethod, is_property


class ATest(object):
    """
    Dummy class for testing `is_classmethod` and `is_property`.
    """

    @classmethod
    def classmethod(cls):
        """
        Dummy classmethod.
        """

    def method(self):
        """
        Dummy method.
        """

    @property
    def prop(self):
        """
        Dummy property.
        """
        return ''

    @cached_property
    def cached_prop(self):
        """
        Dummy cached property.
        """
        return True


def test_is_classmethod():
    """
    Test the `is_classmethod` util.
    """
    assert is_classmethod(ATest, ATest.classmethod) is True
    assert is_classmethod(ATest, ATest.method) is False


def test_is_instancemethod():
    """
    Test the `is_instancemethod` util.
    """
    assert is_instancemethod(ATest.classmethod) is False
    assert is_instancemethod(ATest.method) is True


def test_is_property():
    """
    Test the `is_property` util.
    """
    assert is_property(ATest.classmethod) is False
    assert is_property(ATest.method) is False
    assert is_property(ATest.prop) is True


def test_is_cached_property():
    """
    Test the `is_cached_property` util.
    """
    assert is_cached_property(ATest.classmethod) is False
    assert is_cached_property(ATest.method) is False
    assert is_cached_property(ATest.prop) is False
    assert is_cached_property(ATest.cached_prop) is True
