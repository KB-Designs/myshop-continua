# mpesa/utils.py

import requests
from django.conf import settings

def get_access_token():
    """Get access token from M-Pesa API"""
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(auth_url, auth=(consumer_key, consumer_secret))
    return response.json().get("access_token")
