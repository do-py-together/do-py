"""
Advanced DataObject validations.

Certain use-cases require more complex validations or restrictions that cannot be supported without code execution.
The parent class `Validator` allows us to execute code at instantiation and any time a key is updated. A child of
`Validator` is required to define a `_validate` instance method.
"""
from do_py import R
from do_py.data_object.validator import Validator


class Validated(Validator):
    """
    This DataObject validates that we only have one of key or id, but not both. Since this can't be accomplished only
    using restrictions, we are inheriting from `Validator` so we can attach extra validations.
    """
    _restrictions = {
        'key': R.NULL_STR,
        'id': R.NULL_INT
        }

    def _validate(self):
        """
        Validate that we have exactly one of key or id.

        This function runs at instantiation and any time the instance is updated.
        """
        assert any([self.key, self.id]) and not all([self.key, self.id]), \
            'We need exactly one of id or key to not be None.'
