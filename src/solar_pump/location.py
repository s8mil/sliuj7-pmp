import geopy

geolocator = geopy.geocoders.Nominatim(user_agent="solar_project")

def city_to_coordinates(city):
    try:
        result = geolocator.geocode(city)

        if result is None:
            print("City not found.")
            return None
                    
    except geopy.exc.GeocoderServiceError:
        print("Unable to connect to the geocoding service.")
        return None
       
    latitude = result.latitude
    longitude = result.longitude

    print(f"You have selected: {result.address}")

    return latitude, longitude

def coordinates_to_city(latitude, longitude):
    try:
        result = geolocator.reverse((latitude, longitude))

        if result is None:
            print("No nearby location found.")
            return None

        print(f"Nearest location: {result.address}")

    except geopy.exc.GeocoderServiceError:
        print("Unable to connect to the geocoding service.")
        return None

    return latitude, longitude