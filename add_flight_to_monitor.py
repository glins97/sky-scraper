from skyscraper import SkyScraper
import sys
import argparse
import json
import codecs
import datetime
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--origin')
    parser.add_argument('--destination')
    parser.add_argument('--date')
    parser.add_argument('--days-to-search')
    parser.add_argument('--days-travelling-min')
    parser.add_argument('--days-travelling-max')
    parser.add_argument('--user-email')
    
    kwargs = {}
    for key, value in parser.parse_args()._get_kwargs():
        if value is not None:
            kwargs[key] = value
            
    if not os.path.exists('results'):
        with open('results', 'wb') as fd:
            fd.write('[]')

    results = []
    with open('results', 'rb') as fd:
        results = json.loads(fd.read())

    while True:
        if 'user_email' not in kwargs:
            print 'User e-mail is necessary. Please, try again.'
            break
        if 'origin' not in kwargs:
            kwargs['origin'] = 'JPA'
        if 'destination' not in kwargs:
            kwargs['destination'] = 'GRU'
        if 'date' not in kwargs:
            kwargs['date'] = 'today'
        if 'days_to_search' not in kwargs:
            kwargs['days_to_search'] = 14
        if 'days_travelling_min' not in kwargs:
            kwargs['days_travelling_min'] = 7
        if 'days_travelling_max' not in kwargs:
            kwargs['days_travelling_max'] = 14
        kwargs['results'] = {}
                
        results.append(kwargs)
        with codecs.open('results', 'wb', encoding='utf-8') as fd:
            fd.write(json.dumps(results, indent=2)) 
        
        break