from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from random import randrange
from time import sleep
from config import config

## Selenium Chrome webdriver path - include the file name
chrome_driver_path = r'C:\chromedriver_win32\chromedriver.exe'
max_request_spacing = 5 # secs

# Initialize DB connection
mdb = MongoClient(config['db']['mongodb_conn_str'])
db = mdb[config['db']['database_name']]

#Initialize Selenium Chrome webdriver
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--log-level=3')
driver = webdriver.Chrome(
                                executable_path=chrome_driver_path,
                                options=chrome_options
                            )

while True:
    db_aircraft = db.aircraft.find_one({'registration': {'$exists': 0}, 'opensky_checked': {'$exists': 0}})
    if db_aircraft != None:
        # Fetch details from web
        url = f"https://opensky-network.org/aircraft-profile?icao24={db_aircraft['hex']}"
        print(f'Trying URL: {url}')
        driver.get(url)
        # We put in a random sleep after each request to avoid flooding
        # But instead of doing this at the end, we do it here to utilize the time for page loading
        sleep(randrange(1, max_request_spacing+1))
        #sleep(10)
        # Get the data elements from the page
        aircraft_data = {}
        if driver.find_element_by_id('ap_typecode').text != '':
            aircraft_data['type'] = driver.find_element_by_id('ap_typecode').text
        if driver.find_element_by_id('ap_registration').text != '':
            aircraft_data['registration'] = driver.find_element_by_id('ap_registration').text
        if driver.find_element_by_id('ap_model').text != '':
            aircraft_data['model'] = driver.find_element_by_id('ap_model').text
        if driver.find_element_by_id('ap_operator').text != '':
            aircraft_data['operator'] = driver.find_element_by_id('ap_operator').text
        ac_manufacturer = driver.find_element_by_id('ap_manufacturerName').text
        ac_owner = driver.find_element_by_id('ap_owner').text
        # Combine manufacturer and model if model does not have the manufacturer name
        if ac_manufacturer != '' and 'model' in aircraft_data and ac_manufacturer.lower() not in aircraft_data['model'].lower():
            aircraft_data['model'] = ac_manufacturer + ' ' + aircraft_data['model']
        # Combine owner and operator
        if 'operator' in aircraft_data and aircraft_data['operator'] == 'N/A':
            aircraft_data['operator'] = ac_owner
        print(f"DATA: {aircraft_data['type'] if 'type' in aircraft_data else ''}  {aircraft_data['model'] if 'model' in aircraft_data else ''}    {aircraft_data['registration'] if 'registration' in aircraft_data else ''}  {aircraft_data['operator'] if 'operator' in aircraft_data else ''}")
        aircraft_data['opensky_checked'] = True
        # Update record
        res = db.aircraft.update_one(
                                {'hex': db_aircraft['hex']},
                                {'$set': aircraft_data}
        )
        if res.modified_count < 1:
            print("Something went wrong while updating the record. Terminating.")
            driver.close()
            exit()
    else:
        break

driver.close()
