from adafruit_bitmap_font import bitmap_font # type: ignore

config = {
	#########################
	# Network Configuration #
	#########################

	# WIFI Network SSID
	'wifi_ssid': '<Your 2.4ghz WiFi SSID>',

	# WIFI Password
	'wifi_password': '<Your WiFi Password>',

	#########################
	# Metro Configuration   #
	#########################

	# Metro Station Code
	'metro_station_code': 'D02',

	# Metro Train Group
	'train_group': '2',

	# API Key for WMATA
	# Note: You can get a free API key from https://developer.wmata.com/
    'metro_api_key': '<Your WMATA API Key>',
    
	#########################
	#   Bus Configuration   #
	#########################
	
	#Bus Stop IDs
    # Note: You can have more than one bus stop ID, which can be found on the WMATA website.
    'bus_stop_id': '1001344',
    
	"bus_direction_num": '0', # Direction number for the bus stop, usually 0 or 1
	#Color for Bus Lines
	"Bus Color": 0xADD8E6,
    

	#########################
	# Other Values You      #
	# Probably Shouldn't    #
	# Touch                 #
	#########################
	'metro_api_url': 'https://api.wmata.com/StationPrediction.svc/json/GetPrediction/',
	'metro_api_retries': 2,
	'refresh_interval': 5, # 5 seconds is a good middle ground for updates, as the processor takes its sweet ol time
    
	'bus_api_url': 'http://api.wmata.com/NextBusService.svc/json/jPredictions?',
	'bus_api_retries': 2,

	# Display Settings
	'matrix_width': 64,
	'num_trains': 3,
	'font': bitmap_font.load_font('lib/5x7.bdf'),

	'character_width': 5,
	'character_height': 7,
	'text_padding': 1,
	'text_color': 0xFF7500,

	'loading_destination_text': 'Loading',
	'loading_min_text': '---',
	'loading_line_color': 0xFF00FF, # Something something Purple Line joke

	'heading_text': 'LN DEST   MIN',
	'heading_color': 0xFF0000,

	'train_line_height': 6,
	'train_line_width': 2,

	'min_label_characters': 3,
	'destination_max_characters': 8,
}
