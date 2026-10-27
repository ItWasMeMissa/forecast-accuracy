import requests
import logging


URL = "https://api.open-meteo.com/v1/forecast"


logger = logging.getLogger(__name__)

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

        logger.info("got forecast")

        return r.json()
    except requests.exceptions.RequestException as e:
        raise FetchError("request failed") from e
