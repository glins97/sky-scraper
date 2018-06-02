#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import codecs
import time
import datetime

class SkyScraper():
    def __init__(self, visible=True, date='today', days_to_search=70, days_travelling_min=0, days_travelling_max=14):
        ''' date format => 2018-12-31 '''
        if visible:
            self.driver = webdriver.Firefox()
        else:
            self.driver = webdriver.PhantomJS()
        self.results = {}
        self.days_to_search = days_to_search
        self.days_travelling_min = days_travelling_min
        self.days_travelling_max = days_travelling_max

        date_ = datetime.datetime.now().strftime(r"%Y-%m-%d")
        if date != 'today':
            date_ = date
        self.url = "https://www.google.com/flights/?hl=pt#flt=/m/01hy_.JPA." + date_  + "*JPA./m/01hy_."  + date_ +  ";c:BRL;e:1;sd:1;t:f"
        
    def start_scrape(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)
        self.driver.find_element_by_class_name('gws-flights-results__cheaper-dates-tip').click()

        self.load_next_back_element = self.driver.find_elements_by_class_name('gws-flights-pricefinder__next')[1]
        self.load_previous_back_element = self.driver.find_elements_by_class_name('gws-flights-pricefinder__prev')[1]
        self.load_next_go_element = self.driver.find_elements_by_class_name('gws-flights-pricefinder__next')[0]

    def update_search_results(self):
        cells_ = []
        outer_cells = self.driver.find_elements_by_class_name('tSjb9yj4lbb__cell')
        for cell in outer_cells:
            cells_.append(cell.find_element_by_xpath('.//*'))

        cells = [[cell.text.replace('.', ''), cell.get_attribute('data-col'), cell.get_attribute('data-row')] for cell in cells_ if cell is not None and (cell.text == '' or '$' in cell.text)]
        for cell in cells:
            if cell[1] is None or cell[2] is None:
                continue
            cell[1] = int(cell[1])
            cell[2] = int(cell[2])
                
            if cell[0] == '':
                continue
            else:
                cell[0] = int(cell[0][2:])

            if cell[2] < cell[1] or cell[2] - cell[1] < self.days_travelling_min or cell[2] - cell[1] > self.days_travelling_max - 1:
                continue

            key = '{}-{}'.format(cell[1], cell[2]) 
            if key in self.results:
                if cell[0] > self.results[key]:
                    self.results[key] = cell[0]
            else:
                self.results[key] = cell[0]

    def load_next_data_matrix(self, direction):
        ''' direction = ['up', 'down', 'right'] '''

        if direction == 'right':
            for _ in range(7):
                self.load_next_go_element.click()
        if direction == 'up':
            for _ in range(7):
                self.load_previous_back_element.click()      
        if direction == 'down':
            for _ in range(7):
                self.load_next_back_element.click()

    def get_cheapest_results(self):
        cheapest_dates = []
        cheapest_price = self.results[self.results.keys()[0]]

        for key in self.results:
            if self.results[key] < cheapest_price:
                cheapest_dates = [key]
                cheapest_price = self.results[key]
            elif self.results[key] == cheapest_price:
                cheapest_dates.append(key)
        return cheapest_price, cheapest_dates

    def save_results(self, filename=None):
        sort_key = lambda item: 1000 * int(item.split('-')[0]) + int(item.split('-')[1])
        keys = sorted(self.results.keys(), key=sort_key)
        if filename is None:
            filename = datetime.datetime.now().strftime(r'%m_%d_%Y-%H_%M_%S') + '.csv'
        if '.csv' not in filename:
            filename = filename + '.csv'
        with codecs.open(filename, 'wb', encoding='utf-8') as fd:
            count = 0
            for key in keys:
                count += 1
                fd.write(str(self.results[key]) + ', ')
                if count == self.days_travelling_max - self.days_travelling_min:
                    fd.write('\n')
                    count = 0

    def run(self, save_results=False, result_filename=None):
        self.start_scrape()
        self.update_search_results()
        for _ in range(0, self.days_travelling_max, 7):
            self.load_next_data_matrix('down')
            self.update_search_results()

        for _ in range(7, self.days_to_search, 7):
            self.load_next_data_matrix('right')
            self.update_search_results()
            for _ in range(7, self.days_travelling_max, 7):
                self.load_next_data_matrix('up')
                self.update_search_results()
            for _ in range(7, self.days_travelling_max, 7):
                self.load_next_data_matrix('down')
            self.load_next_data_matrix('down')
            self.update_search_results()
        if save_results:
            self.save_results(filename=result_filename)
        self.driver.close()
        return self

if __name__ == '__main__':
    skyscraper = SkyScraper(date='2018-12-20', days_to_search=30, days_travelling_min=7, days_travelling_max=14).run(save_results=True)
    print skyscraper.get_cheapest_results()