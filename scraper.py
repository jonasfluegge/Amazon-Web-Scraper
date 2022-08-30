import random
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from configparser import ConfigParser
from send_email import send_email

import requests

# Reading the configuration file
config = ConfigParser()
config.read('config.ini')
minutes = int(config.get('scraper', 'minutes'))
urls = config.get('scraper', 'urls').split()
maximumPrices = config.get('scraper', 'maximumPrices').split()
lastSentPrices = config.get('cache', 'lastSentPrices').split()
receiver_email = config.get('mailserver', 'recepientEmail')


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def refreshConfig():
    config.read('config.ini')
    lastSentPrices = config.get('cache', 'lastSentPrices').split()


def check_prices():
    global lastSentPrices
    for i in range(len(urls)):
        response = requests.get(urls[i], headers=headers)
        page = response.text
        soup = BeautifulSoup(page, "lxml")
        price = float(soup.find(name="span", class_="a-offscreen").getText().replace("€", "").replace(",", "."))
        name = (
            soup.find(name="span", id="productTitle", class_="a-size-large product-title-word-break").getText().strip())
        if price < float(maximumPrices[i]):
            if price != float(lastSentPrices[i]):
                print(f"The current price is {price}€, which is below the configured maximum price of {maximumPrices[i]}€, an email will be sent shortly.")
                msg = MIMEMultipart('alternative')
                msg['Subject'] = "Your configured price has fallen below"
                msg['From'] = "Amazon price alert"
                msg['To'] = receiver_email
                html = f"""\
                    <html>
                      <head></head>
                      <body>
                        <font size="4"><strong>The following product fell below the configured maximum price:</strong><br></font>
                        <br>
                        <font size="3"><strong>Product:</strong> {name}<br>
                        <strong>Current price:</strong> {price}€<br>
                        <strong>Your maximum price:</strong> {maximumPrices[i]}€<br>
                        <br>
                        <strong>Link:</strong> {urls[i]}</font>
                      </body>
                    </html>
                    """

                htmlpart = MIMEText(html, 'html')
                msg.attach(htmlpart)
                lastSentPrices[i] = str(price)
                lastSentPricesStr = " ".join(lastSentPrices)
                config['cache']['lastSentPrices'] = lastSentPricesStr

                with open('config.ini', 'w') as configfile:
                    config.write(configfile)

                refreshConfig()
                send_email(msg)
            else:
                print(f"The current price {price} is lower than the maximum price of {maximumPrices[i]}, but an email with the current price has already been sent. Don’t send an e-mail.")
        else:
            print(f"The current price of the item is {price}€, which is higher than the configured maximum price of {maximumPrices[i]}€. No email will be sent.")


while True:
    check_prices()
    secondsToSleep = 60 * minutes + random.randint(30, 60)
    print(f"Going to sleep for {secondsToSleep} seconds.")
    time.sleep(60 * minutes + random.randint(30, 60))
