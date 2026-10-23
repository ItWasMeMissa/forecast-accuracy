import sqlite3
import storage
import json
import pathlib
from weather import parse_weather
import pytest

SAMPLE_PATH = pathlib.Path(__file__).parent / 'forecast.json'

def load():
    with open(SAMPLE_PATH) as f:
        return json.load(f)


def test_normal_handling(con):
    storage.save_to_table(con, parse_weather(load(), 'Rome', 'x'))

    assert con.execute('SELECT COUNT(*) FROM weather_forecast').fetchone()[0] == 48


def test_unique_constraint_rejects_duplicate_row(con):
    storage.save_to_table(con, parse_weather(load(), 'Rome', 'x'))

    q = "INSERT INTO weather_forecast (city, fetched_at, forecast_time, temperature) VALUES (:city, :fetched_at, :forecast_time, :temperature)"

    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
        with con:
            con.executemany(q, parse_weather(load(), 'Rome', 'x'))


def test_two_diff_fetched_at(con):
    storage.save_to_table(con, parse_weather(load(), 'Rome', 'x'))
    storage.save_to_table(con, parse_weather(load(), 'Rome', 'y'))

    assert con.execute('SELECT COUNT(*) FROM weather_forecast').fetchone()[0] == 96


def test_two_same_rows_save(con):
    storage.save_to_table(con, parse_weather(load(), 'Rome', 'x'))
    storage.save_to_table(con, parse_weather(load(), 'Rome', 'x'))

    assert con.execute('SELECT COUNT(*) FROM weather_forecast').fetchone()[0] == 48


def test_two_diff_cities_saves(con):
    storage.save_to_table(con, parse_weather(load(), 'Rome', 'x'))
    storage.save_to_table(con, parse_weather(load(), 'Milan', 'x'))

    assert 96 == con.execute('SELECT COUNT(*) FROM weather_forecast').fetchone()[0]


def test_none_city_is_rejected(con):
    storage.save_to_table(con, parse_weather(load(), 'Rome', 'x'))

    with pytest.raises(sqlite3.IntegrityError):
        storage.save_to_table(con, parse_weather(load(), None, 'x'))

    assert 48 == con.execute('SELECT COUNT(*) FROM weather_forecast').fetchone()[0]


def test_failed_batch_is_rolled_back(con):
    rows = parse_weather(load(), 'Rome', 'x')
    rows[7]['city'] = None

    with pytest.raises(sqlite3.IntegrityError):
        storage.save_to_table(con, rows)

    assert 0 == con.execute('SELECT COUNT(*) FROM weather_forecast').fetchone()[0]


def test_two_diff_connections(tmp_path):
    db = tmp_path / 'test.db'
    con_1 = sqlite3.connect(db)
    storage.create_table(con_1)
    storage.save_to_table(con_1, parse_weather(load(), 'Rome', 'x'))

    con_2 = sqlite3.connect(db)

    assert 48 == con_2.execute('SELECT COUNT(*) FROM weather_forecast').fetchone()[0]

    con_1.close()
    con_2.close()