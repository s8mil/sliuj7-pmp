
import geopy

geolocator = geopy.geocoders.Nominatim(
    user_agent="solar_project"
)


def city_to_coordinates(city, verbose=True):
    try:
        result = geolocator.geocode(city)

        if result is None:
            if verbose:
                print("City not found.")
            return None

    except geopy.exc.GeocoderServiceError:
        if verbose:
            print("Unable to connect to the geocoding service.")
        return None

    if verbose:
        print(f"You have selected: {result.address}")

    return result.latitude, result.longitude


def coordinates_to_city(latitude, longitude, verbose=True):
    try:
        result = geolocator.reverse((latitude, longitude))

        if result is None:
            if verbose:
                print("No nearby location found.")
            return None

        if verbose:
            print(f"Nearest location: {result.address}")

    except geopy.exc.GeocoderServiceError:
        if verbose:
            print("Unable to connect to the geocoding service.")
        return None

    return latitude, longitude
