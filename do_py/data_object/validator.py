"""

:date_created: 2019-08-18
"""

import copy

from do_py import DataObject
from do_py.abc import ABCRestrictions


@ABCRestrictions.require('_validate')
class Validator(DataObject):
    """
    Validator provides capability for more complex data validations. Use ManagedRestrictions for simpler single key
    validations and standardizations. In certain DataObjects, the keys are mutually dependent in the sense that the
    value one key stores depends on what the other key(s) are storing. E.g., consider the data object in the example
    below. Cities 'Dallas' and 'Los Angeles' are only valid with 'TX' and 'CA', respectively. 'Dallas' combined with
    'TX' should be rejected. Validator provides a solution for such problems. In some situations, a combination of
    ManagedRestrictions and Validator may be required.

    Users should implement _validate method and include the validation logic.

    NOTE: This is heavy. Use ManagedRestrictions if possible.

    Example:
        class Address(DataObject):
            _restrictions = {
                'city': (['Dallas', 'Los Angeles'], None),
                'state': (['TX', 'CA'], None)
                }

    :attribute _validate: a validation function to validate data for mutually dependent keys
    """
    _is_abstract_ = True

    def __init__(self, data=None, strict=True):
        super(Validator, self).__init__(data=data, strict=strict)
        if strict:
            self._validate()

    def __setitem__(self, key, value):
        """
        A copy of current data is cached before running _validate. In case of exception, the data is restored using
        the copy.
        """
        self_copy = copy.deepcopy(self)
        super(Validator, self).__setitem__(key, value)
        try:
            # Additional validation
            self._validate()
        except:
            self(data=self_copy)
            raise

    def _validate(self):
        """
        Must be implemented by user. Place all validation logic in this method.
        """
        raise NotImplementedError('_validate must be implemented!')
