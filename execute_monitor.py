
from skyscraper import SkyScraper
import json
import codecs
import datetime
import sys
import sendgrid
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(apikey='API-KEY')
from_email = Email('cron@gruponova.tech')

if __name__ == '__main__':
    flights = []
    with codecs.open('results', 'rb', encoding='utf-8') as fd:
        flights = json.loads(fd.read())

    for index, flight in enumerate(flights):
        print 'Scraping for user {}...'.format(flight['user_email']),
        skyscraper = SkyScraper(servered=False if len(sys.argv) < 2 else (sys.argv[1].lower()=='true'), **flight)
        result = skyscraper.get_cheapest_results()
        print 'DONE'
        flights[index]['results'][datetime.datetime.now().strftime(r'%d_%m_%Y-%H_%M_%S')] = result

	to_email = Email(flights[index]['user_email'])
	subject = 'Results from {} to {} at {}'.format(flight['origin'], flight['destination'], datetime.datetime.strptime(flight['date'], '%Y-%m-%d').strftime('%d of %b, %Y'))
	content = Content('text/plain', u'Best price: {:.2f}\n\n\n\nDates:\n\n{}'.format(result[0], '\n\n'.join(result[1])))
	mail = Mail(from_email, subject, to_email, content)
	response = sg.client.mail.send.post(request_body=mail.get())
        del skyscraper

    with codecs.open('results', 'wb', encoding='utf-8') as fd:
        fd.write(json.dumps(flights, indent=2))

