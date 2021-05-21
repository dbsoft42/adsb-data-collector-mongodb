adsb-data-collector-mongodb
======
An asynchronous Python script to continuously feed ADS-B data from dump1090 to a MongoDB database
-------
### What does this do?
This is mainly a single script that runs continuously and collects data from your dump1090 instance
and stores it in organized MongoDB documents.

* Works with *dump1090-fa* and should work with *dump1090-mutability* too, but it's not tested. Please drop me a line if it works for you.
* Written solely in *Python*.
* Uses Python asynchronous coroutines (through asyncio) to minimize delays from fetching and loading operations.

### Requirements
* Python 3.7+
* Python libraries
..* Motor: Asynchronous Python driver for MongoDB
..* Python-dateutil
..* dnspython

### Installation and setup
Download the files to the directory where you want to run it. I recommend having a dedicated directory/folder for this.
```
git clone https://github.com/dbsoft42/adsb-data-collector-mongodb.git
```
Install the required Python libraries.
```
pip3 install motor python-dateutil dnspython
```
Copy the *config_template.py* file to *config.py*.
```
cp config_template.py config.py
```
Edit *config.py* in your favourite text editor and change the following parameters.
* `mongodb_conn_str` - The MongoDB connection string. If you are using MongoDB Atlas, you can get this by logging in to Atlas, going to your cluster and clicking on the connect button. Get the one for Python.
* `database_name` - The name of the database in MongoDB that you will use to store the ADS-B data. I recommend having a dedicated database for this not using it for any other data.
* `dump1090_url` - This is the dump1090 URL which serves the *aircraft.json* file. Typically this will be in the form of `http://hostname/dump1090/data/aircraft.json` where *hostname* is the host name or IP address of the machine where *dump1090* is running. If you will be running this script on the same machine where dump1090 is running, you can leave it as *localhost*.

The file has more parameters for fine-tuning various operations. You can leave these as the defaults or tune them if you need. The file has comments describing in more detail what each parameter is used for.

Do a quick test run.
```
python3 adsb-data-collector.py
```
Let it run for a few seconds (or longer if you wish). If all goes well, you should not see any output on the terminal. Check your MongoDB database to see if new documents are being created in the **aircraft**, **flights** and **status** collections. If yes, you are good to go! Stop the running script with CTRL+C.

To run it for the long term, I suggest running in in the background with nohup as shown below, but you can choose your own method. The script will basically run indefinitely once started.
```
nohup adsb-data-collector.py &
```
