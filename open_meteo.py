import requests

URL = "https://api.open-meteo.com/v1/forecast"


class FetchError(Exception):
    pass


def fetch_forecast(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
        "timezone": "GMT",
        "forecast_days": 2
    }

    try:
        r = requests.get(URL, params=params, timeout=(3, 10))
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        raise FetchError("request failed") from e
