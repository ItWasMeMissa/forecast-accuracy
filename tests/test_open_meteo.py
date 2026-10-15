import pytest
import requests
import open_meteo

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


def test_ok(monkeypatch):
    def fake_get(url, **kwargs):
        return FakeResponse(data={"hourly": {}})

    monkeypatch.setattr(requests, "get", fake_get)

    assert open_meteo.fetch_forecast(41.9, 12.5) == {"hourly": {}}


def test_timeout(monkeypatch):
    def fake_get(url, **kwargs):
        raise requests.exceptions.ReadTimeout()

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(open_meteo.FetchError):
        open_meteo.fetch_forecast(41.9, 12.5)


def test_connect_error(monkeypatch):
    def fake_get(url, **kwargs):
        raise requests.exceptions.ConnectionError()

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(open_meteo.FetchError):
        open_meteo.fetch_forecast(41.9, 12.5)


def test_send_parameters(monkeypatch):
    seen = {}
    def fake_get(url, **kwargs):
        seen['url'] = url

        seen.update(kwargs)
        return FakeResponse(data={})

    monkeypatch.setattr(requests, "get", fake_get)

    open_meteo.fetch_forecast(41.9, 12.5)

    assert seen == {
        'params': {
            'forecast_days': 2,
            'hourly': 'temperature_2m',
            'latitude': 41.9,
            'longitude': 12.5,
            'timezone': 'GMT'},
        'timeout': (3, 10),
        'url': 'https://api.open-meteo.com/v1/forecast'
    }

@pytest.mark.parametrize('code', [400, 429, 500, 503])
def test_http_error(monkeypatch, code):
    def fake_get(url, **kwargs):
        return FakeResponse(status_code=code)

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(open_meteo.FetchError):
        open_meteo.fetch_forecast(41.9, 12.5)


def test_not_json(monkeypatch):
    def fake_get(url, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(open_meteo.FetchError):
        open_meteo.fetch_forecast(41.9, 12.5)