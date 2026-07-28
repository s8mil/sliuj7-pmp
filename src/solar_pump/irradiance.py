import requests
import pandas as pd

def get_irradiance(latitude, longitude, start_date, end_date):

    start = start_date.strftime("%Y%m%d")
    end = end_date.strftime("%Y%m%d")
    url = ("https://power.larc.nasa.gov/api/temporal/hourly/point")

    params = {
    "parameters": "ALLSKY_SFC_SW_DWN",
    "community": "RE",
    "longitude": longitude,
    "latitude": latitude,
    "start": start,
    "end": end,
    "format": "JSON",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    if "properties" not in data:
        raise ValueError("No irradiance data received from NASA POWER.")

    irradiance = data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]

    df = pd.DataFrame(
    irradiance.items(),
    columns=["datetime", "irradiance"]
    )

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        format="%Y%m%d%H"
    )

    df = df[df["irradiance"] != -999]
    df["hour"] = df["datetime"].dt.hour

    df = (
        df.groupby("hour", as_index=False)["irradiance"]
        .mean()
    )

    df["interval"] = df["hour"].apply(
    lambda h: f"{h:02d}:00-{(h + 1) % 24:02d}:00"
    )

    df = df.drop(columns="hour")
    df["irradiance"] = (df["irradiance"]).round(1)

    df = df[["interval", "irradiance"]]

    return df