import datetime
from turtle import width
import export
import dateutil.relativedelta
import location
import irradiance
import calculations
import graph

today = datetime.date.today()

def location_input():
    while True:
        option = input(
            "\nChoose an option:\n"
            "0. Close\n"
            "1. City\n"
            "2. Coordinates\n"
            "\nOption: "
        )

        if option == "0":
            return None
        if option == "1":
            while True:
                city = input("Input your desired city: ").strip()

                if len(city) > 100 or len(city) < 1 or city.isdigit():
                    print("City name doesn't meet character requirements.")
                    return None

                result = location.city_to_coordinates(city)

                if result is None:
                    continue

                latitude, longitude = result
                break

        elif option == "2":
            while True:
                try:
                    latitude = float(input("Latitude: "))

                    if not (-90 <= latitude <= 90):
                        print("Latitude out of Earth's bounds.\n")
                        continue

                    longitude = float(input("Longitude: "))

                    if not (-180 <= longitude <= 180):
                        print("Longitude out of Earth's bounds.\n")
                        continue

                except ValueError:
                    print("Must be a valid numeric value.\n")
                    continue
                break

            location.coordinates_to_city(latitude, longitude)

        else:
            print("Invalid option.")
            continue
    
        choice = input("\nContinue? Y/N\n").strip().lower()
        if choice == "y":
            break
        if choice == "n":
            continue
        else:
            print("Invalid option.")
            continue
    
    print("\nUsing coordinates:")
    print(latitude, longitude)  

    return latitude, longitude

def irradiance_input():
    while True:
        option = input(
            "Choose an irradiance dataset:\n"
            "0. Cancel\n"
            "1. Last 6 months\n"
            "2. Last 5 years\n"
            "3. Last 10 years\n"
            "4. Custom\n"
            "\nOption: "
        )

        end_date = today - datetime.timedelta(days=1)

        if option == "0":
            print("Irradiance selection cancelled.")
            return None, None

        if option == "1":
            start_date = end_date - dateutil.relativedelta.relativedelta(months=6)
            break

        elif option == "2":
            start_date = end_date - dateutil.relativedelta.relativedelta(years=5)
            break

        elif option == "3":
            start_date = end_date - dateutil.relativedelta.relativedelta(years=10)
            break

        elif option == "4":
            start_date = datetime.datetime.strptime(
                input("Enter the start date (YYYY-MM-DD): "),
                "%Y-%m-%d"
            ).date()

            end_date = datetime.datetime.strptime(
                input("Enter the end date (YYYY-MM-DD): "),
                "%Y-%m-%d"
            ).date()
            break

        else:
            print("Invalid option.")
            continue

    return start_date, end_date
    

def pump_input():
    power = float(input("Input the pumps power:\n"))
    return power

def panel_input():
    power = float(input("Input the panel's power:\n"))
    area = float(input("Input the panel's area:\n"))
    quantity = int(input("Input the total number of panels:\n"))
    return power, area, quantity

def export_data(df):
    while True:
        option = input(
            "Choose an exporting option:\n"
            "0. Cancel\n"
            "1. CSV\n"
            "2. Excel\n\n"
            "Option: "
        )

        if option == "1":
            export.export_csv(df)
            break

        elif option == "2":
            export.export_excel(df)
            break

        elif option == "0":
            print("Export cancelled.")
            break

        else:
            print("Invalid option.")


def export_data(df):
    while True:
        option = input(
            "Choose an exporting option:\n"
            "0. Cancel\n"
            "1. CSV\n"
            "2. Excel\n\n"
            "Option: "
        )

        if option == "1":
            export.export_csv(df)
            break

        elif option == "2":
            export.export_excel(df)
            break

        elif option == "0":
            print("Export cancelled.")
            break

        else:
            print("Invalid option.")

def run():
    width = 60

    print("=" * width)
    print("PROJECT protoJ".center(width))
    print("Build_0.280726_alpha".center(width))
    print("=" * width)
    print("Photovoltaic Water Pump Sizing Calculator".center(width))
    print("Development Build".center(width))
    print("=" * width)
    
    while True:

        result = location_input()

        if result is None:
            print("Closing...")
            break

        latitude, longitude = result

        start_date, end_date = irradiance_input()

        if start_date is None:
            continue

        df = irradiance.get_irradiance(
            latitude,
            longitude,
            start_date,
            end_date
        )

        pump_power = pump_input()

        panel_power, panel_area, panel_quantity = panel_input()

        df = calculations.potency(
            df,
            panel_power,
            panel_area
        )

        df = calculations.photovoltaic_potential(
            df,
            panel_area,
            panel_quantity
        )

        graph.curvegraph(
            df,
            pump_power
        )

        if input("\nDo you want to export the data? (Y/N): ").strip().lower() == "y":
            export_data(df)

        if input("\nNew calculation? (Y/N): ").strip().lower() == "n":
            print("Goodbye!")
            break



