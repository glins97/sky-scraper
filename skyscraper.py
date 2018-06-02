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
driver = webdriver.Firefox()
def replace_month(string):
    string = string.replace(' de jan', '/01')
    string = string.replace(' de fev', '/02')
    string = string.replace(' de mar', '/03')
    string = string.replace(' de abr', '/04')
    string = string.replace(' de mai', '/05')
    string = string.replace(' de jun', '/06')
    string = string.replace(' de jul', '/07')
    string = string.replace(' de ago', '/08')
    string = string.replace(' de set', '/09')
    string = string.replace(' de out', '/10')
    string = string.replace(' de nov', '/11')
    string = string.replace(' de dez', '/12')
    return string

def save_new_values(driver, old_values):
    time.sleep(1)    
    values = old_values
    # loads cells from active matrix
    cells_ = []
    outer_cells = driver.find_elements_by_class_name('tSjb9yj4lbb__cell')
    for cell in outer_cells:
        cells_.append(cell.find_element_by_xpath('.//*'))

    cells = [[cell.text, cell.get_attribute('data-col'), cell.get_attribute('data-row')] for cell in cells_ if cell is not None and (cell.text == '' or '$' in cell.text)]
    for cell in cells:
        if cell[1] is None or cell[2] is None:
            continue
        cell[1] = int(cell[1])
        cell[2] = int(cell[2])
            
        if cell[0] == '':
            continue
        else:
            cell[0] = int(cell[0][2:])

        if cell[2] < cell[1] or cell[2] - cell[1] < days_travelling_min or cell[2] - cell[1] > days_travelling_max - 1:
            continue

        key = '{}-{}'.format(cell[1], cell[2]) 
        if key in values:
            if cell[0] > values[key]:
                values[key] = cell[0]
        else:
            values[key] = cell[0]
    #
    return values


START_TIME = time.time()
driver.get("https://www.google.com/flights/?hl=pt#flt=/m/01hy_./m/022pfm.2018-06-01*/m/022pfm./m/01hy_.2018-06-01;c:BRL;e:1;sd:1;t:f")
driver.implicitly_wait(10)

wrapper = driver.find_element_by_class_name('gws-flights-results__price-finder-tips-wrapper')
driver.find_element_by_class_name('gws-flights-results__cheaper-dates-tip').click()
load_next_back_element = driver.find_elements_by_class_name('gws-flights-pricefinder__next')[1]
load_previous_back_element = driver.find_elements_by_class_name('gws-flights-pricefinder__prev')[1]
load_next_go_element = driver.find_elements_by_class_name('gws-flights-pricefinder__next')[0]

def load_next_matrix(direction):
    ''' direction = ['up', 'down', 'right'] '''

    if direction == 'right':
        for _ in range(7):
            load_next_go_element.click()
    if direction == 'up':
        for _ in range(7):
            load_previous_back_element.click()      
    if direction == 'down':
        for _ in range(7):
            load_next_back_element.click()

values = {}

step = 7

days_to_search = 70
days_travelling_min = 0
days_travelling_max = 7

#########
save_new_values(driver, values)
for _ in range(0, days_travelling_max, step):
    load_next_matrix('down')
    save_new_values(driver, values)

for a in range(step, days_to_search, step):
    load_next_matrix('right')
    save_new_values(driver, values)
    for _ in range(step, days_travelling_max, step):
        load_next_matrix('up')
        save_new_values(driver, values)
    for _ in range(step, days_travelling_max, step):
        load_next_matrix('down')
    load_next_matrix('down')
    save_new_values(driver, values)
#########

driver.close()

# prints cheapest dates
cheapest_dates = []
cheapest_price = values[values.keys()[0]]

for key in values:
    if values[key] < cheapest_price:
        cheapest_dates = [key]
        cheapest_price = values[key]
    elif values[key] == cheapest_price:
        cheapest_dates.append(key)
#

# saves search as csv
sort_key = lambda item: 1000 * int(item.split('-')[0]) + int(item.split('-')[1])
keys = sorted(values.keys(), key=sort_key)
print keys 
with codecs.open(datetime.datetime.now().strftime(r'%m_%d_%Y-%H_%M_%S') + '.csv', 'wb', encoding='utf-8') as fd:
    count = 0
    for key in keys:
        count += 1
        fd.write(str(values[key]) + ', ')
        print 'writing', str(values[key]), 'from', key
        if count == days_travelling_max - days_travelling_min:
            fd.write('\n')
            count = 0

print u'Preço mais baixo:', cheapest_price
print u'Datas mais baratas:', json.dumps(cheapest_dates)
print time.time() - START_TIME
