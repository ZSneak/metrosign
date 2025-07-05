import board # type: ignore
from adafruit_matrixportal.network import Network # type: ignore

from config import config
from secrets import secrets # type: ignore

# Keeping a global reference for this
_network = Network(status_neopixel=board.NEOPIXEL)

class MetroApiOnFireException(Exception):
    """Custom exception for when the Metro API is consistently unreachable."""
    pass

class MetroApi:
    """
    A class to interact with the Metro Transit API for train predictions.
    """

    # Class-level dictionary for line colors, making it easy to extend and read.
    _LINE_COLORS = {
        'RD': 0xFF0000,  # Red
        'OR': 0xFF5500,  # Orange
        'YL': 0xFFFF00,  # Yellow
        'GR': 0x00FF00,  # Green
        'BL': 0x0000FF,  # Blue
        'SV': 0xC0C0C0,  # Silver (commonly used, added for completeness)
    }
    _DEFAULT_COLOR = 0xAAAAAA # Default color for unknown lines

    # A set for quick lookup of destination strings that need normalization.
    _DESTINATION_NORMALIZATIONS = {
        'No Passenger',
        'NoPssenger',
        'ssenger'
    }

    @staticmethod
    def fetch_train_predictions(station_code: str, group: str) -> list[dict]:
        """
        Fetches train predictions for a given station and group.
        Includes retry logic for API connection issues to improve resilience.
        """
        retry_attempt = 0
        # Loop to handle retries instead of recursion, preventing potential stack overflow.
        while retry_attempt <= config['metro_api_retries']:
            try:
                # Use f-string for cleaner URL construction.
                api_url = f"{config['metro_api_url']}{station_code}"
                headers = {'api_key': config['metro_api_key']}

                # Fetch data from the network and parse as JSON.
                train_data = _network.fetch(api_url, headers=headers).json()

                print('Received response from WMATA api...')

                # Use a list comprehension for efficient filtering and mapping.
                # .get() is used to safely access dictionary keys, providing a default empty list
                # if 'Trains' key is missing, preventing KeyError.
                normalized_results = [
                    MetroApi._normalize_train_response(train)
                    for train in train_data.get('Trains', [])
                    if train.get('Group') == group # Safely check 'Group' key.
                ]
                return normalized_results
            except RuntimeError as e:
                # Catch specific network-related errors.
                print(f'Failed to connect to WMATA API. Error: {e}. Reattempting...')
                retry_attempt += 1
        
        # If all retries fail, raise a custom exception with a descriptive message.
        raise MetroApiOnFireException("Failed to fetch train predictions after multiple retries.")

    @staticmethod
    def _normalize_train_response(train: dict) -> dict:
        """
        Normalizes the raw train response from the API into a more consistent format.
        """
        # Use .get() to safely retrieve values, providing empty strings as defaults
        # to prevent KeyError if keys are missing from the API response.
        line = train.get('Line', '')
        destination = train.get('Destination', '')
        arrival = train.get('Min', '')

        # Check if the destination needs normalization using the predefined set.
        if destination in MetroApi._DESTINATION_NORMALIZATIONS:
            destination = 'No Psngr'

        return {
            'line_color': MetroApi._get_line_color(line),
            'destination': destination,
            'arrival': arrival
        }
    
    @staticmethod
    def _get_line_color(line: str) -> int:
        """
        Returns the hexadecimal color for a given Metro line code.
        Uses a dictionary lookup for efficiency and readability.
        """
        # Use .get() with a default value to handle lines not explicitly defined.
        return MetroApi._LINE_COLORS.get(line, MetroApi._DEFAULT_COLOR)
