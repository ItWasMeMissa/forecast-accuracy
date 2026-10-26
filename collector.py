from open_meteo import fetch_forecast, FetchError
from parser import parse_weather, ParseError
from storage import create_table, save_to_table
from datetime import datetime, timezone

import sqlite3

class TimeError(Exception):
    pass

def floor_to_hour(t):
    #time must be in datatime format
    if t.tzinfo is None:
        raise TimeError()

    t = t.astimezone(timezone.utc)
    rounded = t.replace(minute=0)

    return rounded.strftime("%Y-%m-%dT%H:%M")

def collect_once(con, t, city, lat, lng):
    fetched_at = floor_to_hour(t)
    data = fetch_forecast(lat, lng)
    rows = parse_weather(response=data, city=city, fetched_at=fetched_at)

    save_to_table(con, rows)

def main(db_path):
    con = sqlite3.connect(db_path)
    create_table(con)
    try:
        collect_once(con=con, t=datetime.now(timezone.utc), city='Rome',lat=41.9, lng=12.5)
    except FetchError:
        print('fetching error') #todo temporary remake
    except ParseError:
        print('parse error') #todo temporary remake
    finally:
        con.close()