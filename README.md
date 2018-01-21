# DomoticzMQTTGateway


This simple app build on top of Bliknet Lib is used to translates MQTT to JSON for Domoticz connection. It subscribe's all topic found in the devices table. Once a message is recieved it does a device lookup to find it's Domoticz id. Once found the payload is translated to JSON according to https://www.domoticz.com/wiki/Domoticz_API/JSON_URL and published to de domoticz/in topic.

Todo:
+ the other way arround: from Domoticz to Bliknet devices.
+ connect all devices and implement there JSON syntax.
