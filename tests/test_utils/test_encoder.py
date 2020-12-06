import json
from builtins import object

from datetime import datetime

from do_py.utils.json_encoder import MyJSONEncoder


class TestMyJSONEncoder(object):

    def test(self):
        today_datetime = datetime.today()
        today_date = today_datetime.date()
        d = dict(datetime=today_datetime, date=today_date, x=2)
        data = json.loads(json.dumps(d, cls=MyJSONEncoder))
        assert data['datetime'] == today_datetime.isoformat()
        assert data['date'] == today_date.isoformat()
        assert data['x'] == 2
