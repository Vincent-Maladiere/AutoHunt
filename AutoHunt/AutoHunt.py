#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common import action_chains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from functools import wraps
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from format import *
from config import *
from spreadsheet import *

import time

class Results(object):
    """
    Results are the object representation of the scraped item, before putting them inside a pandas.DataFrame and then
    inside a gspread.spreadsheet.worksheet
    """
    def __init__(self, url, source, kwargs):
        self.url = [url]
        self.source = source
        # allow each Results object to be easily turned into a pandas DataFrame afterward
        for k, v in list(kwargs.items()):
            kwargs[k] = [v]
        self.info = kwargs

    def clean_fields(self):
        """
        Fills every missing field from class results with an empty string, so all Results object have the same number of
        keys in their info attribute
        """
        all_fields_list = [elem for elem in vars(results) if not elem.startswith('__')]
        for field in all_fields_list:
            if field not in list(self.info.keys()):
                self.info[field] = NOT_FOUND_ITEM
        return self

class Scraper(object):
    """
    The main class, allow to set query parameters and run scraping according to these parameters
    """
    result_list = []

    def __init__(self, name, driver, search_keys):
        """
        :param name: Name of the target, chosen among targets class
        :param driver: Running webdriver to use
        :param search_keys: Parameters to use for the search
        """
        self.name = name
        self.driver = driver
        self.wait = WebDriverWait(self.driver, EC_MAX_TO_WAIT)
        self.search_keys = search_keys
        # structure of the parameter page
        self.search_fields = SEARCH_FIELDS[name]
        # structure of the scraped page
        self.scrape_fields = SCRAPE_FIELDS[name]
        # first link to browse by the driver to set parameters
        self.link = SEARCH_LINKS[name]
        # button to click on in order to display next page of result
        self.next_button = NEXT_BUTTON_FIELDS[name]
        # item to wait for during result page loading
        self.item_to_wait_for = ITEM_TO_WAIT_FOR[name]
        # field to wait for during item loading from the result page
        self.field_to_wait_for = FIELD_TO_WAIT_FOR[name]
        # structure of the result page to collect the links of all items into a list
        self.url_generator = ITEMS_URL_GENERATOR[name]
        # use to assess that the item has been correctly filled
        self.key_filler_checker = KEY_FILLER_CHECKER[name]
        # number of collected items
        self.scraped_count = 0
        logprint(name)

    def _safe_action(func):
        """
        This decorator is used to interact safely with the element of the webpage, so if an error occures, the program
        won't crash.
        It is called twice : to fill search fields with _parameter_executer and then to scrape displayed elements via
        _item_executer.
        In the first case, no value is returned. The driver use given paths and execute the actions
        In the second case, the value of a targeted element is returned, and if this doesn't exist, an empty string is
        returned instead : ''. Unlike _parameter_executer, _item_executer only execute given lambda function, and
        doesn't provide function itself

        :return: '' if NoSuchElementException is raised (only used by the _item_executer method)
        """
        @wraps(func)
        def decorator(inst, *args, **kwargs):
            attempt = 0
            success = False
            while not success:
                try:
                    func(inst, *args, **kwargs)
                except (NoSuchElementException, IndexError, TimeoutException) as e:
                    attempt += 1
                    if attempt > MAX_ATTEMPT:
                        inst._display_warning(e)
                        return NOT_FOUND_ITEM
                    continue
                else:
                    success = True
        return decorator

    def _key_filler(self, elem, value):
        """
        Allow filling forms with a random speed to stay undetected
        :param elem: elem in which to send keys
        :param value: string to send

        """
        for letter in value:
            elem.send_keys(letter)
            random_wait(TYPING_TIME_RANGE)
        random_wait(ACTION_TIME_RANGE)
        elem.send_keys(Keys.RETURN)

        try:
            self.driver.find_element_by_css_selector(self.key_filler_checker)
        except NoSuchElementException:
            self._display_warning('Can\'t fill the form with value {}, trying again...'.format(value))
            elem.clear()
            self._key_filler(elem, value)

    @_safe_action
    def _parameter_executer(self, action, field=None):
        if field is not None: # if None, this is a button
            value = self.search_keys[field]
        else:
            value = None

        print('• {0} ; value = {1} ; field = {2}'.format(repr(action), repr(value), repr(field)))

        random_wait(ACTION_TIME_RANGE)

        if action['method'] == methods.sendkeys:
            elem = self.driver.find_element_by_css_selector(action['path'])
            self._key_filler(elem, value) # humain-like keys typing
            self._display_info('{0} set to {1}'.format(field, value))

        elif action['method'] == methods.click or action['method'] == methods.pclick:
            if value is not None: # some buttons can be dynamically chosen
                if 'offset' in list(action.keys()):
                    value = str(int(value) + action['offset'])
                action['path'] = action['path'].replace(field, value) # ex : replace {room_number} by its actual value
            self.driver.execute_script('document.querySelector("{0}").click()'.format(action['path']))
            self._display_info('button clicked')

        elif action['method'] == methods.pclick:
            self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, action['next']))
            )
            self._display_info('page loaded')

        elif action['method'] == methods.value:
            self.driver.execute_script('el = document.querySelector("{0}")'.format(action['path']))
            self.driver.execute_script('el.value = arguments[0]', value) # hypothesis : we don't need to human typing look alike with js
            self._display_info('{0} set to {1}'.format(field, value))

        else:
            self._display_warning('{} is not a method'.format(action))

    def parameters_setter(self):
        """
        Set parameters of the search according to self.key_search
        Works in pair with the safely wrapped _parameter_executer
        """
        self.driver.get(self.link)
        self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self.search_fields[fields.location]['path']))) # item 'location' is arbitrary chosen, we just need to wait for some element
        for field, action in list(self.search_fields.items()):
            if field in list(self.search_keys.keys()):
                self._parameter_executer(action=action, field=field)
            if field in FIELD_WHITELIST:
                self._parameter_executer(action=action)

    @_safe_action
    def _wait_for_first_field(self):
        print('path to wait for : {}'.format(self.field_to_wait_for))
        self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self.field_to_wait_for))
        )
        random_wait(ACTION_TIME_RANGE)

    def _click_on_next(self):
        """
        Click on the next button to see the next page of item
        """
        self.next_button = self.next_button.replace('ul:nth-child(2)', 'ul:nth-child(3)').replace('{current_page_number+1_max_3}', '2')
        try:
            next_button = self.driver.find_element_by_css_selector(self.next_button)
            next_button.click()
            self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.item_to_wait_for))
            )
            return False
        except (NoSuchElementException, TimeoutException):
            return True

    @_safe_action
    def _item_executer(self, driver, lambda_func):
        return lambda_func(driver)

    def item_scraper(self):
        """
        Collect data from each item by creating a second webdriver.
        The action is executed according to the lambda functions defined in scrape_fields
        Works in pair with the safely wrapped _item_executer
        """
        while True:
            # url_list contains the url of all item to check by the second webdriver
            url_list = self.url_generator(self.driver)

            print('url_list', url_list)

            for url in url_list:

                # Among SeLoger items are found some link to Belle Demeure
                if BELLE_DEMEURE['base_url'] in url:
                    self.scrape_fields = self.scrape_fields['Belle_Demeure']
                    self.field_to_wait_for = BELLE_DEMEURE['field_to_wait_for']

                # some url in the list need to be blacklisted because they are reference to external websites
                for url_elem in URL_BLACK_LIST:
                    if url_elem in url:
                        break
                else:
                    driver2 = webdriver.Chrome('chromedriver')
                    driver2.get(url)
                    self._wait_for_first_field()

                    # defining an id based on Epoch
                    ##id = int(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()*1000)
                    scraping_results = {}
                    for field, lambda_func in list(self.scrape_fields.items()):

                        if isinstance(lambda_func, str):
                            scraping_results[field] = lambda_func
                        else:
                            for func in lambda_func:
                                try:
                                    result = func(driver2)
                                    # scraping_results[field] = self._item_executer(driver2, lambda_func) TODO
                                    break
                                except Exception as e:
                                    self._display_warning('Wrong path for {0} : {1}'.format(field, e))
                                    continue

                            if result != NOT_FOUND_ITEM:
                                scraping_results[field] = result
                                print('scraping_results : {}'.format(repr(scraping_results)))

                    self.result_list.append(Results(url=url, source=self.name, kwargs=scraping_results).clean_fields())

                    driver2.quit()

                    self.scraped_count += 1
                    self._display_info('[ {0}/{1} ] -- item scraped'.format(self.scraped_count, MAX_RESULT_PER_TARGET))
                    if self.scraped_count >= MAX_RESULT_PER_TARGET:
                        self._display_warning('Scraping Limit Reached')
                        return

            if(self._click_on_next()):
                self._display_warning('No next button clickable')
                [print(repr(result.info)) for result in self.result_list]
                return

    def _display_warning(self, msg):
        logger.warning('%s : %s', self.name, msg)
        print('WARNING: {0} : {1}'.format(self.name, msg))

    def _display_info(self, msg):
        logger.info('%s : %s', self.name, msg)
        print('INFO: {0} : {1}'.format(self.name, msg))



def main(driver):

    logprint('\n\n_________________AutoHunt 1.0 (beta)_________________\n\n')

    tic = time.time()

    result_sheet, input_sheet = open_spreadsheet(GOOGLE_SPREADSHEET_NAME)
    result_sheet_values, input_sheet_values = result_sheet.get_all_values(), input_sheet.get_all_values()

    search_keys = get_key(input_sheet_values)

    #search_keys = {'Localisation': 'Neuilly', 'Budget min': '100000', 'Budget max': '500000', 'Surface min': '30',
    #               'Surface max': '100', 'Nombre de pièces': 3}

    # Getting the list of all targets
    targets_list = get_target_list()

    result_list = []

    #driver.get('https://www.pap.fr/annonce/vente-immobiliere-paris-5e-g37772-3-pieces-jusqu-a-1200000-euros-a-partir-de-20-m2')

    #for target in targets_list:
    target = targets.Century21
    scraper = Scraper(name=target, driver=driver, search_keys=search_keys)
    scraper.parameters_setter()
    scraper.item_scraper()

    # scraper.result_list is a mutable class attribute, thus all Scraper objects share it
    result_list = scraper.result_list

    export_result_to_spreadsheet(input_sheet_values, result_sheet, result_list)

    toc = time.time()
    print('Durée: {} sec'.format(toc-tic))

class Test(object):

    def __init__(self, driver, search_keys, name):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, EC_MAX_TO_WAIT)
        self.name = name
        self.search_keys = search_keys
        self.search_fields = SEARCH_FIELDS[name]

    def _safe_action(func):
        @wraps(func)
        def decorator(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
                print('GOOD')
            except NoSuchElementException as e:
                self._display_warning(e)
                return NOT_FOUND_ITEM

        return decorator

    def parameters_setter(self):
        # Set parameters of the search according to self.key_search

        self.driver.get(SEARCH_LINKS[self.name])
        self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, self.search_fields[fields.location]['path']))) # item 'location' is arbitrary chosen, we just need to wait for some element

        for field, action in list(self.search_fields.items()):
            if field in list(self.search_keys.keys()):
                self.bar(action)  # , method=action['method'], field=field)
            if field in FIELD_WHITELIST:
                self.bar(action)  # , method=action['method'])

    def _display_warning(self, msg):
        print('WARNING {}'.format(msg))

    @_safe_action
    def bar(self, action):
        print("normal call")
        print('action {}'.format(action))
        self.driver.find_element_by_css_selector(action['path'])
        if isinstance(action['method'], tuple):
            print(repr(action['method'])[1])
        else:
            print(repr(action['method']))
        print(type(action['method']))

def test1():
    driver = webdriver.Chrome('chromedriver')
    search_keys = {'Localisation': 'Neuilly', 'Nombre de pieces': 3, 'Budget min': 300000, 'Budget max': 1200000,
                   'Surface min': 20, 'Surface max': 100}
    driver.get('https://www.pap.fr/annonces/appartement-paris-5e-r422401573')
    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'body > div.right-sidebar-layout.bg-grey-1.details-annonce-container > div > div.main-content > div.details-item > div > div > h1 > span.h1'))
    )

    #res = ['https://www.pap.fr/' + elem.split('href=')[1].split('"')[0] for elem in
    #           driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]').get_attribute('outerHTML').split(
    #               'item-title')[1:]]
    #res = [elem.find_element_by_css_selector('a').get_attribute('href') for elem in driver.find_elements_by_class_name("search-list-item")]
    print(SCRAPE_FIELDS[targets.PAP][results.title](driver))
    print(SCRAPE_FIELDS[targets.PAP][results.price](driver))
    print(SCRAPE_FIELDS[targets.PAP][results.date_creation](driver))
    print(SCRAPE_FIELDS[targets.PAP][results.surface](driver))
    print(SCRAPE_FIELDS[targets.PAP][results.photo_url](driver))

def test2():
    result_sheet, _, = open_spreadsheet(GOOGLE_SPREADSHEET_NAME)





if __name__ == '__main__':
    chromeOptions = webdriver.ChromeOptions()
    #opts = Options()
    prefs = {'profile.managed_default_content_settings.images': 2}
    chromeOptions.add_experimental_option("prefs", prefs)
    #prefs.add_argument(
    #    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36")
    driver = webdriver.Chrome(chrome_options=chromeOptions)

    main(driver=driver) #TODO close



