class RestrictionError(Exception):
    """
    Exceptions for Restrictions.
    """

    @classmethod
    def bad_data(cls, data, allowed):
        """
        Run time error. Data violated restrictions.
        """
        return cls("'%s' not allowed per restriction '%s'" % (data, allowed))

    @classmethod
    def from_mixed_value_and_type(cls, allowed):
        """
        Compile time error. Restriction syntax not allowed.
        """
        return cls("Mixed type and value restrictions unsupported '%s'" % allowed)

    @classmethod
    def from_unsupported_dataobj_in_rstr_list(cls, allowed):
        """
        Compile time error. DO in restriction can only be combined with None type.
        """
        return cls("DataObject in restriction list '%s' only valid with type(None)." % allowed)

    @classmethod
    def from_dataobj_in_rstr_list(cls, allowed):
        """
        Compile time error. DO in restriction cannot be combined other data types (expect None type).
        """
        return cls("DataObjects not allowed in restriction lists '%s'. Use (<DataObject>, <default_value>)" % allowed)

    @classmethod
    def from_invalid_default_value(cls, default):
        """
        Compile time error. Default value for restriction is invalid.
        """
        return cls('Invalid default "%s".' % default)

    @classmethod
    def from_unsupported(cls, allowed):
        """
        Compile time error. Restriction syntax is incorrect.
        """
        return cls("Malformed restriction. Allowed '%s' is of type '%s'." % (allowed, type(allowed)))
