# mpesa/utils.py
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
import base64
from datetime import datetime

def get_mpesa_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    response = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    access_token = response.json().get('access_token')
    return access_token

def generate_password(shortcode, passkey):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = shortcode + passkey + timestamp
    encoded = base64.b64encode(data_to_encode.encode()).decode('utf-8')
    return encoded, timestamp
    




