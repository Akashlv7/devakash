"""
Pulls data from database periodically, and calculates cdn_url access histogram.
"""

from elasticsearch import Elasticsearch 
import time
from pymongo import MongoClient
import paho.mqtt.publish as publish
import json
import queue
from threading import Thread
from config import MESSAGE_QUEUE_IP, OFFLOAD_THRESHOLD, UE_PULL_TOPIC, UE_PUSH_TOPIC

mongoDBClient = MongoClient()
analytics_DB = mongoDBClient.analytics
ua_col = analytics_DB.live_user_activity

concurrent_workers = 50
q = queue.Queue()
count = 0

#name, lat, long, radius
brh_loc = [["bengaluru", (12.9716, 77.5946), 0.02], ["delhi", (28.7041, 77.1025),0.02]] 

broadcast_list = []
user_state = {}

def worker():
    global count
    while True:
        payload = q.get()
        notify_UE(payload)
        q.task_done()


def get_live_users_data_within_radius(latitude, longitude, range):
    result = ua_col.find({"medium":"broadband", "location": {"$geoWithin": { "$centerSphere": [ [ longitude, latitude ], 0.02 ]}}})
    return result

def notify_UE(json_payload):
    publish.single(UE_PUSH_TOPIC, json.dumps(json_payload), hostname=MESSAGE_QUEUE_IP)
    print ("notify UE", json.dumps(json_payload))

def get_above_thrershold_urls(data):
    url_hit = {}
    above_threshold_urls = []
    for row in data:
        url = row["url"]
        if not url in url_hit:
            url_hit[url] = 0
        url_hit[url] = url_hit[url] + 1

        if url_hit[url] >= OFFLOAD_THRESHOLD:
            return url

def detect_threshold():
    global broadcast_list
    peak_urls = {}
    for brh_center in brh_loc:
        live_users_data = get_live_users_data_within_radius(brh_center[1][0], brh_center[1][1], 200)
        peak_content  = get_above_thrershold_urls(live_users_data)
        if peak_content is not None:
            if peak_content not in broadcast_list:
                broadcast_list.append(peak_content)

def get_users_watching_url_on_broadband(url):  
    return ua_col.find({"url":url, "medium": "broadband"})

def process_broadcast_list():
    global broadcast_list
    for url in broadcast_list[:3]: #hard limit on broadcast channel
        # call RM to schedule stream immediately
        offload_content(url)

def offload_content(url):
    users = get_users_watching_url_on_broadband(url)
    for user in users:
        q.put({"user_id" : user["user_id"], "cdn_url": user["url"]})
        ua_col.update_one({"user_id": user["user_id"]}, {"$set": { "medium": "transit"}})



for i in range(concurrent_workers):
    t = Thread(target = worker)
    t.daemon = True
    t.start()


while True:
    time.sleep(1)
    detect_threshold()
    process_broadcast_list()