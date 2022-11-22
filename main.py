from selenium import webdriver
import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import requests
import pandas as pd
import json
from dataclasses import dataclass, asdict
from datetime import datetime



chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

# driver = webdriver.Chrome('./chromedriver.exe')

tdy = datetime.today()
date = f'Nov {tdy.day}, 2022'

wwl_db = {'cluster': "WWL", 
'uri': 'https://data.mongodb-api.com/app/data-qvnrx/endpoint/data/v1' ,
'db': "wwl" ,
'key': "5d9sGO28viSiX1HnJlOLN6QMqPqxYz6NIKVUMvEU8wXvAS0CPHMMHs2jF0UHKSCF"}



## Updating database

def submit_data(collection, docs, credential):
    headers = {'Content-Type': 'application/json', 'Access-Control-Request-Headers': '*','api-key': credential['key']}
    insert_url = f"{credential['uri']}/action/insertMany"
    Payload = json.dumps({"collection": collection, "database": credential['db'], "dataSource": credential['cluster'], "documents": docs})
    response = requests.request("POST", insert_url, headers=headers, data=Payload)
    return response

def update_many(collection, condition, doc,  credential):
    headers = {'Content-Type': 'application/json', 'Access-Control-Request-Headers': '*','api-key': credential['key']}
    updateMany_url = f"{credential['uri']}/action/updateMany"
    Payload = json.dumps({"collection": collection, "database": credential['db'], "dataSource": credential['cluster'], "filter": condition, "update":{"$set": doc}})
    response = requests.request("POST", updateMany_url, headers=headers, data=Payload)
    return response

def update_one(collection, condition, doc,  credential):
    headers = {'Content-Type': 'application/json', 'Access-Control-Request-Headers': '*','api-key': credential['key']}
    updateOne_url = f"{credential['uri']}/action/updateOne"
    Payload = json.dumps({"collection": collection, "database": credential['db'], "dataSource": credential['cluster'], "filter": condition, "update":{"$set": doc}})
    response = requests.request("POST", updateOne_url, headers=headers, data=Payload)
    return response

def delete_many(collection, condition, credential):
    headers = {'Content-Type': 'application/json', 'Access-Control-Request-Headers': '*','api-key': credential['key']}
    deleteOne_url = f"{credential['uri']}/action/deleteMany"
    Payload = json.dumps({"collection": collection, "database": credential['db'],"dataSource": credential['cluster'], "filter": condition})
    response = requests.request("POST", deleteOne_url, headers=headers, data=Payload)
    return response

## Get data from database

def get_data_json(collection, credential):
    headers = {'Content-Type': 'application/json', 'Access-Control-Request-Headers': '*','api-key': credential['key']}
    findAll_url =  f"{credential['uri']}/action/find"
    Payload = json.dumps({"collection": collection, "database":credential['db'], "dataSource": credential['cluster'], "filter": {}, "limit":5000})
    response = requests.request("POST", findAll_url, headers=headers, data=Payload)
    response_json = response.json()['documents']
    return response_json

def get_data_df(collection, credential):
    headers = {'Content-Type': 'application/json', 'Access-Control-Request-Headers': '*','api-key': credential['key']}
    findAll_url =  f"{credential['uri']}/action/find"
    Payload = json.dumps({"collection": collection, "database":credential['db'], "dataSource": credential['cluster'], "filter": {}, "limit":5000})
    response = requests.request("POST", findAll_url, headers=headers, data=Payload)
    response_json = response.json()['documents']
    df = pd.read_json(json.dumps(response_json))
    return df


@dataclass
class Report:
    date: str
    access_point: str
    validation_type: str
    total: str
driver.get("https://eu.connectngo.com/login")
pw = 'LusailWW2022'
email = 'icerink@lww.com'

email_css = '#email'
pw_css ='#password'
sign_in_btn ='#app > main > div > div > div.d-flex.col-lg-4.align-items-center.bg-white.p-5 > div > div > form > div.d-flex.justify-content-between.align-items-center.m-0 > button'

def test_selector(selector, driver=driver):
    try:
        ele = driver.find_element(By.CSS_SELECTOR, selector)
        return ele
    except NoSuchElementException:
        return None

def login(user_name_selector, user_name, pw_selector, pw, btn_selector):
    un_ele = test_selector(user_name_selector)
    pw_ele = test_selector(pw_selector)
    btn_ele = test_selector(btn_selector)
    if (un_ele is not None) and (pw_ele is not None) and (btn_ele is not None):
        un_ele.clear()
        un_ele.send_keys(user_name)
        pw_ele.clear()
        pw_ele.send_keys(pw)
        btn_ele.click()
        return 'Logged In'
    else:
        return 'Failed to log in'

def select_report(i=3):
    reporting_tools_css = '#nova > div > div.min-h-screen.flex-none.pt-header.w-sidebar.bg-grad-sidebar.px-6.sidebar-hidden > h3.cursor-pointer.flex.items-center.font-normal.dim.text-white.mb-6.text-base.no-underline > span'
    option_css = f'#report > option:nth-child({i})'
    launch_css = '#button'
    reporting_tools = test_selector(reporting_tools_css)
    if reporting_tools is None:
        return None
    else:
        reporting_tools.click()
        time.sleep(3)
        report = test_selector(option_css)
        if report is None:
            return None
        else:
            report.click()
            launch = test_selector(launch_css)
            launch.click()

def get_table_data():
    date_css = '#dateRange > div > span'
    try:
        table = driver.find_element(By.TAG_NAME, 'table')
        rows = table.find_elements(By.TAG_NAME, 'tr')
    except NoSuchElementException:
        return None
    dt_rng = test_selector(date_css)
    table = []
    if dt_rng is None:
        return None
    else:
        for i in range(1, len(rows)):
            cols = rows[i].find_elements(By.TAG_NAME, 'td')
            table_rows = [dt_rng.text]
            for j in range(len(cols)):
                table_rows.append(cols[j].text)
            table.append(table_rows)
        return table

def scrape_aacess_point():

    data = get_table_data()
    if data is not None:
        db_data = []
        for rows in data:
            db_data.append(asdict(Report(date=rows[0], access_point=rows[1] , validation_type=rows[2] , total=rows[3])))
        delete_many(collection='wwl_tickets', condition={'date': db_data[0]['date']}, credential=wwl_db)
        submit_data(collection='wwl_tickets', docs=db_data, credential=wwl_db)


def scrapper_app():
    if login(user_name=email , user_name_selector=email_css , pw=pw , pw_selector=pw_css , btn_selector=sign_in_btn) == 'Logged In':
        print('here 0')
        select_report()
        print('here')
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)
        print('here 1')
        scrape_aacess_point()
        time.sleep(3)
        print('here')
        scrape_aacess_point()
        time.sleep(3)
        print('here 1')
        date_css = '#dateRange > div'
        date = test_selector(date_css)
        date.click()
        yesterday = 'body > div.daterangepicker.ltr.show-ranges.opensright > div.ranges > ul > li:nth-child(2)'
        yest = test_selector(yesterday)
        yest.click()
        submit_btn = '#main-container > form > div > button.btn.btn-primary'
        sub_btn = test_selector(submit_btn)
        sub_btn.click()
        time.sleep(3)
        scrape_aacess_point()
        print('here 2')


scrapper_app()