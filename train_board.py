import displayio
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_matrixportal.matrix import Matrix

from config import config


class TrainBoard:
    """
    Manages the display of multiple train prediction entries on a matrix display.

    get_new_data is a function that is expected to return an array of dictionaries like this:

    [
        {
            'line_color': 0xFFFFFF,
            'destination': 'Dest Str',
            'arrival': '5'
        }
    ]
    """
    def __init__(self, get_new_data):
        self.get_new_data = get_new_data
        
        self.display = Matrix().display

        # A single parent group to hold all display elements.
        # Max size is num_trains (for Train groups) + 1 (for heading_label).
        self.parent_group = displayio.Group(max_size=config['num_trains'] + 1)

        # Initialize and add the heading label to the parent group.
        self.heading_label = Label(config['font'], max_glyphs=len(config['heading_text']), anchor_point=(0,0))
        self.heading_label.color = config['heading_color']
        self.heading_label.text = config['heading_text']
        self.parent_group.append(self.heading_label)

        # Create and store Train objects.
        self.trains = [Train(self.parent_group, i) for i in range(config['num_trains'])]

        # Show the main group on the display.
        self.display.show(self.parent_group)

    def refresh(self) -> bool:
        """
        Fetches new train data and updates the display.
        Hides trains if no data is available or if there's less data than display slots.
        """
        print('Refreshing train information...')
        train_data = self.get_new_data()
        
        if train_data is None:
            print('No data received. Clearing display.')
            train_data = [] # Treat no data as an empty list for consistent processing

        print('Reply received.' if train_data else 'No data received.')

        # Iterate through all available train display slots.
        for i in range(config['num_trains']):
            if i < len(train_data):
                # If there's data for this slot, update the train.
                train_info = train_data[i]
                self.trains[i].update(
                    train_info.get('line_color', config['loading_line_color']),
                    train_info.get('destination', config['loading_destination_text']),
                    train_info.get('arrival', config['loading_min_text']),
                    train_info.get('car', '-') # Default to '-' if 'car' is not provided
                )
            else:
                # If no data for this slot, hide the train.
                self.trains[i].hide()
        
        print('Successfully updated.' if train_data else 'Display cleared.')
        return train_data is not None # Return True if data was received, False otherwise.


class Train:
    """
    Represents a single train prediction entry on the display,
    including its line color, destination, and arrival time.
    """
    def __init__(self, parent_group: displayio.Group, index: int):
        # Calculate Y position for this train entry.
        y = int(config['character_height'] + config['text_padding']) * (index + 1)

        # Initialize the line color rectangle.
        self.line_rect = Rect(0, y, config['train_line_width'], config['train_line_height'], fill=config['loading_line_color'])
        
        # Initialize the destination label.
        self.destination_label = Label(config['font'], max_glyphs=config['destination_max_characters'], anchor_point=(0,0))
        self.destination_label.x = config['train_line_width'] + 2
        self.destination_label.y = y
        self.destination_label.color = config['text_color']
        self.destination_label.text = config['loading_destination_text'][:config['destination_max_characters']]

        # Initialize the minutes label (arrival time).
        self.min_label = Label(config['font'], max_glyphs=config['min_label_characters'], anchor_point=(0,0))
        self.min_label.x = config['matrix_width'] - (config['min_label_characters'] * config['character_width']) + 1
        self.min_label.y = y
        self.min_label.color = config['text_color']
        self.min_label.text = config['loading_min_text']

        # Group all elements for this train entry for easy management.
        self.group = displayio.Group(max_size=3) # Contains line_rect, destination_label, min_label
        self.group.append(self.line_rect)
        self.group.append(self.destination_label)
        self.group.append(self.min_label)

        # Add this train's group to the main parent group.
        parent_group.append(self.group)

    def show(self):
        """Makes the train entry visible."""
        self.group.hidden = False

    def hide(self):
        """Hides the train entry."""
        self.group.hidden = True

    def set_line_color(self, line_color: int):
        """Sets the fill color of the train line rectangle."""
        self.line_rect.fill = line_color

    def set_text_color(self, car: str):
        """
        Sets the text color based on the car number.
        If car is '-', it uses the default text color.
        Otherwise, it uses the car color from the config.
        """ 
        if (car == 8) or car == '8':
            self.min_label.color = config['text_color_8_car_train']
        else:
            self.min_label.color = config['text_color']

    def set_destination(self, destination: str):
        """Sets the destination text, truncating if too long."""
        self.destination_label.text = destination[:config['destination_max_characters']]

    def set_arrival_time(self, minutes: str):
        """
        Sets the arrival time, ensuring it's a string and right-justified.
        """
        # Convert to string and right-justify with spaces for consistent alignment.
        min_chars = int(config['min_label_characters'])
        min_str = str(minutes)
        if len(min_str) < min_chars:
            min_str = ' ' * (min_chars - len(min_str)) + min_str
        self.min_label.text = min_str

    def update(self, line_color: int, destination: str, minutes: str, car: str = '-'):
        """
        Updates all display elements for this train entry.
        """
        self.show() # Ensure the train is visible before updating.
        self.set_line_color(line_color)
        self.set_destination(destination)
        self.set_arrival_time(minutes)
        self.set_text_color(car)
