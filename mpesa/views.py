# mpesa/views.py
from django.http import JsonResponse
from .utils import get_mpesa_access_token, generate_password
import requests
import os

def token_view(request):
    token = get_mpesa_access_token()
    return JsonResponse({'access_token': token})


def stk_push_request(request):
    access_token = get_mpesa_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    business_short_code = os.getenv("MPESA_SHORTCODE", "174379")
    passkey = os.getenv("MPESA_PASSKEY", "your_passkey_here")
    phone_number = "254769876650"  # Replace with your test phone number

    password, timestamp = generate_password(business_short_code, passkey)

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/mpesa/callback/",
        "AccountReference": "TestAccount",
        "TransactionDesc": "Test Payment"
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return JsonResponse(response.json())
