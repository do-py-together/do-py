"""

"""

import json

from do_py.utils.json_encoder import MyJSONEncoder


class RestrictedDictMixin(dict):
    """
    Mixin for DataObjects that drops support for methods that allow the structure to be mutable.
    """

    def _unsupported(self, op):
        raise TypeError('%s does not support %s' % (self.__class__.__name__, op))

    def __delitem__(self, k):
        """
        deletion is not allowed in RestrictedDict
        """
        self._unsupported('delete')

    def clear(self):
        """
        clear is not allowed in RestrictedDict
        """
        self._unsupported('clear')

    def pop(self, k, *args):
        """
        pop is not allowed in RestrictedDict
        """
        self._unsupported('pop')

    def popitem(self):
        """
        popitem is not allowed in RestrictedDict
        """
        self._unsupported('popitem')

    def update(self, e=None, **kwargs):
        """
        Equivalent to dict.update(), but it was needed to call RestrictedDict.__setitem__() instead of dict.__setitem__
        """
        self._unsupported('update')

    def __repr__(self):
        return json.dumps(self, cls=MyJSONEncoder)

    def __str__(self):
        return '%s%s' % (self.__class__.__name__, super(RestrictedDictMixin, self).__str__())

    def __setitem__(self, item, value):
        """
        This assigns a value to item in the key and attribute namespaces.
        :param item:
        :param value:
        """
        super(RestrictedDictMixin, self).__setitem__(item, value)

    def __setattr__(self, key, value):
        """
        This assigns a value to key in the attribute namespace. This value will not undergo data validation, unless the
        key exists in the key namespace.
        Note: Value in key namespace is preferred over attribute namespace.
        :param key: dictionary key
        :param value: value to store in dict or instance
        """
        if key in self:
            self[key] = value
        else:
            super(RestrictedDictMixin, self).__setattr__(key, value)

    def __getattr__(self, item):
        """
        Only called when item is not found in the attribute namespace, meaning that we only need to check
        if item exists in the key space.
        :param item: dictionary key
        :return: attribute selected by item key
        :raises AttributeError: KeyErrors are reraised as attribute errors to match attribute getter.
        """
        try:
            return self[item]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, item))

    def __dir__(self):
        dict_dir = dir(dict)
        for x in ['clear', 'pop', 'popitem', 'update', '__delitem__']:
            dict_dir.remove(x)
        return dict_dir
