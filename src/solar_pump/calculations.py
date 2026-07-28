def potency(df, panel_power, panel_area):
    df["potency"] = (
    df["irradiance"] * panel_power / (panel_area * 1000)).round(1)

    return df

def photovoltaic_potential(df, panel_area, panel_quantity):
    df["photovoltaic_power"] = (
    df["potency"] * panel_area * panel_quantity).round(1)

    print(df.to_string(index=False))
    return df