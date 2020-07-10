"""
:date_created: 2019-08-01
"""
import json

from datetime import date, datetime


class MyJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder used for adding encoding support to datetime/date.
    """

    def default(self, obj):
        """
        :param obj: Object being encoded.
        :return: Encoded format.
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        return super(MyJSONEncoder, self).default(obj)
