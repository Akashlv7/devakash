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
from config import MESSAGE_QUEUE_IP, UE_PULL_TOPIC

concurrent_workers = 50
message_queue = queue.Queue()
message_count = 0

city_centers = [["bengaluru", (12.9716, 77.5946)],
                ["chennai", (13.0827, 80.2707)], 
                ["delhi", (28.7041, 77.1025)], 
                ["mumbai", (19.0760, 72.8777)],
                ["kolkata", (22.5726, 88.3639)]] 

#returns a random cdl url with a suffix drawn from a probability distribution
def get_random_cdn_url(variation_count, distribution):
    return "cdn_url_" + str(np.random.choice(np.arange(1, variation_count), p = distribution))

def _get_random_coordinates():
    random_city_center = city_centers[randrange(len(city_centers))]
    return random_city_center[1][0], random_city_center[1][1]

def push_message(json_payload):
    publish.single(UE_PULL_TOPIC, json.dumps(json_payload), hostname=MESSAGE_QUEUE_IP)

def worker():
    global message_count
    while True:
        payload = message_queue.get()
        push_message(payload)
        message_queue.task_done()
        message_count = message_count + 1
        if message_count %100 == 0:
            print (message_count)

def emulate_user_tx_activity():
    for user in range(10000):

        loc_lat, loc_long = _get_random_coordinates()

        payload = {
            "location": {
                "type": "Point",
                "coordinates": [loc_long + random.uniform(-0.1, 0.1), loc_lat + random.uniform(-0.1, 0.1)]
                },
                "url" : get_random_cdn_url(7, [0.1, 0.05, 0.05, 0.2, 0.4, 0.2]),
                "user_id" : user,
                "event" : "start",
                "start_time" : int(time.time()),
                "timestamp" : int(time.time()),
                "medium" : "broadband"
        }

        
        message_queue.put(payload)

#starting message workers
for i in range(concurrent_workers):
    t = Thread(target = worker)
    t.daemon = True
    t.start()

emulate_user_tx_activity()
message_queue.join()
