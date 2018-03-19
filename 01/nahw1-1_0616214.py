import requests
import argparse
import simplejson as json
import sys
import getopt
import os
import base64
import pandas
import getpass
from bs4 import BeautifulSoup
from prettytable import from_csv
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if __name__ == "__main__":
    print("Web crawler for NCTU class schedule")
    parsor = argparse.ArgumentParser()
    parsor.add_argument("username", help="username of NCTU portal")
    args = parsor.parse_args()
    name = args.username
    password = getpass.getpass("Password for " + name + ": ")
    driver = webdriver.Chrome()
    driver.get("https://portal.nctu.edu.tw/portal/login.php")
    parsed = False
    while not parsed:
        img = driver.find_element(By.ID, "captcha")
        cookies_list = driver.get_cookies()
        # print(cookies_list)
        header = {
            'Cookie': '',
            'Referer': 'https://portal.nctu.edu.tw/portal/login.php',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }

        cookies_dict = {}
        for cookie in cookies_list:
            cookies_dict[cookie['name']] = cookie['value']
        cookies_string = ""
        cookies_string = \
            'PHPSESSID=' + cookies_dict['PHPSESSID']
        header['Cookie'] = cookies_string
        # print(cookies_string)
        with open(r"/tmp/getcaptcha.jpg", "wb") as f:
            res = requests.get(
                'https://portal.nctu.edu.tw/captcha/pitctest/pic.php?t=1512570353936',
                headers=header)  # paint
            f.write(res.content)
        print(header)
        files = {"file": open("/tmp/getcaptcha.jpg", "rb")}
        res = requests.post("https://hare1039.nctu.me/cracknctu", files=files)
        os.remove("/tmp/getcaptcha.jpg")
        if res.status_code == requests.codes.ok and res.text != "ERROR":
            print(res.text)
            cap = driver.find_element(By.ID, "seccode")
            cap.send_keys(res.text)
            parsed = True
        else:
            print("refresh!")
            reload_but = driver.find_element(By.ID, "seccode_refresh")
            ActionChains(driver).click(reload_but).perform()

    print("Get it!")

    namefield = driver.find_element(By.ID, "username")
    namefield.send_keys(name)
    passfield = driver.find_element(By.ID, "password")
    passfield.send_keys(password)
    passfield.submit()

    driver.get("https://portal.nctu.edu.tw/portal/relay.php?D=cos")
    try:
        element_present = EC.presence_of_element_located((By.ID, "submit"))
        WebDriverWait(driver, 10).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
        assert False, "Timed out waiting for page to load"
    driver.find_element(By.ID, "submit").submit()

    driver.find_element(By.ID, "idfrmSetPreceptor").submit()

    driver.switch_to.frame("frmMenu")
    driver.execute_script("checkDiv('CrsTakenStateSearch');")
    driver.find_element(By.XPATH, "//a[@href='adSchedule.asp']").click()

    driver.switch_to.default_content()
    driver.switch_to.frame("frmMain")

    try:
        element_present = EC.presence_of_element_located(
            (By.XPATH, "/html/body/center/p/table[2]"))
        WebDriverWait(driver, 10).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
        assert False, "Timed out waiting for page to load"

    html_table = driver.find_element(By.XPATH, "/html/body/center/p/table[2]")
    table = pandas.read_html(html_table.get_attribute("outerHTML"))
    table[0].to_csv("/tmp/getclasses.csv")
    fp = open("/tmp/getclasses.csv", "r")
    ptable = from_csv(fp)
    fp.close()
    os.remove("/tmp/getclasses.csv")
    print(ptable)
    driver.quit()
