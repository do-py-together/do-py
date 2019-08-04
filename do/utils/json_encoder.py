import json
from datetime import date, datetime


class MyJSONEncoder(json.JSONEncoder):
    """
    TODO
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        return super(MyJSONEncoder, self).default(obj)
