import openmeteo_requests
from datetime import datetime
import pandas as pd
import requests_cache
from retry_requests import retry

FIELD_MAP = {
    "temperature_2m": "temperature",
    "relativehumidity_2m": "humidity",
    "precipitation": "precipitation"
}

def cleanWeather(url, params):
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    response = openmeteo.weather_api(url, params=params)[0]

    hourly = response.Hourly()

    hourly_data = {"timestamp": pd.date_range(
        start = pd.to_datetime(hourly.Time() + response.UtcOffsetSeconds(), unit = "s", utc = True),
        end =  pd.to_datetime(hourly.TimeEnd() + response.UtcOffsetSeconds(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}


    requested_fields = params["hourly"]
    if isinstance(requested_fields, str):
        requested_fields = requested_fields.replace(" ", "").split(",")



    for i, field in enumerate(requested_fields):
        column_name = FIELD_MAP.get(field, field)
        
        hourly_data[column_name] = hourly.Variables(i).ValuesAsNumpy()

    df = pd.DataFrame(data=hourly_data)
    df = df.round(2)
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    return df
