# mpesa/views.py
import base64
import requests
from datetime import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from orders.models import Order

from django.views.decorators.csrf import csrf_exempt
import json
from orders.models import Order

def format_phone_number(phone):
    phone = phone.strip().replace(' ', '').replace('+', '')

    if phone.startswith('07'):
        return '254' + phone[1:]
    elif phone.startswith('254'):
        return phone
    elif phone.startswith('1') and len(phone) == 9:
        return '254' + phone
    else:
        return phone  # fallback

def stk_push(request):
    order_id = request.session.get('mpesa_order_id')
    phone = request.session.get('mpesa_phone')

    if not order_id or not phone:
        return redirect('orders:order_create')

    # ✅ Format the phone number right after retrieving it
    formatted_phone = format_phone_number(phone)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return render(request, 'mpesa/stk_push_error.html', {
            'error': {'errorMessage': 'Order not found'}
        })

    # Step 1: Get access token
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    auth_response = requests.get(auth_url, auth=(consumer_key, consumer_secret))
    access_token = auth_response.json().get('access_token')

    # Step 2: Prepare STK Push request
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
    ).decode()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(order.get_total_cost()),
        "PartyA": formatted_phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": formatted_phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"ORDER{order.id}",
        "TransactionDesc": "Order Payment"
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )

    res_data = response.json()
    if response.status_code == 200 and res_data.get('ResponseCode') == '0':
        return render(request, 'mpesa/stk_push_sent.html', {'order': order})
    else:
        return render(request, 'mpesa/stk_push_error.html', {'order': order, 'error': res_data})


#callback view to handle M-Pesa responses
@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body.decode('utf-8'))

    try:
        stk_callback = data['Body']['stkCallback']
        result_code = stk_callback['ResultCode']

        if result_code == 0:
            metadata = stk_callback['CallbackMetadata']['Item']
            order_id = int(stk_callback['CheckoutRequestID'].split('-')[-1])  # Optional if you use ref

            # Extract fields
            receipt = next(i['Value'] for i in metadata if i['Name'] == 'MpesaReceiptNumber')
            phone = next(i['Value'] for i in metadata if i['Name'] == 'PhoneNumber')
            amount = next(i['Value'] for i in metadata if i['Name'] == 'Amount')

            # You can link by reference/account or session
            order = Order.objects.filter(
                paid=False,
                get_total_cost__gte=amount,  # Optional safeguard
                phone=phone
            ).last()

            if order:
                order.paid = True
                order.mpesa_receipt_number = receipt
                order.mpesa_phone = phone
                order.save()
        else:
            print("❌ Payment failed:", stk_callback['ResultDesc'])

    except Exception as e:
        print("Callback error:", str(e))

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Received ok"})