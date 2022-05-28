from bs4 import BeautifulSoup
import requests

from configparser import ConfigParser
from send_email import send_email

# Reading the configuration file
config = ConfigParser()
config.read('config.ini')
url = config.get('scraper', 'URL')
maximumPrice = config.getfloat('scraper', 'maximumPrice')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

response = requests.get(url, headers=headers)
page = response.text

soup = BeautifulSoup(page, "lxml")
price = float(soup.find(name="span", class_="a-offscreen").getText().replace("€", "").replace(",", "."))
name = (soup.find(name="span", id="productTitle", class_="a-size-large product-title-word-break").getText().strip())

if price <= maximumPrice:
    message = (f"From: Amazon price alert\nSubject:Your configured price has fallen below\n\n{name} is now {price} euro.\n\nFollow the link to get it\n{url}")
    print(f"The current price {price}€ is below the configured maximum price of {maximumPrice}, an email will be sent shortly.")
    send_email(message)
