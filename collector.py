import sys

from open_meteo import fetch_forecast, FetchError
from parser import parse_weather, ParseError
from storage import create_table, save_to_table
from datetime import datetime, timezone

import sqlite3
import logging

logger = logging.getLogger(__name__)

class TimeError(Exception):
    pass

def floor_to_hour(t):
    #time must be in datatime format
    if t.tzinfo is None:
        raise TimeError("given time is not utc or auto picked by your system")

    t = t.astimezone(timezone.utc)
    rounded = t.replace(minute=0)

    return rounded.strftime("%Y-%m-%dT%H:%M")

def collect_once(con, t, city, lat, lng):
    fetched_at = floor_to_hour(t)
    data = fetch_forecast(lat, lng)
    rows = parse_weather(response=data, city=city, fetched_at=fetched_at)

    num_of_saved = save_to_table(con, rows)

    logger.info("saved %d new rows for %s at %s", num_of_saved, city, fetched_at)

def main(db_path):
    db_path.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(db_path)
    logger.info("connected to database %s", db_path)
    create_table(con)
    try:
        collect_once(con=con, t=datetime.now(timezone.utc), city='Rome',lat=41.9, lng=12.5)
    except FetchError:
        logger.exception("fetch failed")
        return 1
    except ParseError:
        logger.exception("could not parse forecast")
        return 1
    finally:
        con.close()

    return 0