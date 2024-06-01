import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import logging
import random

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# User input
CAR_MODEL = input('Enter car model (e.g., Toyota Camry): ')
EMAIL_ADDRESS = input('Enter your email address: ')
EMAIL_PASSWORD = input('Enter your email password: ')
RECIPIENT_EMAIL = input("Enter recipient's email address: ")
CAR_MILEAGE = input('Enter preferred car mileage: ')
CAR_COLOR = input('Enter preferred car color: ')
CHECK_INTERVAL = 2500  # Check every 2500 secs

# Websites to scrape
WEBPAGES = {
    
    'Cars.com': 'https://www.cars.com/for-sale/searchresults.action/?dealerType=all&mdId=20688&mkId=20088&searchSource=QUICK_FORM&zc=94016',
    'Edmunds': 'https://www.edmunds.com/inventory/srp.html?make=toyota&model=camry&zip=94016',
    'AutoTrader': 'https://www.autotrader.com/cars-for-sale/all-cars/toyota/camry/94016',
    'Carvana': 'https://www.carvana.com/cars/toyota-camry',
    'TrueCar': 'https://www.truecar.com/used-cars-for-sale/listings/toyota/camry/location-san-francisco-ca/',
    'Vroom': 'https://www.vroom.com/cars/toyota/camry',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Function to send email notification
def send_email_notification(car_details):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = 'Car Found!'
        body = f'The car {CAR_MODEL} has been found!\n\nDetails:\n{car_details}'
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        logging.info('Email notification sent successfully.')
    except Exception as e:
        logging.error(f'Failed to send email: {e}')

# Generic scraper function
def scrape_website(name, url, car_model, car_mileage, car_color, parser_func):
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return parser_func(soup, car_model, car_mileage, car_color)
        else:
            logging.warning(f'Failed to retrieve {name} page. Status code: {response.status_code}')
            return None
    except requests.RequestException as e:
        logging.error(f'Error fetching {name} page: {e}')
        return None

# Specific parsers for each website


def parse_carscom(soup, car_model, car_mileage, car_color):
    cars = soup.find_all('div', class_='shop-srp-listings__listing-container')
    for car in cars:
        title = car.find('h2', class_='title')
        mileage = car.find('div', class_='listing-row__mileage')
        color = car.find('div', class_='listing-row__exterior-color')
        if title and car_model in title.text.strip() and car_mileage in mileage.text.strip() and car_color in color.text.strip():
            return car.text.strip()
    return None

def parse_edmunds(soup, car_model, car_mileage, car_color):
    cars = soup.find_all('div', class_='inventory-listing-body')
    for car in cars:
        title = car.find('a', class_='usurp-inventory-card-model')
        mileage = car.find('div', class_='usurp-inventory-card-mileage')
        color = car.find('div', class_='usurp-inventory-card-exterior-color')
        if title and car_model in title.text.strip() and car_mileage in mileage.text.strip() and car_color in color.text.strip():
            return car.text.strip()
    return None

def parse_autotrader(soup, car_model, car_mileage, car_color):
    cars = soup.find_all('div', class_='inventory-listing')
    for car in cars:
        title = car.find('h2', class_='text-bold')
        mileage = car.find('span', class_='text-bold text-size-400 text-size-sm-500')
        color = car.find('div', class_='text-size-200 text-size-sm-300')
        if title and car_model in title.text.strip() and car_mileage in mileage.text.strip() and car_color in color.text.strip():
            return car.text.strip()
    return None

def parse_carvana(soup, car_model, car_mileage, car_color):
    cars = soup.find_all('div', class_='result-tile')
    for car in cars:
        title = car.find('h2')
        mileage = car.find('div', class_='result-tile-details')
        color = car.find('div', class_='result-tile-exterior')
        if title and car_model in title.text.strip() and car_mileage in mileage.text.strip() and car_color in color.text.strip():
            return car.text.strip()
    return None

def parse_truecar(soup, car_model, car_mileage, car_color):
    cars = soup.find_all('div', class_='card-content vehicle-card-body order-3 vehicle-card-carousel-body')
    for car in cars:
        title = car.find('span', class_='vehicle-header-make-model')
        mileage = car.find('div', class_='vehicle-card-mileage')
        color = car.find('div', class_='vehicle-card-exterior-color')
        if title and car_model in title.text.strip() and car_mileage in mileage.text.strip() and car_color in color.text.strip():
            return car.text.strip()
    return None

def parse_vroom(soup, car_model, car_mileage, car_color):
    cars = soup.find_all('div', class_='vehicle-card')
    for car in cars:
        title = car.find('h4')
        mileage = car.find('div', class_='vehicle-card-mileage')
        color = car.find('div', class_='vehicle-card-exterior-color')
        if title and car_model in title.text.strip() and car_mileage in mileage.text.strip() and car_color in color.text.strip():
            return car.text.strip()
    return None

# Dictionary mapping website names to their respective parsing functions
PARSERS = {
    
    'Cars.com': parse_carscom,
    'Edmunds': parse_edmunds,
    'AutoTrader': parse_autotrader,
    'Carvana': parse_carvana,
    'TrueCar': parse_truecar,
    'Vroom': parse_vroom,
}

# Main function to check all websites
def check_all_websites():
    for name, url in WEBPAGES.items():
        parser_func = PARSERS[name]
        result = scrape_website(name, url, CAR_MODEL, CAR_MILEAGE, CAR_COLOR, parser_func)
        if result:
            send_email_notification(result)
            return True
        time.sleep(random.uniform(1, 3))  # Add delay to avoid detection
    return False

# Main loop to continuously check for the car
while True:
    found = check_all_websites()
    if found:
        break
    time.sleep(CHECK_INTERVAL)
