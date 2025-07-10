# DC Metro Board
import time
import board

from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
from config import config
from train_board import TrainBoard
from metro_api import MetroApi, MetroApiOnFireException

STATION_CODE = config['metro_station_code']
TRAIN_GROUP = config['train_group']
REFRESH_INTERVAL = config['refresh_interval']

CURRENT_BOARD = 0
board_list = ['metro', 'bus']

def refresh_trains() -> list[dict]:
	try:
		return MetroApi.fetch_train_predictions(STATION_CODE, TRAIN_GROUP)
	except MetroApiOnFireException:
		print('WMATA Api is currently on fire. Trying again later ...')
		return None

train_board = TrainBoard(refresh_trains)

def board_switch():
	"""
	Switches the current board being displayed.
	Cycles through the available boards in `board_list`.
	"""
	CURRENT_BOARD = (CURRENT_BOARD + 1) % len(board_list)
	print(f'Switched to {board_list[CURRENT_BOARD]} board.')

def metrosign():
	"""
	Function to run the MetroSign application.
	This function is called when the script is run directly.
	"""
	print('MetroSign is running...')
	print(f'Fetching train predictions for station: {STATION_CODE}, group: {TRAIN_GROUP}')
	print(f'Refreshing every {REFRESH_INTERVAL} seconds.')
	while CURRENT_BOARD == 0:
		train_board.refresh()
		time.sleep(REFRESH_INTERVAL)

def bussign():
	"""
	Function to run the BusSign application.
	This function is called when the script is run directly.
	"""
	print('BusSign is running...')
	print(f'Fetching bus predictions for stop ID: {config["bus_stop_id"]}, direction: {config["bus_direction_num"]}')
	while CURRENT_BOARD == 1:
		# Placeholder for bus sign functionality
		print('Bus sign functionality not implemented yet.')
		time.sleep(REFRESH_INTERVAL)

global button_a_pin
button_a_pin = DigitalInOut(board.BUTTON_UP)
button_a_pin.switch_to_input(Pull.UP)
button_a = Debouncer(button_a_pin)

while True:
	button_a.update()
	if button_a.fell:
		board_switch()
		if CURRENT_BOARD == 0:
			metrosign()
		elif CURRENT_BOARD == 1:
			bussign()
	
