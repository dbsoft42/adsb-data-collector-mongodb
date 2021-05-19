import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from copy import deepcopy
from config import config

messages = {}

async def cleanup():
    '''
    Trims the messages dict that grows over time
    based on max age defined in config dict
    '''
    while True:
        now = datetime.now()
        cutoff_time = now - relativedelta(seconds=config['messages_max_age'])
        for key, value in messages.items():
            if value['time'] < cutoff_time:
                del messages[key]
        await asyncio.sleep(config['cleanup_run_interval'])

async def process_dataset(db, dataset):
    '''
    Processes the dump1090 JSON dataset, process each record/message into messages dict
    and call process_message(message) for each
    '''
    # Loop through each item of the aircraft list - we call them messages
    for message in dataset['aircraft']:
        aircraft = message['hex']
        if aircraft not in messages:
            # Add to the list as skeleton dict if not existing
            messages[aircraft] = {'status':{}, 'first_flight_message':False, 'processed':False}
        # Keep a copy of the old status for comparison
        old_status = deepcopy(messages[aircraft]['status'])
        # Fill/replace each attribute below
        for key, value in message.items():
            if key not in config['excluded_fields']:
                if type(value) == str:
                    value = value.strip()
                # Set flag if flight ID is received for the first time
                if (key == 'flight' and len(value) > 0
                    and (
                            'flight' not in messages[aircraft]['status']
                            or len(messages[aircraft]['status']['flight']) == 0
                        )
                    ):
                    messages[aircraft]['first_flight_message'] = True
                messages[message['hex']]['status'][key] = value
                # In future consider skipping and unsetting zero/empty values
        # Set the processed flag and time if status is changed from earlier
        if messages[aircraft]['status'] != old_status:
            messages[aircraft]['processed'] = False
            messages[aircraft]['time'] = datetime.fromtimestamp(dataset['now'])
        asyncio.create_task(process_message(db, messages[aircraft]))
        #await process_message(messages[aircraft])

async def process_message(db, message):
    '''Process given message into DB records as needed by calling required sub-functions'''
    if not message['processed']:
        status = deepcopy(message['status'])
        status['time'] = message['time']
        # Insert aircraft into DB if not already existing or update 'last seen'
        db_aircraft = await db.aircraft.find_one({'hex':status['hex']})
        if  db_aircraft == None:
            await db.aircraft.insert_one({  'hex':          status['hex'],
                                            'first seen':   status['time'],
                                            'last seen':    status['time']
                                        })
        else:
            await db.aircraft.update_one({'hex':status['hex']}, {'$set':{'last seen':status['time']}})
        # If flight available
        if (
            'flight' in status
            and len(status['flight']) > 0
            ):
            # Insert flight into DB if not erxisting or update 'last seen'
            db_flight = await db.flights.find_one({ 'flight':status['flight'], 'hex':status['hex']})
            if  db_flight == None:
                await db.flights.insert_one({   'flight':       status['flight'],
                                                'hex':          status['hex'],
                                                'first seen':   status['time'],
                                                'last seen':    status['time'],
                                                'seen on':      [datetime.combine(status['time'].date(), time.fromisoformat('00:00'))]
                                            })
            else:
                await db.flights.update_one({'flight':status['flight'], 'hex':status['hex']},
                                                {'$set':{
                                                        'last seen':status['time']
                                                        },
                                                '$addToSet':{
                                                        'seen on':datetime.combine(status['time'].date(), time.fromisoformat('00:00'))
                                                        }
                                                }
                                            )
        # Create status record
        await db.status.insert_one(status)
        # If flight ID received for the first time
        if message['first_flight_message']:
            # Retroactively update older status records (which don't have the flight ID yet)
            await db.status.update_many(  {
                                        'hex':status['hex'],
                                        'time':{'$gte':status['time']-relativedelta(seconds=config['orphan_status_update_max_age'])}
                                    },
                                    {'$set':{'flight':status['flight']}}
                                )
            messages[status['hex']]['first_flight_message'] = False
        messages[status['hex']]['processed'] = True
        # Debug timing messages
        print(f'Status for {status["hex"]} from {status["time"].time()} submitted at {datetime.now().time()}')

async def main():
    '''The driver function - will get the JSON from the URL and call process_dataset'''
    # Initialize DB connection
    mdb = AsyncIOMotorClient(config['db']['mongodb_conn_str'])
    db = mdb[config['db']['database_name']]

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=config['http_timeout'])) as http_session:
        asyncio.create_task(cleanup())
        while True:
            try:
                async with http_session.get(config['dump1090_url']) as response:
                    dataset = await response.json()
            except Exception as exc:
                print(f'EXCEPTION!')
                print(exc)
                await asyncio.sleep(config['source_poll_interval'])
                continue
            await process_dataset(db, dataset)
            await asyncio.sleep(config['source_poll_interval'])

if __name__ == '__main__':
    asyncio.run(main())
