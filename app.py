import datetime
from io import BytesIO
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

import dateutil.relativedelta
import matplotlib

matplotlib.use("Agg")  # headless backend so plt.show() in graph.py can't block

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from solar_pump import calculations
from solar_pump import graph
from solar_pump import irradiance
from solar_pump import location


st.set_page_config(
    page_title="PROJECT protoJ",
    page_icon="☀️",
    layout="wide"
)

# Header (mirrors the CLI banner)

st.title("PROJECT protoJ")
st.caption("Beta v1.0.1")
st.subheader("Photovoltaic Water Pump Sizing Calculator")
st.caption("Development Build")

today = datetime.date.today()
default_end = today - datetime.timedelta(days=1)


# 1. Location

st.header("1. Location")

location_type = st.radio(
    "Choose an option",
    ["City", "Coordinates"],
    horizontal=True
)

city_input = ""
lat_input = None
lon_input = None

if location_type == "City":
    city_input = st.text_input("Input your desired city")
else:
    col1, col2 = st.columns(2)

    with col1:
        lat_input = st.number_input(
            "Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=0.0,
            step=0.0001,
            format="%.6f"
        )

    with col2:
        lon_input = st.number_input(
            "Longitude",
            min_value=-180.0,
            max_value=180.0,
            value=0.0,
            step=0.0001,
            format="%.6f"
        )


# 2. Irradiance dataset

st.header("2. Irradiance dataset")

period = st.selectbox(
    "Choose an irradiance dataset",
    [
        "Last 6 months",
        "Last 5 years",
        "Last 10 years",
        "Custom"
    ]
)

if period == "Custom":
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Enter the start date",
            value=default_end - datetime.timedelta(days=180),
            max_value=default_end
        )

    with col2:
        end_date = st.date_input(
            "Enter the end date",
            value=default_end,
            max_value=default_end
        )

elif period == "Last 6 months":
    end_date = default_end
    start_date = end_date - dateutil.relativedelta.relativedelta(months=6)

elif period == "Last 5 years":
    end_date = default_end
    start_date = end_date - dateutil.relativedelta.relativedelta(years=5)

else:
    end_date = default_end
    start_date = end_date - dateutil.relativedelta.relativedelta(years=10)


# 3. Pump

st.header("3. Pump")

pump_power = st.number_input(
    "Input the pump's power [W]",
    min_value=0.1,
    value=1000.0
)


# 4. Panels

st.header("4. Panels")

col1, col2, col3 = st.columns(3)

with col1:
    panel_power = st.number_input(
        "Input the panel's power [W]",
        min_value=0.1,
        value=550.0
    )

with col2:
    panel_area = st.number_input(
        "Input the panel's area [m²]",
        min_value=0.1,
        value=2.5
    )

with col3:
    panel_quantity = st.number_input(
        "Input the total number of panels",
        min_value=1,
        value=4,
        step=1
    )


# Calculation

def run_calculation():
    """Run the full pipeline and return a results dict, or None on failure."""

    # Location (same validation rules as the CLI)
    if location_type == "City":
        city_name = city_input.strip().title()

        if len(city_name) < 1 or len(city_name) > 100 or city_name.isdigit():
            st.error("City name doesn't meet character requirements.")
            return None

        coordinates = location.city_to_coordinates(city_name)

        if coordinates is None:
            st.error("City not found or geocoding service unavailable.")
            return None

        latitude, longitude = coordinates

    else:
        latitude, longitude = float(lat_input), float(lon_input)

        try:
            found = location.coordinates_to_city(latitude, longitude)
        except Exception:
            found = None

        city_name = found if isinstance(found, str) and found else (
            f"{latitude}, {longitude}"
        )

    if period == "Custom" and start_date > end_date:
        st.error("The start date must be before the end date.")
        return None

    with st.spinner("Retrieving irradiance data..."):
        df = irradiance.get_irradiance(
            latitude,
            longitude,
            start_date,
            end_date
        )

    if df is None or df.empty:
        st.warning("No irradiance data was returned.")
        return None

    quantity = int(panel_quantity)

    df = calculations.power(df, panel_power, panel_area)
    df = calculations.photovoltaic_potential(df, panel_area, quantity)

    df_names = df.rename(columns={
        "irradiance": "Irradiance [W/m²]",
        "power": "Power [W/m²]",
        "photovoltaic_power": "Photovoltaic Power [W]"
    })

    solar_peak = calculations.solar_peak(df)

    # curvegraph may return a figure, or draw on the current one and call
    # plt.show(); handle both cases.
    plt.close("all")
    fig = graph.curvegraph(
        df,
        pump_power,
        city_name,
        solar_peak,
        quantity,
        panel_power
    )

    if fig is None:
        fig = plt.gcf()

    csv_data = df_names.to_csv(index=False).encode("utf-8")

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df_names.to_excel(writer, index=False, sheet_name="Results")

    return {
        "city_name": city_name,
        "latitude": latitude,
        "longitude": longitude,
        "df_names": df_names,
        "solar_peak": solar_peak,
        "fig": fig,
        "csv": csv_data,
        "excel": excel_buffer.getvalue(),
        "total_power": panel_power * quantity,
    }


if st.button("Calculate", type="primary"):
    try:
        st.session_state["results"] = run_calculation()
    except Exception as error:
        st.session_state["results"] = None
        st.error(f"Calculation failed: {error}")


# 5. Results (kept in session_state so download clicks don't wipe them)

results = st.session_state.get("results")

if results:
    st.header("5. Results")

    st.write("**Using coordinates:**")
    st.write(
        f"{results['city_name']} "
        f"({results['latitude']}, {results['longitude']})"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Solar Peak Hour",
            f"{results['solar_peak']:.2f} kWh/kWp/day"
        )

    with col2:
        st.metric(
            "Total installed panel power",
            f"{results['total_power']:,.2f} W"
        )

    st.subheader("Irradiance and power data")
    st.dataframe(results["df_names"])

    st.subheader("Graph")
    st.pyplot(results["fig"])

    st.header("6. Export data")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Download CSV",
            data=results["csv"],
            file_name="solar_pump_results.csv",
            mime="text/csv"
        )

    with col2:
        st.download_button(
            "Download Excel",
            data=results["excel"],
            file_name="solar_pump_results.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            )
        )