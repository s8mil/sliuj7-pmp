def power(df, panel_power, panel_area):
    df["power"] = (
    df["irradiance"] * panel_power / (panel_area * 1000)
    ).round(1)

    return df


def photovoltaic_potential(df, panel_area, panel_quantity):
    df["photovoltaic_power"] = (
    df["power"] * panel_area * panel_quantity
    ).round(1)

    return df

def solar_peak(df):
    return df["irradiance"].sum() / 1000