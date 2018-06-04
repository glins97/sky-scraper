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

class Result():
    def __init__(self, departure, arrival, price):
        now = datetime.datetime.now()
        self.departure = int(departure) if departure is not None else -1
        self.arrival = int(arrival) if departure is not None else -1
        self.price = int(price[price.index(' '):].replace('.', '')) if price != '' else -1

        self.departure_date = (now + datetime.timedelta(days=self.departure)) if departure is not None else None
        self.arrival_date = (now + datetime.timedelta(days=self.arrival)) if arrival is not None else None

    def __str__(self):
        return '\n\tDeparture: {departure}\n\tArrival: {arrival}\n\tPrice: {price}'.format(departure=self.departure_date.strftime(r"%Y-%m-%d"), arrival=self.arrival_date.strftime(r"%Y-%m-%d"), price=self.price)

    def __repr__(self):
        return '{departure} - {arrival}'.format(departure=self.departure_date.strftime(r"%d %b"), arrival=self.arrival_date.strftime(r"%d %b"))

class SkyScraper():
    def __init__(self, origin='JPA', destination='GRU', date='today', days_to_search=14, days_travelling_min=7, days_travelling_max=14, servered=False, **kwargs):
        self.results = {}
        self.days_to_search = days_to_search if type(days_to_search) == int else int(days_to_search)
        self.days_travelling_min = days_travelling_min if type(days_travelling_min) == int else int(days_travelling_min)
        self.days_travelling_max = days_travelling_max if type(days_travelling_max) == int else int(days_travelling_max)
        self.origin = origin
        self.destination = destination

        date_ = datetime.datetime.now().strftime(r"%Y-%m-%d")
        if date != 'today':
            date_ = date
        self.url = 'https://www.google.com/flights/?hl=pt#flt={origin}.{destination}.{date}*{destination}.{origin}.{date};c:BRL;e:1;sd:1;t:f'.format(origin=self.origin, destination=self.destination, date=date_)

	if servered:
		from pyvirtualdisplay import Display
		Display(visible=0, size=(1024, 728)).start()
    def start_scrape(self):
        self.driver = webdriver.Firefox()
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)
        self.driver.find_element_by_class_name('gws-flights-results__cheaper-dates-tip').click()

        self.load_next_arrival_element = self.driver.find_elements_by_class_name('gws-flights-pricefinder__next')[1]
        self.load_previous_arrival_element = self.driver.find_elements_by_class_name('gws-flights-pricefinder__prev')[1]
        self.load_next_departure_element = self.driver.find_elements_by_class_name('gws-flights-pricefinder__next')[0]

    def update_search_results(self):
        cells_ = []
        outer_cells = self.driver.find_elements_by_class_name('tSjb9yj4lbb__cell')
        for cell in outer_cells:
            cells_.append(cell.find_element_by_xpath('.//*'))

        results = [Result(cell.get_attribute('data-col'), cell.get_attribute('data-row'), cell.text) for cell in cells_ if cell is not None and (cell.text == '' or '$' in cell.text)]
        for result in results:
            if result.departure == -1 or result.arrival == -1 or result.price == -1:
                continue

            if result.arrival< result.departure  or result.arrival - result.departure < self.days_travelling_min or result.arrival - result.departure > self.days_travelling_max - 1:
                continue

            key = '{}-{}'.format(result.departure, result.arrival) 
            if key in self.results:
                if result.price > self.results[key].price:
                    self.results[key] = result
            else:
                self.results[key] = result

    def load_next_data_matrix(self, direction):
        ''' direction = ['up', 'down', 'right'] '''

        if direction == 'right':
            for _ in range(7):
                self.load_next_departure_element.click()
        if direction == 'up':
            for _ in range(7):
                self.load_previous_arrival_element.click()
        if direction == 'down':
            for _ in range(7):
                self.load_next_arrival_element.click()

    def get_cheapest_results(self):
        if not self.results:
            self.run()

        cheapest_dates = [self.results[self.results.keys()[0]]]
        cheapest_price = cheapest_dates[0].price

        for key in self.results:
            if self.results[key].price < cheapest_price:
                cheapest_dates = [self.results[key]]
                cheapest_price = self.results[key].price
            elif self.results[key].price == cheapest_price:
                cheapest_dates.append(self.results[key])

        return cheapest_price, [repr(result) for result in cheapest_dates]

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
    skyscraper = SkyScraper(origin='BSB', destination='JPA', date='2018-12-12', days_to_search=70, days_travelling_min=7, days_travelling_max=14).run()
    print skyscraper.get_cheapest_results()
