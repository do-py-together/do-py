"""
System messages to directly support error messages in base_model modules.
:date_created: 2018-12-05
:author: Tim Davis
"""


class SystemMessages(object):
    REQUIRED_FOR = '%s is required for %s!'
    GENERIC = 'Unknown error.'
    INSTANTIATION_ERROR = 'Base class may not be instantiated'
    restrictions_allowed = 'Requirements can only be assigned to Root and Node-type classes!'
    class_already_defined = 'Class already defined in ABCRestrictions!'
    attribute_already_declared = '%s attribute "%s" has already been declared in %s!'
