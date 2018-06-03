from skyscraper import SkyScraper
import json
import codecs
import datetime
import os

if __name__ == '__main__':
    flights = []
    with codecs.open('results', 'rb', encoding='utf-8') as fd:
        flights = json.loads(fd.read()) 

    for index, flight in enumerate(flights):
        skyscraper = SkyScraper(**flight)
        flights[index]['results'][datetime.datetime.now().strftime(r'%m_%d_%Y-%H_%M_%S')] = skyscraper.get_cheapest_results()
        del skyscraper

    with codecs.open('results', 'wb', encoding='utf-8') as fd:
        fd.write(json.dumps(flights, indent=2)) 