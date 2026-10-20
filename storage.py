def create_table(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS weather_forecast (
            city TEXT NOT NULL,
            fetched_at  TEXT NOT NULL,
            forecast_time TEXT NOT NULL,
            temperature REAL,
            UNIQUE (city, fetched_at, forecast_time)
        )
    """)

def save_to_table(con, rows):
    q = "INSERT INTO weather_forecast (city, fetched_at, forecast_time, temperature) VALUES (:city, :fetched_at, :forecast_time, :temperature) ON CONFLICT DO NOTHING"

    with con:
        con.executemany(q, rows)