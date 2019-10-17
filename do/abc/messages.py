"""
System messages to directly support error messages in base_model modules.
:date_created: 2018-12-05
:author: Tim Davis
"""


class SystemMessages(object):
    inactive_account = 'Inactive account!'
    missing_account_meta = 'Account Meta missing for pulsem account!'
    invalid_pulsem_account_id = 'Invalid pulsem account id!'
    required_argument = '%s is required for %s!'
    expected_data_set = "Data set %s of %s is missing!"
    value_not_allowed = '%s is not allowed for %s!'
    FETCH_LIMIT_EXCEEDED = 'Attempted to fetch %s items but the limit is %s.'
    GENERIC = 'Unknown error.'
    GENERIC_SENTRY = '{} %s'.format(GENERIC)
    instantiation_error = 'Base class may not be instantiated'
    new_in_abc_restrictions = 'Found __new__ in class!'
    meta_in_abc_restrictions = 'Found __metaclass__ in class!'
    restrictions_allowed = 'Requirements can only be assigned to Root and Node-type classes!'
    class_already_defined = 'Class already defined in ABCRestrictions!'
    attribute_already_declared = '%s attribute "%s" has already been declared in %s!'
