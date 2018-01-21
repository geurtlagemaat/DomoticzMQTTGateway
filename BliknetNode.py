import sqlite3

import os

__author__ = 'geurt'

import datetime
from twisted.internet import reactor
from twisted.internet import task

from bliknetlib import nodeControl
import logging
logger = logging.getLogger(__name__)
oNodeControl = None
devicesByTopic = {}

# MQTT Things
def onMQTTSubscribe(client, userdata, mid, granted_qos):
    logger.info("Subscribed: " + str(mid) + " " + str(granted_qos))

def onMQTTMessage(client, userdata, msg):
    logger.debug("ON MESSAGE:" + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if msg.topic in devicesByTopic:
        domoticzIdx = devicesByTopic[msg.topic]
        domoticzJson = ""
        if 'hum' in msg.topic:
            domoticzJson = '{ "idx" : %s, "nvalue" : "44", "svalue" : 0 }' % (domoticzIdx) # , str(msg.payload)
        else:
            domoticzJson = '{ "idx" : %s, "nvalue" : 0, "svalue" : "%s" }' % (domoticzIdx, str(msg.payload))

        oNodeControl.MQTTPublish(sTopic="domoticz/in", sValue=str(domoticzJson), iQOS=0, bRetain=False)

def subscribeTopics():
    myDBConn = None
    if oNodeControl.nodeProps.has_option('devices-db', 'dbtype') and\
            oNodeControl.nodeProps.get('devices-db', 'dbtype') == "sqllite":
        if not oNodeControl.nodeProps.has_option('devices-db', 'datafile'):
            logger.error("No SQLLite datafile location found in configfile")
        elif not os.path.isfile(oNodeControl.nodeProps.get('devices-db', 'datafile')):
            logger.error("SQLLite datafile location does not exists")
        else:
            myDBConn = sqlite3.connect(oNodeControl.nodeProps.get('devices-db', 'datafile'))
    elif oNodeControl.nodeProps.has_option('devices-db', 'dbtype') and\
            oNodeControl.nodeProps.get('devices-db', 'dbtype') == "mysql":
        import mysql.connector
        if not oNodeControl.nodeProps.has_option('devices-db', 'host') or\
                not oNodeControl.nodeProps.has_option('devices-db', 'port') or\
                not oNodeControl.nodeProps.has_option('devices-db', 'db') or\
                not oNodeControl.nodeProps.has_option('devices-db', 'user') or\
                not oNodeControl.nodeProps.has_option('devices-db', 'pw'):
            logger.error("MySQL config options incomplete (host, port, db, user and pw.")
        else:
            myDBConn = mysql.connector.connect(host=oNodeControl.nodeProps.get('devices-db', 'host'),\
                                               port=oNodeControl.nodeProps.getint('devices-db', 'port'),\
                                               db=oNodeControl.nodeProps.get('devices-db', 'db'),\
                                               user=oNodeControl.nodeProps.get('devices-db', 'user'),\
                                               passwd=oNodeControl.nodeProps.get('devices-db', 'pw'))
    if myDBConn is not None and oNodeControl.mqttClient is not None:
        oNodeControl.mqttClient.on_subscribe = onMQTTSubscribe

        myDBCursor = myDBConn.cursor()
        myDBRecordSet = myDBCursor.execute('SELECT id,naam,topic FROM devices')
        for myDevice in myDBRecordSet:
            oNodeControl.mqttClient.subscribe(myDevice[2], 0);
            devicesByTopic[myDevice[2]]=myDevice[0]
        oNodeControl.mqttClient.on_message = onMQTTMessage
        oNodeControl.mqttClient.loop_start()

if __name__ == '__main__':
    now = datetime.datetime.now()
    oNodeControl = nodeControl.nodeControl(r'settings/bliknetnode.conf')
    logger.info("BliknetNode: %s starting at: %s." % (oNodeControl.nodeID, now))

    subscribeTopics()

    if oNodeControl.nodeProps.has_option('watchdog', 'circusWatchDog'):
        if oNodeControl.nodeProps.getboolean('watchdog', 'circusWatchDog') == True:
            oNodeControl.circusNotifier.start()

    reactor.run()