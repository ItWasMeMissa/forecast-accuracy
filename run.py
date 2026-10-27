from pathlib import Path

from collector import main

db_path = Path(__file__).parent / 'forecast-data' / 'weather_forecast.db'

if __name__ == '__main__':
    main(db_path)