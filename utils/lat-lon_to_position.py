'''
The lat/lon fields in the status documents were recently changed to the MongoDB
preferred GeoJSON format that lets you visualize positions on a map more easily.
This script help you convert your older data to the new format.
To run, just copy it to the parent directory/folder (same place where config.py
is located) and execute with python3. Depending on the volume of data that is to
be converted, this may run a long time and may need to be several times.
I could not find a more efficient way to do this that would work easily for
everybody. If you have ideas, please let me know.
Of course, it's not absolutely necessary to do the conversion if the homogeneity
of older and newer data isn't important to you.
'''

from pymongo import MongoClient
from datetime import datetime
from config import config

batch_size = 50000

mdb = MongoClient(config['db']['mongodb_conn_str'])
db = mdb[config['db']['database_name']]

print(f"Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
all_docs = db.status.find(
                            {'lat': {'$exists': 'true'}, 'lon': {'$exists': 'true'}},
                            projection={'time': 1, 'lat': 1, 'lon': 1, '_id': 1},
                            batch_size=batch_size
                        )
for doc in all_docs:
    #print(doc)
    res = db.status.update_one(
                            {'_id': doc['_id']},
                            {'$set': {
                                        'position': {
                                                        'type': 'Point',
                                                        'coordinates': [
                                                                            doc['lon'],
                                                                            doc['lat']
                                                                        ]
                                                    }
                                        },
                            '$unset': {
                                        'lat': '',
                                        'lon': ''
                                    }
                            }
                        )
    if res.modified_count > 0:
        print(f"Document updated: {doc['_id']} from {doc['time']}")

print(f"Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
