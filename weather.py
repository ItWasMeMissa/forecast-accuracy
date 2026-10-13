class ParseError(Exception):
    pass

#data always == dict
def parse_weather(response, city, fetched_at):
    if not isinstance(response, dict):
        raise ParseError()

    try:
        if 'hourly' not in response or not all(e in response['hourly'] for e in ['time', 'temperature_2m']):
            raise ParseError()
        else:
            forecast_time = response['hourly']['time']
            temperature = response['hourly']['temperature_2m']
    except TypeError:
        raise ParseError()

    try:
        if None in forecast_time:
            raise ParseError()
    except TypeError:
        raise ParseError()

    try:
        if len(forecast_time) != len(temperature) :
            raise ParseError()
    except TypeError:
        raise ParseError()

    response_dict = []
    for t, value in zip(forecast_time,temperature):
        response = {'city': city, 'fetched_at': fetched_at, 'forecast_time': t, 'temperature': value}
        response_dict.append(response)

    return response_dict