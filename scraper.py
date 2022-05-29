from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bs4 import BeautifulSoup
import requests

from configparser import ConfigParser
from send_email import send_email

# Reading the configuration file
config = ConfigParser()
config.read('config.ini')
url = config.get('scraper', 'URL')
maximumPrice = config.getfloat('scraper', 'maximumPrice')
receiver_email = config.get('mailserver', 'recepientEmail')

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
        <font size="3"><strong>Name:</strong> {name}<br>
        <strong>Price:</strong> {price}€<br>
        <strong>Max. price:</strong> {maximumPrice}€<br>
        <br>
        <strong>Link:</strong> {url}</font>
      </body>
    </html>
    """

    htmlpart = MIMEText(html, 'html')
    msg.attach(htmlpart)

    print(f"The current price is {price}€, which is below the configured maximum price of {maximumPrice}€, an email will be sent shortly.")
    send_email(msg)
else:
    print(f"The current price of the item is {price}€, which is higher than the configured maximum price of {maximumPrice}€. No email will be sent.")
