import base64
import requests
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

# Create a logger
logger = logging.getLogger(__name__)

def lipa_na_mpesa(request):
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Encode password
    password_str = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    password = base64.b64encode(password_str.encode()).decode()

    # Get access token
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth_response = requests.get(auth_url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    access_token = auth_response.json().get("access_token")

    # STK Push endpoint
    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,  # 174379
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": "254769876650",  # 🔴 Replace with your number
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": "254769876650",  # 🔴 Replace with your number
        "CallBackURL": "https://5715050c7dca.ngrok-free.app/mpesa/callback/",  # 👈 your ngrok HTTPS URL
        "AccountReference": "Test001",
        "TransactionDesc": "Payment for testing"
    }

    response = requests.post(stk_url, json=payload, headers=headers)
    return JsonResponse(response.json())

@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        logger.info(f"Callback data: {json.dumps(data, indent=4)}")
        print("M-PESA CALLBACK DATA:", json.dumps(data, indent=4))
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Received Successfully"})

