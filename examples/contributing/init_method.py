"""
The `__init__` method.
A DataObject has a special '****init****' function that is responsible for a few things. It grabs the setting for
strict, and calls the `validate_data` function on itself. This is a very important function. Notice that we pass
validate_data 3 variables (not counting cls).

**d** stands for data in this case. This variable takes the data we pass in as a dictionary upon instantiation.

Finally, we have the variable **strict.** This is only used if the user wants to use strict=False instantiation.

Now we arrive at the validate_data function. If no data was passed in, we use an empty dictionary. Next we make sure we
have no unaccounted keys in the data that were not declared inside the _restrictions dictionary. We then check if the
keys inside the _restrictions dictionary belong to the data. An error will be raised in this case, unless strict=False.
In this case the default value for the restriction will be used and added to the **_dict** attribute. Once all the keys
have been checked they will all be inside the **_dict** assuming that there we no errors. Finally, we return _dict. So
whenever a DataObject is instantiated, you will receive a return containing a dictionary of all the data.
"""
from do_py import DataObject
from do_py.exceptions import DataObjectError, RestrictionError


# Below is the __init__ function for DataObject as well as its dependent validate data
def __init__(self, data=None, strict=True):
    self._strict = strict
    super(DataObject, self).__init__(self._validate_data(self._restrictions, data, strict=strict))
    # NOTE: Now that we are done loading, we go back to strict mode
    self._strict = True


@classmethod
def _validate_data(cls, _restrictions, d, strict=True):
    _dict = dict()
    d = {} if d is None else d
    # NOTE: Unrestricted keys are never allowed.
    for k in list(d.keys()):
        if k not in _restrictions:
            raise DataObjectError.from_unknown_key(k, cls)

    # NOTE: Use default in strict for missing keys in data.
    for k, v in _restrictions.items():
        if k not in d:
            if strict:
                raise DataObjectError.from_required_key(k, cls)
            else:
                _dict[k] = v.default
        else:
            try:
                _dict[k] = v(d[k], strict=strict)
            except RestrictionError as e:
                raise DataObjectError.from_restriction_error(k, cls, e)

    return _dict
