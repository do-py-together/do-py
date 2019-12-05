"""
System messages to directly support error messages in base_model modules.
:date_created: 2018-12-05
:author: Tim Davis
"""

from builtins import object


class SystemMessages(object):
    REQUIRED_FOR = '%s is required for %s!'
    GENERIC = 'Unknown error.'
    INSTANTIATION_ERROR = 'Base class may not be instantiated'
    RESTRICTIONS_ALLOWED = 'Requirements can only be assigned to Root and Node-type classes!'
    CLASS_ALREADY_DEFINED = 'Class already defined in ABCRestrictions!'
    ATTRIBUTE_ALREADY_DECLARED = '%s attribute "%s" has already been declared in %s!'
