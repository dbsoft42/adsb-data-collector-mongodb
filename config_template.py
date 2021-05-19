# Make a copy of this file as config.py and update the required values below.
# The MongoDB connection details and the dump1090 URL are the ones you really need to look at.
# The rest can be left at the defaults to start with.

config = {} # Ignore this line

# MongoDB connection details (don't miss the username and password):
config['db'] = {
                'mongodb_conn_str':
                    'mongodb+srv://username:password@url.mongodb.net/myFirstDatabase?retryWrites=true&w=majority',
                'database_name': 'adsb'
                } #Include username and password in mongodb_conn_str

# Dump1090 URL for the aircraft.json file
config['dump1090_url'] = 'http://localhost/dump1090/data/aircraft.json'

# Once a flight ID is received for the first time,
# status records already inserted to the DB can be updated with the flight ID.
# Records only up to these many seconds will be updated.
config['orphan_status_update_max_age'] = 600 # seconds

# The source (dump1090 JSON URL) will be checked every:
# This affects how often the script checks dump1090 for updated status
# Increasing this interval is a way to reduce amount of data going into the DB.
config['source_poll_interval'] = 1 # seconds

# The timeout for the HTTP request to get the JSON file from dump1090
# If a response if not received within this period, the request will be aborted.
# This will not fail the script and it will try the next request after the source_poll_interval.
# If your dump1090 is running locally, a short timeout is fine.
# If your source_poll_interval is short, better to keep the timeout short.
config['http_timeout'] = 3 # seconds

# A dictionary is used to maintain a local of copy of the ADS-B status messages
# so that new messages can be distinhuished from those already processed.
# A cleanup function periodically trims this dictionary to keep it from growing too much.
# The following 2 options control how often the cleanup runs
config['cleanup_run_interval'] = 3600 # seconds
# and how old the messages can be before they are removed.
config['messages_max_age'] = 1800 # seconds

# The following fields are excluded from the status documents.
# This is primarily done to prevent new status documents from being created
# when there is no change in the actual data but just change in the
# age or cumulative fields. Add or remove fields here as per your preferences.
config['excluded_fields'] = ['messages', 'seen', 'seen_pos',]
