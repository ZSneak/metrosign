# DC Metro Board
import time

from config import config
#from train_board import TrainBoard
from metro_api import MetroApi, MetroApiOnFireException
from bus_api import BusApi

STATION_CODE = config['metro_station_code']
TRAIN_GROUP = config['train_group']

STOP_ID = config['bus_stop_id']
DIRECTION_NUM = config['bus_direction_num']

def refresh():
	try:
		print(MetroApi.fetch_train_predictions(STATION_CODE, TRAIN_GROUP))
		print(BusApi.fetch_bus_predictions(STOP_ID, DIRECTION_NUM))
	except MetroApiOnFireException:
		print('WMATA Api is currently on fire. Trying again later ...')

refresh()