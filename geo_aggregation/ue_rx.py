import paho.mqtt.publish as publish
import json
from threading import Thread
from elasticsearch import Elasticsearch 
from random import randrange
import random
from pymongo import MongoClient
import queue
import time
import paho.mqtt.client as mqtt
import numpy as np
from config import MESSAGE_QUEUE_IP, UE_PULL_TOPIC, UE_PUSH_TOPIC

concurrent = 50
q = queue.Queue()
count = 0

def push_message(json_payload):
    publish.single(UE_PULL_TOPIC, json.dumps(json_payload), hostname=MESSAGE_QUEUE_IP)

def worker():
    global count
    while True:
        payload = q.get()
        push_message(payload)
        q.task_done()
        count = count + 1
        if count %100 == 0:
            print (count)

for i in range(concurrent):
    t = Thread(target = worker)
    t.daemon = True
    t.start()



#Back channel
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(UE_PUSH_TOPIC)


def on_message(client, userdata, msg):
    topic = msg.topic
    response = (msg.payload).decode("UTF-8")
    print(response)

    process_response(json.loads(response))

def process_response(resp):
    user_id = resp["user_id"]
    cdn_url = resp["cdn_url"]
    #frequency = resp["frequency"]

    payload = {
                "user_id" : user_id,
                "cdn_url" : cdn_url,
                "event" : "start",
                "start_time" : int(time.time()),
                "timestamp" : int(time.time()),
                "medium" : "broadcast"
        }

        
    q.put(payload)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MESSAGE_QUEUE_IP, 1883, 60)
client.loop_forever()