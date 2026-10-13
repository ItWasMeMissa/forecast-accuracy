import pytest
import json
import pathlib
from weather import parse_weather, ParseError

FIXTURE = pathlib.Path(__file__).parent / 'forecast.json'

def load_sample():
    with open(FIXTURE) as f:
        return json.load(f)

def test_correct_response():
    response = parse_weather(response=load_sample(), city='Rome', fetched_at='x')
    sample = load_sample()

    assert len(response) == 72
    assert response[1]['forecast_time'], response[1]['temperature'] == ('2026-10-09T01:00', 19.7)
    assert response[-1]['forecast_time'], response[-1]['temperature'] == ('2026-10-11T23:00', 18.9)


def test_dict_without_hourly():
    with pytest.raises(ParseError):
        parse_weather(response={'x':67}, city='Rome', fetched_at='x')


def test_dict_with_hourly_without_time_and_without_temperature():
    with pytest.raises(ParseError):
        parse_weather(response={'hourly':{'time':'x','x':'x'}}, city='Rome', fetched_at='x')

    with pytest.raises(ParseError):
        parse_weather(response={'hourly': {'x': 'x', 'temperature_2m': 'x'}}, city='Rome', fetched_at='x')


def test_different_length_of_time_and_temperature():
    with pytest.raises(ParseError):
        parse_weather(response={'hourly': {'time': [1, 2 ,3], 'temperature_2m': [1,2]}}, city='Rome', fetched_at='x')


def test_wrong_data_input():
    with pytest.raises(ParseError):
        parse_weather(response=None, city='Rome', fetched_at='x')

    with pytest.raises(ParseError):
        parse_weather(response='', city='Rome', fetched_at='x')


def test_none_in_forecast_time():
    with pytest.raises(ParseError):
        parse_weather(response={'hourly': {'time': None, 'temperature_2m': [1,2]}}, city='Rome', fetched_at='x')

    with pytest.raises(ParseError):
        parse_weather(response={'hourly': {'time': [1, None], 'temperature_2m': [1,2]}}, city='Rome', fetched_at='x')



def test_none_in_temperature():
    resalt = parse_weather(response={'hourly': {'time': [1, 2, 3], 'temperature_2m': [1, None, 3]}}, city='Rome', fetched_at='x')
    assert resalt[1]['temperature'] is None

    with pytest.raises(ParseError):
        parse_weather(response={'hourly': {'time': [1, 2, 3], 'temperature_2m': None}}, city='Rome', fetched_at='x')