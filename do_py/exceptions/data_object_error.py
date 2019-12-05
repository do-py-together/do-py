class DataObjectError(Exception):
    """
    Errors related to restriction and data keys.
    """

    @classmethod
    def from_unknown_key(cls, key, cls_ref):
        """
        Compile time error. Not allowed to pass a key to DO that was not declared in restrictions.
        """
        return cls("%s: Unexpected key '%s' in data." % (cls_ref.__name__, key))

    @classmethod
    def from_required_key(cls, key, cls_ref):
        """
        Run time error. A required key was absent in data.
        """
        return cls("%s: Key '%s' required in data." % (cls_ref.__name__, key))

    @classmethod
    def from_restriction_error(cls, key, cls_ref, restriction_error):
        """
        Run time error. An error captured from restriction layer is enhanced by adding class reference and key info.
        Finally rethrown.

        Movation:
        Catch -> Rethrow to add more information that would save debugging time.
        """
        return cls("%s.%s: %s" % (cls_ref.__name__, key, restriction_error))
