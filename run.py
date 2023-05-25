from utilities import browser_setup, network_random, network_info, get_queries, search
from time import time, sleep
from datetime import date
from SERPscraper import scrape
import pandas as pd
from random import randint

result_folder = "results"
logs_folder = "logs"
inputs_folder = "inputs"

listing_types = ["Result", "Banner", "Video", "Carousel"]

search_terms = get_queries()

def main():
    network_random()

    browser, useragent, captcha_count = browser_setup()

    for search_term in search_terms:
        
        if randint(0,10) == 8:
            network_random()
            sleep(5)

        scrape_time_start = time()
        
        search(browser, search_term)

        sleep(10)

        df = scrape(browser)   

        df.to_csv("results//"+search_term.replace(" ","_")+".csv")

        scrape_time_end = time()
        total_scrape_time = scrape_time_end - scrape_time_start

        location, mullvad_node = network_info()

        log = {
            "Date": date.today().strftime("%m/%d/%Y"),
            "Time": time(),
            "Time2Scrape": total_scrape_time,
            "WindowSize": browser.get_window_size(),
            "MullvadLocation": location,
            "MullvadNode": mullvad_node,
            "UserAgent": useragent,
            "CaptchaCount": captcha_count
        }

        log_df = pd.DataFrame([log])

        log_df.to_csv("logs//"+search_term.replace(" ","_")+".csv")

if __name__ == "__main__":
    main()