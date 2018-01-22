# DomoticzMQTTGateway


This simple app build on top of Bliknet Lib is used to translates MQTT messages to Domoticz JSON format and Domoticz topic. It subscribe's all topics found in the devices table. Once a message is recieved it does a device lookup to find it's Domoticz device id. Once found the payload is translated to JSON according to https://www.domoticz.com/wiki/Domoticz_API/JSON_URL%27s and published to de domoticz/in topic.

Todo:
+ expand devices table to support different JSON message formats;
+ the other way arround: from Domoticz to Bliknet devices
+ connect all devices and implement there JSON syntax.
