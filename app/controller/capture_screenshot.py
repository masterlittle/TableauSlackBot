# coding=utf-8
import asyncio
import logging
import time
from selenium import webdriver
import chromedriver_binary


def _get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument("--disable-gpu")
    options.add_argument("--single-process")
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument("--disable-setuid-sandbox")

    logging.info(chromedriver_binary.chromedriver_filename)
    driver = webdriver.Chrome(executable_path=chromedriver_binary.chromedriver_filename, options=options)
    return driver


def get_url_screenshot(url: str, filename, wait_load_time: int):
    driver: webdriver.Chrome = _get_driver()
    driver.get(url)
    time.sleep(wait_load_time)

    S = lambda x: driver.execute_script('return document.body.parentNode.scroll' + x)
    driver.set_window_size(2560, S('Height'))  # May need manual adjustment
    driver.find_element_by_tag_name('body').screenshot(filename=filename)

    driver.quit()

