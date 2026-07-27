import location

def location_input():
    option = input(
        "Choose an option:\n"
        "1. City\n"
        "2. Coordinates\n"
        "\nOption: "
    )

    if option == "1":
        while True:
            city = input("Input your desired city: ").strip()

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
        return

    print("\nUsing coordinates:")
    print(latitude, longitude)    

def run():
    location_input()