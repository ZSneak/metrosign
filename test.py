import json

with open('wifiandapikey.txt', 'r') as f:
	data = json.load(f)
	api_key = data['api_key']
	ssid = data['ssid']
	password = data['password']