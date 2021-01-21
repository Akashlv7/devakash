"""
Pulls user activity data from message queue and stores in a database

"""

import paho.mqtt.client as mqtt
import json
from pymongo import MongoClient
import traceback
from haversine import haversine, Unit, haversine_vector
import numpy as np
import timeit
from elasticsearch import Elasticsearch
from config import MESSAGE_QUEUE_IP, RESET_DB_FLAG, UE_PULL_TOPIC, UE_PUSH_TOPIC

message_count = 0

#DB initilization
mongoDBClient = MongoClient()
db = mongoDBClient.analytics
activity_col = db.live_user_activity

if RESET_DB_FLAG:
    activity_col.delete_many({})

  
def process_message(message):
    #can implement when an event occur not implemented as of now
    event = message["event"]
    medium = message["medium"]
    if medium == "broadband":
        activity_col.insert_one(message)
    else:
        activity_col.update_one({"user_id": message["user_id"]}, {"$set": { "medium": "broadcast"}})
        print (message["user_id"], "broadcast")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(UE_PULL_TOPIC)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global message_count
    message_count += 1
    if message_count % 100 == 0: 
        print (message_count)
    try:
        topic = msg.topic
        payload = (msg.payload).decode("UTF-8")

        json_data = json.loads(payload)
    
        process_message(json_data)    
    except:
        print (traceback.format_exc())

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MESSAGE_QUEUE_IP, 1883, 60)
client.loop_forever()