# coding=utf-8
import asyncio
import time
from selenium import webdriver


def _get_driver(driver_location: str):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=driver_location, options=options)
    return driver


def get_url_screenshot(driver_location: str, url: str, filename, wait_load_time: int):
    driver: webdriver.Chrome = _get_driver(driver_location)
    driver.get(url)
    time.sleep(wait_load_time)

    S = lambda x: driver.execute_script('return document.body.parentNode.scroll' + x)
    driver.set_window_size(S('Width') + 1200, S('Height'))  # May need manual adjustment
    driver.find_element_by_tag_name('body').screenshot(filename=filename)

    driver.quit()
