import json
import pathlib
import pytest
import requests

from collector import floor_to_hour, collect_once, TimeError
from datetime import datetime, timezone, timedelta
from open_meteo import FetchError
from weather import ParseError


@pytest.mark.parametrize('t, expected', [
    (datetime(2026, 10, 21, 10, 59, 59, 123456, timezone.utc), '2026-10-21T10:00'),
    (datetime(2026, 10, 21, 10, 0, 0, 0, timezone.utc), '2026-10-21T10:00'),
    (datetime(2026, 10, 21, 23, 59, 59, 12345, timezone.utc), '2026-10-21T23:00'),
    (datetime(2026, 10, 21, 10, 0, 0, 0, timezone(timedelta(hours=2))), '2026-10-21T08:00'),
    (datetime(2026, 10, 21, 1, 30, 0, 0, timezone(timedelta(hours=2))), '2026-10-20T23:00'),
])
def test_floor_to_hour(t, expected):
    assert floor_to_hour(t) == expected


def test_naive_datetime_is_rejected():
    with pytest.raises(TimeError):
        floor_to_hour(datetime(2026, 10, 21, 10, 0, 0, 0))


def load():
    with open(pathlib.Path(__file__).parent / 'forecast.json') as f:
        json_data = json.load(f)
        return json_data

class FakeResponse:
    def __init__(self, data=None, status_code=200):
        self.data = data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError()

    def json(self):
        if self.data is None:
            raise requests.exceptions.JSONDecodeError("bad json", "", 0)

        return self.data

def test_collect_once(monkeypatch, con):
    seen = {}
    def fake(url, **kwargs):
        seen['url'] = url
        seen.update(kwargs)

        return FakeResponse(data=load())

    monkeypatch.setattr(requests, 'get', fake)

    collect_once(con=con, t=datetime(2026, 10, 21, 10, 47, tzinfo=timezone.utc), city='Rome',lat=41.9, lng=12.5)

    assert con.execute("SELECT COUNT(*) FROM weather_forecast WHERE fetched_at = '2026-10-21T10:00' AND city = 'Rome'").fetchone()[0] == 48
    assert seen['params']['latitude'] == 41.9
    assert seen['params']['longitude'] == 12.5

def test_two_collect_once(monkeypatch, con):
    def fake(url, **kwargs):
        return FakeResponse(data=load())

    monkeypatch.setattr(requests, 'get', fake)

    collect_once(con=con, t=datetime(2026, 10, 21, 10, 5, tzinfo=timezone.utc), city='Rome',lat=41.9, lng=12.5)
    collect_once(con=con, t=datetime(2026, 10, 21, 10, 40, tzinfo=timezone.utc), city='Rome',lat=41.9, lng=12.5)

    assert con.execute("SELECT COUNT(*) FROM weather_forecast").fetchone()[0] == 48


def test_different_hours_are_saved_separately(monkeypatch, con):
    def fake(url, **kwargs):
        return FakeResponse(data=load())

    monkeypatch.setattr(requests, 'get', fake)

    collect_once(con=con, t=datetime(2026, 10, 21, 10, 5, tzinfo=timezone.utc), city='Rome',lat=41.9, lng=12.5)
    collect_once(con=con, t=datetime(2026, 10, 21, 11, 5, tzinfo=timezone.utc), city='Rome',lat=41.9, lng=12.5)

    assert con.execute("SELECT COUNT(*) FROM weather_forecast").fetchone()[0] == 96


def test_errortest_fetch_error_propagates_handling_1(monkeypatch, con):
    def fake(url, **kwargs):
        raise requests.exceptions.RequestException()

    monkeypatch.setattr(requests, 'get', fake)

    with pytest.raises(FetchError):
        collect_once(con=con, t=datetime(2026, 10, 21, 10, 5, tzinfo=timezone.utc), city='Rome', lat=41.9, lng=12.5)


def test_parse_error_propagates(monkeypatch, con):
    def fake(url, **kwargs):
        return FakeResponse(data='')

    monkeypatch.setattr(requests, 'get', fake)

    with pytest.raises(ParseError):
        collect_once(con=con, t=datetime(2026, 10, 21, 10, 5, tzinfo=timezone.utc), city='Rome', lat=41.9, lng=12.5)
