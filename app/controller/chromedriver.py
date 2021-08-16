import logging

import chromedriver_binary
from selenium import webdriver


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument("--disable-gpu")
    options.add_argument("--single-process")
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument("--disable-setuid-sandbox")

    logging.info("Starting chromedriver....")
    return webdriver.Chrome(executable_path=chromedriver_binary.chromedriver_filename, options=options)


driver = get_driver()
