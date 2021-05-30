adsb-data-collector-mongodb
======
## An asynchronous Python script to continuously feed ADS-B data from dump1090 to a MongoDB database

### What does this do?
This is mainly a single script that runs continuously and collects [ADS-B](https://en.wikipedia.org/wiki/Automatic_Dependent_Surveillance%E2%80%93Broadcast "What is ADS-B?") data from your dump1090 instance and stores it in organized MongoDB documents.

* Works with *[dump1090-fa](https://github.com/adsbxchange/dump1090-fa)* and should work with *[dump1090-mutability](https://github.com/adsbxchange/dump1090-mutability)* too, but it's not tested. Please drop me a line if it works for you.
* Written solely in *Python*.
* Uses Python asynchronous coroutines (through asyncio) to minimize delays from fetching and loading operations.
* Logging facility available
* Ready for Pushover notifications in case of errors/failure.

### Requirements
* A configured and running **dump1090** instance (see links above). This can be yours or a friend's but you should be able to access it from wherever you intend to run this script, if the script is not running on the same machine as dump1090.
* MongoDB - If you don't already have it, I recommend setting up a free cluster with [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
* Python 3.7+
* Python libraries
  * aiohttp
  * Motor: Asynchronous Python driver for MongoDB
  * PyMongo
  * Python-dateutil
  * dnspython

### Installation and setup
Download the files to the directory where you want to run it. I recommend having a dedicated directory/folder for this.
```
git clone https://github.com/dbsoft42/adsb-data-collector-mongodb.git
```
Install the required Python libraries.
```
pip3 install aiohttp motor pymongo python-dateutil dnspython
```
Copy the *config_template.py* file to *config.py*.
```
cp config_template.py config.py
```
Edit *config.py* in your favourite text editor and change the following parameters.
* `mongodb_conn_str` - The MongoDB connection string. If you are using MongoDB Atlas, you can get this by logging in to Atlas, going to your cluster and clicking on the connect button. Get the one for Python.
* `database_name` - The name of the database in MongoDB that you will use to store the ADS-B data. I recommend having a dedicated database for this not using it for any other data.
* `dump1090_url` - This is the dump1090 URL which serves the *aircraft.json* file. Typically this will be in the form of `http://hostname/dump1090/data/aircraft.json` where *hostname* is the host name or IP address of the machine where *dump1090* is running. If you will be running this script on the same machine where dump1090 is running, you can leave it as *localhost*.

The file has more parameters for fine-tuning various operations. You can leave these as the defaults or tune them if you like. The file has comments describing in more detail what each parameter is used for.

Do a quick test run.
```
python3 adsb-data-collector.py
```
Let it run for a few seconds (or longer if you wish). If all goes well, you should not see any output on the terminal. Check your MongoDB database to see if new documents are being created in the **aircraft**, **flights** and **status** collections. If yes, you are good to go! Stop the running script with CTRL+C.

To run it for the long term, I suggest running in in the background with nohup as shown below, but you can choose your own method. The script will basically run indefinitely once started.
```
nohup python3 adsb-data-collector.py &
```

### About Logging
The script supports logging to a file using the standard Python logging package. It is disabled by default and can be enabled from the *config.py* file. Please see the config file on how to enabled it and set the other parameters. The files are rotated such that a new file is created at midnight and the old file is renamed with the date stamp. You can configure how may days of old files you want to keep.

### About Pushover Notifications
The script also supports sending log messages as Pushover notifications. So you can set it up to notify you of errors or failures. The feature is disabled by default. To enabled it, please download the *LogPushoverHandler* from [here](https://github.com/dbsoft42/LogPushoverHandler) and place the *LogPushoverHandler.py* file in the same directory as *adsb-data-collector.py*. Then go to *config.py* and enable the feature. I recommend you keep the log level to *logging.ERROR* or *logging.CRITICAL* for the Pushover notifications.
