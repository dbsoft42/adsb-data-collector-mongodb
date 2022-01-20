from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from random import randrange
from time import sleep
from config import config

# Planespotters credentials
planespotters_username = 'Enter your username here'
planespotters_password = 'Your password here'
# Selenium Chrome webdriver path - include the file name
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

# Login
print("Logging in...")
driver.get('https://www.planespotters.net/user/login')
if driver.current_url != 'https://www.planespotters.net/':
    driver.find_element(By.NAME, 'username').send_keys(planespotters_username)
    driver.find_element(By.NAME, 'password').send_keys(planespotters_password)
    driver.find_element(By.CLASS_NAME, 'btn-block').click()
if driver.current_url != 'https://www.planespotters.net/':
    print("The login didn't work")
    exit()

while True:
    db_aircraft = db.aircraft.find_one({'registration': {'$exists': 0}, 'planespotters_checked': {'$exists': 0}})
    if db_aircraft != None:
        # Fetch details from web
        url = f"https://www.planespotters.net/hex/{db_aircraft['hex'].upper()}"
        print(f'Trying URL: {url}')
        driver.get(url)
        # We put in a random sleep after each request to avoid flooding
        # But instead of doing this at the end, we do it here to utilize the time for page loading
        sleep(randrange(1, max_request_spacing+1))
        #sleep(10)
        # Eliminate any residual data from the previous iteration
        aircraft_data = {}
        # Get the data elements from the page
        for e in driver.find_elements(By.CLASS_NAME, 'dt-td-nowrap'):
            try:
                if e.find_element(By.TAG_NAME, 'a').get_attribute('title') == 'View detailed Information about this airframe':
                    aircraft_data['registration'] = e.text
                    break
            except Exception:
                continue
        for e in driver.find_elements(By.CLASS_NAME, 'dt-td-min150'):
            try:
                if '/production-list/' in e.find_element(By.TAG_NAME, 'a').get_attribute('href'):
                    aircraft_data['model'] = e.text
                    break
            except Exception:
                continue
        for e in driver.find_elements(By.CLASS_NAME, 'dt-td-min150'):
            try:
                if '/airline/' in e.find_element(By.TAG_NAME, 'a').get_attribute('href'):
                    aircraft_data['operator'] = e.text
                    break
            except Exception:
                continue
        print(f"DATA: {aircraft_data['model'] if 'model' in aircraft_data else ''}    {aircraft_data['registration'] if 'registration' in aircraft_data else ''}  {aircraft_data['operator'] if 'operator' in aircraft_data else ''}")
        aircraft_data['planespotters_checked'] = True
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
