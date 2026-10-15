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
- [ ] Store snapshots in SQLite without duplicates
- [ ] Handle network errors, timeouts and missing values
- [ ] Compute the average error per city and lead time
- [ ] HTTP API (FastAPI)
- [ ] Docker and full documentation

## Known limitations

- "Actual" weather is taken from Open-Meteo's own current values, not from weather stations,
  so this measures consistency of the forecast with the service's own analysis.