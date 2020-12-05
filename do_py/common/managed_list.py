"""
:date_created: 2020-06-28
"""
from do_py.common import R
from do_py.data_object.restriction import ManagedRestrictions
from do_py.exceptions import RestrictionError


class ManagedList(ManagedRestrictions):
    """
    Use this when you need a restriction for a list of DataObject's.
    """
    _restriction = R(list, type(None))

    def __init__(self, obj_cls, nullable=False):
        """
        :param obj_cls: The DO to check each value in the list against.
        :type obj_cls: DataObject
        :param nullable: Valid values are a list of Do's or a NoneType.
        :type nullable: bool
        """
        super(ManagedList, self).__init__()
        self.obj_cls = obj_cls
        self.nullable = nullable

    def manage(self):
        if self.data is not None:
            items = []
            for item in self.data:
                items.append(item if type(item) == self.obj_cls else self.obj_cls(item))
            self.data = items
        else:
            if not self.nullable:
                raise RestrictionError.bad_data(self.data, self._restriction.allowed)


# TODO: Unit tests
class OrderedManagedList(ManagedList):

    def __init__(self, obj_cls, nullable=False, key=None, reverse=False):
        """
        :param obj_cls: DataObject class reference to wrap each object in list.
        :type nullable: bool
        :type key: function
        :type reverse: bool
        """
        self.key = key
        self.reverse = reverse
        super(OrderedManagedList, self).__init__(obj_cls, nullable=nullable)

    def manage(self):
        """
        Sort the data list after ManagedList does its work.
        """
        super(OrderedManagedList, self).manage()
        self.data = sorted(self.data, key=self.key, reverse=self.reverse)
