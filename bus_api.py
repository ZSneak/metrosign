import board # type: ignore
from adafruit_matrixportal.network import Network # type: ignore

from config import config
from secrets import secrets # type: ignore

# Keeping a global reference for this
_network = Network(status_neopixel=board.NEOPIXEL)

class MetroApiOnFireException(Exception):
    """Custom exception for when the MetroBus API is consistently unreachable."""
    pass

class BusApi:
    """
    A class to interact with the Metro Transit API for bus predictions.
    """

    _DEFAULT_COLOR = 0xADD8E6 # Default color for bus lines

    # A set for quick lookup of destination strings that need normalization.
    _DESTINATION_NORMALIZATIONS = {
        'No Passenger',
        'NoPssenger',
        'ssenger'
    }

    @staticmethod
    def fetch_bus_predictions(stop_id: str, direction_num: str) -> list[dict]:
        """
        Fetches bus predictions for a given station and direction_num.
        Includes retry logic for API connection issues to improve resilience.
        """
        retry_attempt = 0
        # Loop to handle retries instead of recursion, preventing potential stack overflow.
        while retry_attempt <= config['metro_api_retries']:
            try:
                # Use f-string for cleaner URL construction.
                api_url = f"{config['bus_api_url']}{stop_id}"
                headers = {'api_key': config['metro_api_key']}

                # Fetch data from the network and parse as JSON.
                bus_data = _network.fetch(api_url, headers=headers).json()

                print('Received response from WMATA api...')

                # Use a list comprehension for efficient filtering and mapping.
                # .get() is used to safely access dictionary keys, providing a default empty list
                # if 'bus' key is missing, preventing KeyError.
                normalized_results = [
                    BusApi._normalize_bus_response(bus)
                    for bus in bus_data.get('Predictions', [])
                    if bus.get('DirectionNum') == direction_num # Safely check 'direction_num' key.
                ]
                return normalized_results
            except RuntimeError as e:
                # Catch specific network-related errors.
                print(f'Failed to connect to WMATA API. Error: {e}. Reattempting...')
                retry_attempt += 1
        
        # If all retries fail, raise a custom exception with a descriptive message.
        raise MetroApiOnFireException("Failed to fetch bus predictions after multiple retries.")

    @staticmethod
    def _normalize_bus_response(bus: dict) -> dict:
        """
        Normalizes the raw bus response from the API into a more consistent format.
        """
        # Use .get() to safely retrieve values, providing empty strings as defaults
        # to prevent KeyError if keys are missing from the API response.
        line = bus.get('RouteID', '')
        destination = bus.get('DirectionText', '')
        arrival = bus.get('Minutes', '')

        # Check if the destination needs normalization using the predefined set.
        if destination in BusApi._DESTINATION_NORMALIZATIONS:
            destination = 'No Psngr'

        return {
            'line_color': BusApi._get_line_color(line),
            'destination': destination,
            'arrival': arrival
        }
    
    @staticmethod
    def _get_line_color(line: str) -> int:
        """
        Returns the hexadecimal color for a given Metro line code.
        Uses a dictionary lookup for efficiency and readability
        All bus lines are the default config color
        """
        # Use .get() with a default value to handle lines not explicitly defined.
        return config.get("Bus Color", BusApi._DEFAULT_COLOR)
