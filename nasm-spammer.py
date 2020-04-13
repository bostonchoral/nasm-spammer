#!/usr/bin/python

# Compatibility with Python 3.
from __future__ import print_function

import csv
import datetime
import getpass
import io
import logging
import os
import random
import re
import sys
import time
import traceback

# Need to "pip install selenium" (done in ./install)
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import Safari
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as expect

site = 'https://nasm.arts-accredit.org'

# This optional file contains the login info: user then password on separate lines
nasm_user_file_name = 'nasm-user.txt'

# This output file is a TSV (tab-separated values) containing (institution name), (NASM page ID) for each institution.
catalog_file_name = 'catalog.tsv'

# This output file is a TSV (tab-separated values) containing the following columns.
output_file_name = 'contacts.tsv'
output_column_names = ['school', 'nasm_link', 'website', 'name', 'title', 'email']

tmp_suffix = '.tmp'

# Configure logging.
logging.basicConfig(format='%(asctime)s | %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.INFO)


# These functions work around the fact that the "csv" package doesn't support Unicode.
# They're taken straight from the Python documentation at https://docs.python.org/2/library/csv.html .
def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_data):
    for line in unicode_data:
        yield line.encode('utf-8')


class nasm_scraper(object):
    def __init__(self, browser_constructor, browser_name):
        self.preexisting_schools = set()
        self.browser_name = browser_name
        self.browser_constructor = browser_constructor
        self.browser = None

    def start_browser(self):
        logging.info('Starting a {} browser session...'.format(self.browser_name))
        self.browser = self.browser_constructor()
        logging.info('{} is active.'.format(self.browser_name))

    def wait_up_to(self, seconds):
        return WebDriverWait(self.browser, seconds, ignored_exceptions=(NoSuchElementException,StaleElementReferenceException))
        
    def get_user_and_password(self, user=None, password=None):
        '''
        Get the username and password for NASM - 
        either from nasm-user.txt, if it exists, or by asking the user to type them in.
        '''
        
        # First try reading from nasm-user.txt
        if os.path.isfile(nasm_user_file_name):
            with open(nasm_user_file_name) as f:
                lines = f.read().splitlines()
                user = lines[0]
                password = lines[1]

        # If file was not found and nothing was supplied, ask for username and password
        if not user:
            user = raw_input("NASM Username: ")
        if not password:
            password = getpass.getpass("NASM Password: ")
        return user, password
    
    def login(self, user=None, password=None):
        '''Log in to NASM.'''

        # Go to the login page.
        user, password = self. get_user_and_password(user, password)
        url = os.path.join(site, 'login')
        logging.info('Logging into url[{}] as user[{}]'.format(url, user))
        self.browser.get(url)

        # Type in the username and password, and submit.
        self.browser.find_element_by_id('user_login').send_keys(user)
        self.browser.find_element_by_id('user_pass').send_keys(password)
        self.browser.find_element_by_id('wp-submit').click()

        # We should be sent to the "My Account" page.
        self.wait_up_to(seconds=30).until(lambda x: self.browser.title.startswith("My Account"))
        logging.info('Login successful.')

    def download_catalog(self):
        '''
        Open the catalog page (the list of all institutions) and write its contents to catalog.tsv.
        '''
        
        # Go to the search page and submit the "institution search" form with no values filled in.
        # It should return a list of all institutions.
        url = os.path.join(site, 'directory-lists/accredited-institutions/search/')
        logging.info('Retrieving catalog page at url[{}]'.format(url))
        self.browser.get(url)
        self.browser.find_element_by_id('institution-search').submit()
        self.wait_up_to(seconds=120).until(
            lambda x: any(re.search('search returned \d+ results', elt.text, re.IGNORECASE) is not None
                          for elt in self.browser.find_elements_by_xpath('//h2')))
        logging.info('Catalog page retrieved.')

        # Find the page ID for every institution, and write them to a new catalog file.
        catalog_tmp_file_name = catalog_file_name + tmp_suffix
        with io.open(catalog_tmp_file_name, 'w', encoding='utf8') as catalog_file:
            search_result_wrapper = self.browser.find_element_by_class_name('wpb_wrapper')
            # Find every <a> element within the wpb_wrapper.
            links = search_result_wrapper.find_elements_by_xpath('.//a')
            for link in links:
                institution_name = link.text.replace(u'\n', u'').replace(u'\t', u' ')
                link_target = link.get_attribute('href')
                print(institution_name, link_target, sep=u'\t', file=catalog_file)
        os.rename(catalog_tmp_file_name, catalog_file_name)
        logging.info('Catalog page downloaded to file[{}]'.format(catalog_file_name))

    def scan_preexisting_output_file(self):
        '''
        Scan a previously generated output file and remember which schools it contained,
        so we can pick up where we left off and we don't have to process those schools again.
        '''
        if not os.path.exists(output_file_name):
            return
        with io.open(output_file_name, 'r', encoding='utf8') as preexisting_file:
            csv_reader = unicode_csv_reader(preexisting_file, delimiter='\t')
            for row in csv_reader:
                self.preexisting_schools.add(row[0])
        
    def loop_catalog(self):
        '''
        Loop through the catalog file and look up the info page for every school.
        Append that school's information to the output file.
        '''
        output_file_existed = os.path.exists(output_file_name)
        with io.open(catalog_file_name, 'r', encoding='utf8') as catalog_file:
          with io.open(output_file_name, 'a', encoding='utf8') as output_file:
            if not output_file_existed:
                print(u'\t'.join(output_column_names), file=output_file)
                
            csv_reader = unicode_csv_reader(catalog_file, delimiter='\t')
            for row in csv_reader:
                if row[0] in self.preexisting_schools:
                    continue
                try:
                    contacts_found = self.lookup_school(row[0], row[1])
                    for contact_info_fields in contacts_found:
                        print(u'\t'.join(contact_info_fields), file=output_file)
                except Exception as e:
                    logging.error(u'Error looking up school[{}] at url[{}]: {}'.format(row[0], row[1], traceback.format_exc()))

                # Sleep somewhere beween 20 and 50 seconds between each page access
                # so we don't overwhelm the server, and the access pattern looks more like a human user.
                output_file.flush()
                time.sleep(random.uniform(20, 50))

    def lookup_school(self, school_name, info_url):
        '''
        Go to the school's NASM info page, and return a list of all contacts with email addresses on that page.
        '''
        result = []
        
        # Go to a blank page so wait_up_to can detect a change from the current page.
        self.browser.get('about:blank')
        time.sleep(0.5)
        
        # Go to the school's info URL on the NASM site.
        self.browser.get(info_url)
        self.wait_up_to(seconds=30).until(lambda x: self.browser.find_element_by_id('footer') is not None)
        result_wrapper = self.browser.find_element_by_class_name('wpb_wrapper')

        # Find the school's website: Starting from <H2>, find a following <P> whose text contains "Web Site",
        # then return its first child matching <A HREF="...">.
        xpath = "//h2/following-sibling::p[text()[contains(.,'Web Site:')]]/a[@href]"
        school_websites = result_wrapper.find_elements_by_xpath(xpath)
        school_website = school_websites[0].get_attribute('href') if school_websites else ""

        # Find the "contacts" section: Starting from <H3>Contacts</H3>, return all following <P>s whose text contains "E-mail:".
        xpath = "//h3[starts-with(text(),'Contacts')]/following-sibling::p[text()[contains(., 'E-Mail:')]]"
        contact_elements = result_wrapper.find_elements_by_xpath(xpath)
        logging.info(u"Found school [{}] with website[{}] and {} contacts".format(school_name, school_website, len(contact_elements)))

        # Return each contact in a list so it can be written to the output file.
        for contact in contact_elements:
            name_and_title = contact.find_element_by_xpath("./text()[1]").text
            name_and_title = re.sub(r'\s+', ' ', name_and_title)
            if ',' in name_and_title:
                name, title = re.split(r',\s*', name_and_title, maxsplit=1)
            else:
                name, title = name_and_title, ''
            email = contact.find_element_by_xpath("./a[text()[contains(., '@')]]/text()").text
            logging.info(u"Found contact name[{}] title[{}] email[{}] at school[{}]".format(name, title, email, school_name))
            result.append([school_name, info_url, school_website, name, title, email])

        return result
        
    def main(self):
        user, password = self.get_user_and_password()
        self.start_browser()
        try:
            self.login(user, password)
            if not os.path.exists(catalog_file_name):
                self.download_catalog()
            self.scan_preexisting_output_file()
            self.loop_catalog()
        finally:
            self.browser.quit()


if __name__ == '__main__':
    nasm_scraper(Safari, 'Safari').main()
