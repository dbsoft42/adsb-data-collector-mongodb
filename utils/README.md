# Utilities
This folder contains utility scripts for various purposes. Please see details on each below and how to use them.

## Planespotters.net scraper to populate aircraft details.
This script fetches aircraft details from planespotters.net and populates your **aircraft** documents with additional aircraft details like registration, model/type and operator(airline).

#### Requirements
* This script uses the Selenium webdriver to simulate the browser activity. 
  *  You need to have Chrome installed on the system running this script
  *  Download the [Chrome webdriver](https://chromedriver.chromium.org/downloads) for your platform and place in a folder of your choice.
  *  Install the Python Selenium library.
     ```
     pip3 install selenuim
     ```
* Depending on where you're running the script, you may need to install the PyMongo Python library. If you're running this at the same location where you run the main data-collector script, you already have the required library. If not, please insyall it as below.
```
pip3 install pymongo
```
* You need to register with planespotters.net and create an account if you don't already have one. *You need to be registered with planespotters.net as not logged-in users can only do a few queries.*

#### To use:
* Copy the script `scraper_planespotters.py` from the `utils` folder to the parent folder.
* Edit the script and enter your planespotters.net credentials in the marked section (lines 10 and 11).
* Edit the script and modify the **chrome_driver_path** directory path to the location where you placed the Chrome webdriver.
* Run the script as `python3 scraper_planespotters.py`. If you have a lot of aircraft to be updated, it may take a while to finish.

#### The following parameters can be tuned in the script.
* **max_request_spacing**: A random number of seconds between 1 and max_request_spacing is used to space each request to planespotters.net. This is to prevent flooding their system with too many requests at once and make the requests have a more natural flow.


## Opensky network scraper to populate aircraft details.
This script fetches aircraft details from opensky-network.org and populates your **aircraft** documents with additional aircraft details like registration, model/type and operator(airline).

#### Requirements
* This script uses the Selenium webdriver to simulate the browser activity. 
  *  You need to have Chrome installed on the system running this script
  *  Download the [Chrome webdriver](https://chromedriver.chromium.org/downloads) for your platform and place in a folder of your choice.
  *  Install the Python Selenium library.
     ```
     pip3 install selenuim
     ```
* Depending on where you're running the script, you may need to install the PyMongo Python library. If you're running this at the same location where you run the main data-collector script, you already have the required library. If not, please insyall it as below.
```
pip3 install pymongo
```

#### To use:
* Copy the script `scraper_opensky.py` from the `utils` folder to the parent folder.
* Edit the script and modify the **chrome_driver_path** directory path to the location where you placed the Chrome webdriver.
* Run the script as `python3 scraper_opensky.py`. If you have a lot of aircraft to be updated, it may take a while to finish.

