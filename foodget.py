import os
import time
import json
import logging
from sys import stdout
from datetime import datetime
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

cookie_file = 'epic-proxies/sg'
bin_dir = 'epic-bin/epic.exe'
base_url = 'https://food.grab.com'
home_url = '/sg/en'
add = 'Little India Arcade - 48 Serangoon Rd, Singapore, 217959'
pagination = 2
debug_mode = False


def check_create_dir(dirname):
    '''
    Checks if directory exists and if it doesn't creates a new directory
    :param dirname: Path to directory
    '''
    if not os.path.exists(dirname):
        if '/' in dirname:
            os.makedirs(dirname)
        else:
            os.mkdir(dirname)


def xpath_soup(element):
    """
       Generate xpath from BeautifulSoup4 element.
       :param element: BeautifulSoup4 element.
       :type element: bs4.element.Tag or bs4.element.NavigableString
       :return: xpath as string
       """
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
            )
        )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)


if __name__ == '__main__':
    print('Foodget')

    rootLogger = logging.getLogger()
    consoleHandler = logging.StreamHandler(stdout)
    check_create_dir('logs')
    log_timestamp = datetime.now()
    fileHandler = logging.FileHandler(
        os.path.join('logs', 'FoodGet{0}.log'.format(log_timestamp.strftime('%m-%d-%y-%H-%M-%S'))), 'w',
        'utf-8')
    fileHandler.setFormatter(logging.Formatter('%(asctime)s:-[%(name)s] - %(levelname)s - %(message)s'))
    rootLogger.addHandler(consoleHandler)
    rootLogger.addHandler(fileHandler)
    rootLogger.setLevel(logging.DEBUG)
    logging.getLogger('seleniumwire.handler').setLevel(logging.ERROR)
    logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.ERROR)
    logging.getLogger('seleniumwire.server').setLevel(logging.ERROR)
    logging.getLogger('hpack.hpack').setLevel(logging.ERROR)
    logging.getLogger('hpack.table').setLevel(logging.ERROR)
    logging.getLogger('seleniumwire.storage').setLevel(logging.ERROR)
    if debug_mode:
        consoleHandler.setLevel(logging.DEBUG)
    else:
        consoleHandler.setLevel(logging.INFO)
    fileHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(logging.Formatter('[%(name)s] - %(levelname)s - %(message)s'))

    rootLogger.info('Initiating browser')
    options = uc.ChromeOptions()
    options.user_data_dir = cookie_file
    options.binary_location = bin_dir
    options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disk-cache-size=1073741824')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--dns-prefetch-disable')
    options.add_argument('--hide-scrollbars')
    options.add_argument("--disable-infobars")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument('--log-level=0')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--start-maximized")
    driver = uc.Chrome(headless=False, options=options, version_main=91)
    try:
        rootLogger.info('Connecting to home url')
        driver.get(base_url + home_url)
        rootLogger.info('Entering address')
        base_soup = BeautifulSoup(driver.page_source, 'html.parser')
        address_box = base_soup.find('input', {'class': 'ant-input'})
        address_box_sel = driver.find_element(By.XPATH, xpath_soup(address_box))
        text_value = address_box['value']
        if len(text_value) > 0:
            rootLogger.debug('Text already in box. Removing')
            for i in range(len(text_value)):
                address_box_sel.send_keys(Keys.BACKSPACE)
        time.sleep(1)
        address_box_sel.send_keys(add)
        address_box_sel.send_keys(Keys.ENTER)
        rootLogger.info('Clicking submit')
        submit_button = driver\
            .find_element(By.XPATH, xpath_soup(base_soup
                                               .find('button', {'class': 'ant-btn submitBtn___2roqB ant-btn-primary'})))\
            .click()
        time.sleep(10)
        rootLogger.debug('Starting routine')
        action = ActionChains(driver)
        for page in range(pagination):
            # print('loop get')
            time.sleep(3)
            listing_cnt = 0
            results_soup = BeautifulSoup(driver.page_source, 'html.parser')
            pg_error = results_soup.find('h6', {'class': 'ErrorMessageWidget-title___3i3Uu'})
            if pg_error is not None:
                rootLogger.info('End of results found. Ending process')
                break
            if pagination > 1:
                rootLogger.info('Increasing pagination')
                results_soup = BeautifulSoup(driver.page_source, 'html.parser')
                try:
                    load_more_button = driver.find_element(By.XPATH, xpath_soup(
                        results_soup.find('button', {'class': 'ant-btn ant-btn-block'})))
                    action.move_to_element(load_more_button).perform()
                    time.sleep(3)
                    action.click().perform()
                except Exception as exc:
                    rootLogger.error('Could not find load more. Exiting')
                    rootLogger.debug('Details: {}'.format(str(exc)))
                    break
    except Exception as exc:
        rootLogger.error('Error (outer)')
        rootLogger.error('Details: {}'.format(str(exc)))
    driver.refresh()
    time.sleep(3)
    res_soup = BeautifulSoup(driver.page_source, 'html.parser')
    s = res_soup.find('script', type='application/json')
    try:
        for key, value in json.loads(s.text)['props']['initialReduxState']['pageRestaurantsV2']['entities'][
         'restaurantList'].items():
            print()
            res_id = key
            rootLogger.info('Restaurant ID: {}'.format(res_id))
            rootLogger.info('Restaurant: {}'.format(value['name']))
            rootLogger.info('Latitude: {}'.format(value['latitude']))
            rootLogger.info('Longitude: {}'.format(value['longitude']))
    except Exception as exc:
        rootLogger.error('Error with reporting values')
        rootLogger.error('Details: {}'.format(str(exc)))
    rootLogger.info('Closing browser')
    rootLogger.info('Goodbye')
    driver.close()
    driver.quit()