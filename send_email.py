import smtplib
import ssl
from configparser import ConfigParser

# Reading the configuration file
config = ConfigParser()
config.read('config.ini')


def send_email(message):
    port = config.getint('mailserver', 'port')
    smtp_server = config.get('mailserver', 'SMTPserver')
    sender_email = config.get('mailserver', 'senderEmail')
    receiver_email = config.get('mailserver', 'recepientEmail')
    password = config.get('mailserver', 'senderPassword')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        try:
            server.login(sender_email, password)
            res = server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"An email has been sent to {receiver_email}!")
        except:
            print("Error connecting to the mail server.")