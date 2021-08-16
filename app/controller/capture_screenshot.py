# coding=utf-8
import logging
import time
from selenium import webdriver

from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, WebDriverException, \
    SessionNotCreatedException


def get_url_screenshot(driver: webdriver.Chrome, url: str, filename, wait_load_time: int, retries=1):
    try:
        driver.get(url)
        time.sleep(wait_load_time)

        S = lambda x: driver.execute_script('return document.body.parentNode.scroll' + x)
        driver.set_window_size(1240, S('Height'))  # May need manual adjustment
        driver.find_element_by_tag_name('body').screenshot(filename=filename)

    except (NoSuchWindowException, NoSuchElementException, WebDriverException, SessionNotCreatedException) as e:
        if retries >= 0:
            get_url_screenshot(driver, url, filename, wait_load_time, retries - 1)
        else:
            raise e


def close_driver(driver: webdriver.Chrome):
    if driver:
        driver.quit()
