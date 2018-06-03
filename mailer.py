import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

class Mailer():
    def __init__(self, sender='', password=''):
        self.sender = sender
        self.password = password

        print 'Connecting to SMTP...',
        self.mail = smtplib.SMTP('smtp.gmail.com', 587)
        self.mail.ehlo()
        self.mail.starttls()
        print 'DONE'

    def login(self):
        print 'Logging in...',
        self.mail.login(self.sender, self.password)
        print 'DONE'

    def send(self, receiver='', text='', subject=''):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(text, 'plain'))

        print 'Sending mail to {}...'.format(receiver),
        self.mail.sendmail(self.sender, receiver, msg.as_string())
        print 'DONE'
