from skyscraper import SkyScraper
import json
import codecs
import datetime
import os
import sys
from mailer import Mailer

if __name__ == '__main__':
    flights = []
    with codecs.open('results', 'rb', encoding='utf-8') as fd:
        flights = json.loads(fd.read()) 

    mailer = Mailer('skyscraper.result@gmail.com', 'qazxsaq01')
    mailer.login()

    for index, flight in enumerate(flights):
        print 'Scraping for user {}...'.format(flight['user_email']),
        skyscraper = SkyScraper(servered=False if len(sys.argv) < 2 else (sys.argv[1].lower()=='true'), **flight)
        result = skyscraper.get_cheapest_results()
        print 'DONE'
        flights[index]['results'][datetime.datetime.now().strftime(r'%m_%d_%Y-%H_%M_%S')] = result
        mailer.send(flight['user_email'], u'Best price: R$ {:.2f}\n\nDates:\n{}'.format(result[0], '\n'.join(result[1])), u'Scraping results for {}'.format(flight['date']))
        del skyscraper

    with codecs.open('results', 'wb', encoding='utf-8') as fd:
        fd.write(json.dumps(flights, indent=2)) 
