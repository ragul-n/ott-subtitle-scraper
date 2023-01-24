import time
import re
import pandas as pd
import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import  Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def init_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.notifications": 2
    })                  

    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")
    chrome_options.add_argument("user-data-dir=C:/Users/natar/AppData/Local\Google/Chrome/User Data/Profile 1") 


    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

    driver = webdriver.Chrome("C:\DRIVERS\chromedriver.exe",options=chrome_options,desired_capabilities=capabilities)
    driver.implicitly_wait(10)

    return driver


def is_subtitle(soup):
    try: 
        if 'begin' in soup.find_all("p")[0].attrs.keys():
            return True
    except:
        return False

def get_data(driver, url):
    title=driver.find_element_by_class_name('previewModal--player-titleTreatment-logo').get_attribute("title")
    year=driver.find_element_by_class_name('year').text
    duration=driver.find_element_by_class_name('duration').text

    return title, year, duration


def get_subtitle_file(driver):
    xhr_files = [entry for entry in driver.get_log('performance') ]# if 'fetch' in entry.get('message')

    for xhr_file in xhr_files:
        params=json.loads(xhr_file.get('message'))['message']['params']
        if 'request' in params.keys():
            if "url" in params["request"].keys():
                url=json.loads(xhr_file.get('message'))['message']['params']['request']['url']
            else:
                continue
            if '/?o=' in url:
                sub_url=json.loads(xhr_file.get('message'))['message']['params']['request']['url']
                
                response=requests.get(sub_url)

                soup = BeautifulSoup(response.text, "html.parser")
                if is_subtitle(soup):
                    return response.text
                

def get_subtitle_data(driver,url):
    driver.execute_script(f'''window.open("{url}","_blank");''')

    driver.switch_to.window(driver.window_handles[-1])
    
    title,duration, year=get_data(driver, url)

    driver.get(url.replace("title", "watch"))

    sub=None
    while not sub:
        time.sleep(3)
        sub=get_subtitle_file(driver)

    driver.close()
    driver.switch_to.window(driver.window_handles[-1])

    return title, duration, year,sub
    

if __name__=="__main__":
    url='https://www.netflix.com/title/81128584'
    
    driver= init_driver()

    title, duration, year,sub=get_subtitle_data(driver,url)

    driver.quit()

    print(title,duration,year)
    with open(title+".xml","w",  encoding="utf-8") as f:
        f.write(sub)
