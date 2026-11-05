import sys
from pathlib import Path
import logging

from collector import main

if __name__ == '__main__':
    db_path = Path(__file__).parent / 'forecast-data' / 'weather_forecast.db'
    log_path = Path(__file__).parent / 'forecast-data' / 'collector.log'
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    sys.exit(main(db_path))