import logging

logger = logging.getLogger(__name__)

class ParseError(Exception):
    pass

#data always == dict
def parse_weather(response, city, fetched_at):
    if not isinstance(response, dict):
        raise ParseError("response is not a dict")

    try:
        if not isinstance(response['hourly'], dict):
            raise ParseError("in response 'hourly' is not a dict")
    except KeyError:
        raise ParseError("response has no 'hourly'")

    if not all(e in response['hourly'] for e in ['time', 'temperature_2m']):
        raise ParseError("'hourly' is missing 'time' or 'temperature_2m'")
    else:
        forecast_time = response['hourly']['time']
        temperature = response['hourly']['temperature_2m']

    if not isinstance(forecast_time, list) or not isinstance(temperature, list):
        raise ParseError("'time' and 'temperature_2m' aren't list")

    if None in forecast_time:
        raise ParseError("one or some values are None in 'time'")

    if len(forecast_time) != len(temperature):
        raise ParseError("'time' and 'temperature_2m' are different lengths")

    if forecast_time == [] and temperature == []:
        raise ParseError("forecast is empty")

    response_dict = []
    for t, value in zip(forecast_time,temperature):
        row = {'city': city, 'fetched_at': fetched_at, 'forecast_time': t, 'temperature': value}
        response_dict.append(row)

    logger.info("Successfully parsed weather data")

    return response_dict