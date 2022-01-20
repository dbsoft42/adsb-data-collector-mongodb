'''
This script helps you in cleaning up the "status" collection if the growing size
is threatening to exceed your MongoDB quota. It works on a very simple principle.
It removes the documents from the status collection whose times have the "second"
value within the range specified below. For example, if you set it to (20,30),
all status documents that have a time value with the second part from 20 to 30
will be deleted.
To run, copy this script to the parent directory/folder (same place where config.py
is located) and execute with python3.
'''
# Documents whose timestamps have seconds falling within this range (inclusive of bounds)
# are to be deleted
sec_range = (20, 50)

from pymongo import MongoClient
from config import config

batch_size = 50000

mdb = MongoClient(config['db']['mongodb_conn_str'])
db = mdb[config['db']['database_name']]

print('Please wait, this may take some time...')
all_docs = db.status.find(
                            {'time': {'$ne': 'null'}},
                            projection={'time': 1, '_id': 1},
                            batch_size=batch_size
                        )
docs_to_del = []
for doc in all_docs:
    s = doc['time'].second
    if s >= sec_range[0] and s <= sec_range[1]:
        docs_to_del.append(doc['_id'])

print(f'Documents to be deleted: {len(docs_to_del)}')
proceed = ''
while proceed not in ['Y', 'N']:
    proceed = input('Proceed with deletion (Y/N)?').upper()
if proceed == 'Y':
    res = db.status.delete_many({'_id': {'$in': docs_to_del}})
    print(f'Deleted documents: {res.deleted_count}')
