# forecast-accuracy

Collects hourly weather forecasts from Open-Meteo and measures how accurate they are,
depending on how far ahead the forecast was made.

## Status

In development. See the checklist below.

## The question

If a forecast says "tomorrow at 15:00 it will be 21 degrees", how far off is it on average?
Is a forecast made 6 hours ahead better than one made 48 hours ahead, and does it depend on the city?

## Data source

Weather data by [Open-Meteo.com](https://open-meteo.com/) (free API, non-commercial use).
Data is licensed under [CC BY 4.0](https://open-meteo.com/en/licence). Forecast values are stored unchanged.

## Plan

- [x] Fetch and parse a forecast for one city
- [x] Store snapshots in SQLite without duplicates
- [x] Collector (one run)
- [x] Logging and exit codes
- [ ] Hourly schedule
- [ ] Handle network errors, timeouts and missing values
- [ ] Compute the average error per city and lead time
- [ ] HTTP API (FastAPI)
- [ ] Docker and full documentation

## Known limitations

- "Actual" weather is taken from Open-Meteo's own current values, not from weather stations,
  so this measures consistency of the forecast with the service's own analysis.

## How it works

Each run does one pass through the pipeline:

1. `collector.py` takes the current UTC time and floors it to the hour (`fetched_at`).
2. `open_meteo.py` requests a 48-hour temperature forecast.
3. `parser.py` validates the response and turns it into rows.
4. `storage.py` saves the rows into SQLite, skipping duplicates.

Running twice within the same hour does not create duplicates.

## Quick start

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-dev.txt
    pytest
    python run.py

The database is created at `forecast-data/weather_forecast.db`.
Tests never use the real network.

## Data

Table `weather_forecast`: `city`, `fetched_at`, `forecast_time`, `temperature`.
A row is unique by `(city, fetched_at, forecast_time)`, so forecasts for the same
hour made at different times are all kept. This is what makes accuracy by lead time possible.
All times are UTC, ISO strings.