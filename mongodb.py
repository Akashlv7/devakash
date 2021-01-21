import pymongo

#


try:
    myclient = pymongo.MongoClient()
except pymongo.errors.ConnectionFailure as e:
    print(e)
    exit()

db = myclient["analytics"]
mycol = db["UE_details"]


data = {
            "streamID": "5e721c78555f246d770000d1",
            "serviceReference": "http://52.220.15.209/v2/smart_urls/5ea6c974dd7702199732a0ab?service_id=6&play_url=yes&protocol=hls&us=34ceac98f0dd2c9a60110b5ba1963ed4",
            "smartURL": "true",
            "broadcastFlag": "true",
            "contentProtocol": "mpd",
            "bitrate": "15000000",
            "resolution": "1280x720",
            "startTime": "1597662259",
            "duration": "1800",
            "videoEncoding": "hev1.1.6.L120.90",
            "audioEncoding": "mp4a.40.2",
            "contentTitle": "The Shawshank Redemption",
            "contentDescription": "The Shawshank Redemption is a 1994 American drama film written and directed by Frank Darabont, based on the 1982 Stephen King novella Rita Hayworth and Shawshank Redemption.",
            "language": "fr",
            "regionId": "AL - ED",
            "contentRating": "PG-13",
            "ratingDescription": "Parents strongly cautioned",
            "adMarkers": "true",
            "liveFlag": "false"
        }

mycol.insert_one(data)

#print(x.inserted_id)
print(myclient.list_database_names())
