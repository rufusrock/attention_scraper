from twocaptcha import TwoCaptcha
from selenium.webdriver.support.wait import WebDriverWait
from os import remove, getenv, system
import urllib.request
import csv
from random import choice
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from time import sleep
from selenium.webdriver.firefox.options import Options
import subprocess

BINARY_LOCATION = r"C://Program Files//Mozilla Firefox//firefox.exe"
FILEPATH_TO_KEY = r"C://Users//Rufus//OneDrive//Desktop//credentials.txt"

#get the api key from the text file in home directory
with open(FILEPATH_TO_KEY, "r", encoding="UTF-8") as f:
    API_KEY = f.readline()
    f.close()

TWOCAPTCHA_API_KEY = getenv("APIKEY_2CAPTCHA", API_KEY)

def captcha_solver(browser, KEY):
    try:
        captcha = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "form[action='/errors/validateCaptcha']")))
        if captcha:
            captcha_c = True
            solver = TwoCaptcha(KEY)
            try:
                print("[+] Solving Captcha")
                image_url = captcha[0].find_element(By.TAG_NAME, "img").get_attribute("src")
                # Download the captcha image and save it to a file
                urllib.request.urlretrieve(image_url, "captcha.jpg")
                result = solver.normal("captcha.jpg")
                print(result)
                remove("captcha.jpg")
                text_form = browser.find_element(By.CSS_SELECTOR, "input[id='captchacharacters']")
                text_form.clear()
                send_string = result["code"].upper()
                text_form.send_keys(send_string)
                text_form.send_keys(Keys.RETURN)
            except NoSuchElementException:
                print("[+] Captcha element not found")
                captcha = False
                return captcha
            except Exception as e:
                print(f"[-] Unexpected error: {e}")
        else:
            captcha_c = False
            return captcha_c
    except:
        print("[+] No Captcha Found")
        pass

def browser_setup():
    # Initializing a list with two Useragents 
    useragentlist = [ 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    ]

    options = Options()

    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)
    options.binary_location = BINARY_LOCATION

    user_agent = choice(useragentlist)

    options.set_preference("dom.push.enabled", False)
    options.set_preference("general.useragent.override", user_agent)
    options.set_preference("dom.webnotifications.enabled", False)

    browser = webdriver.Firefox(options=options)    

    browser.get("https://www.amazon.com")

    sleep(2)

    captcha = True
    captcha_count = 0

    while captcha:
        captcha = captcha_solver(browser, TWOCAPTCHA_API_KEY)
        if captcha:
            captcha_count += 1

    browser.refresh()

    return browser, user_agent, captcha_count

def network_info():
    network_info = subprocess.run(["mullvad","status"], capture_output=True, text=True).stdout
    location = network_info.split("in")[-1].strip() #much faster location detection than using geoip
    mullvad_node = network_info.split(" ")[2].strip() #could be relevant - might be able to see in data if there is a correlation between node and ad prevelance
    return location, mullvad_node

def network_random():
    country = "us"
    cities = ["atl", "chi", "dal", "den", "hou", "lax", "mia", "nyc", "phx", "qas","rag", "slc", "sjc", "uyk", "sea"]
    system("mullvad relay set location " + country + " " + choice(cities))
    sleep(15)

def search(browser, search_term):
    search_bar = WebDriverWait(browser,20).until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))) #finds the amazon search bar
    search_bar.clear() #clears the search bar
    search_bar.send_keys(search_term) #enters the search term
    search_bar.send_keys(Keys.RETURN) #presses the enter key

def get_queries(query_file="inputs//queries.csv"):
    queries = []
    with open(query_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            queries.append(row["query"])

    return queries