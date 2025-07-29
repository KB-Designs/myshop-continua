import base64
import json
import requests
from datetime import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
import logging

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

    formatted_phone = format_phone_number(phone)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return render(request, 'mpesa/stk_push_error.html', {
            'error': {'errorMessage': 'Order not found'}
        })

    # Access token
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    auth_response = requests.get(auth_url, auth=(consumer_key, consumer_secret))
    try:
        access_token = auth_response.json().get('access_token')
    except ValueError:
        print("⚠️ Failed to decode access token JSON:", auth_response.text)
        return render(request, 'mpesa/stk_push_error.html', {
            'error': {'errorMessage': 'Unable to get access token from M-Pesa'}
        })

    if not access_token:
        return render(request, 'mpesa/stk_push_error.html', {
            'error': {'errorMessage': 'Access token not found in response'}
        })

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

    try:
        res_data = response.json()
    except ValueError:
        print("⚠️ M-Pesa STK Push response not JSON:", response.text)
        return render(request, 'mpesa/stk_push_error.html', {
            'order': order,
            'error': {'errorMessage': 'Invalid response from M-Pesa STK Push'}
        })

    if response.status_code == 200 and res_data.get('ResponseCode') == '0':
        order.checkout_request_id = res_data.get('CheckoutRequestID')
        order.mpesa_phone = formatted_phone
        order.save()
        return render(request, 'mpesa/stk_push_sent.html', {'order': order})
    else:
        return render(request, 'mpesa/stk_push_error.html', {
            'order': order,
            'error': res_data
        })


@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)

    try:
        stk_callback = data['Body']['stkCallback']
        result_code = stk_callback['ResultCode']
        checkout_request_id = stk_callback['CheckoutRequestID']

        try:
            order = Order.objects.get(checkout_request_id=checkout_request_id)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

        if result_code == 0:
            metadata = stk_callback['CallbackMetadata']['Item']
            receipt = next(item['Value'] for item in metadata if item['Name'] == 'MpesaReceiptNumber')
            amount = next(item['Value'] for item in metadata if item['Name'] == 'Amount')
            phone = next(item['Value'] for item in metadata if item['Name'] == 'PhoneNumber')

            order.paid = True
            order.payment_status = 'Paid'
            order.payment_reference = receipt
            order.mpesa_phone = phone
            order.save()
        else:
            order.payment_status = 'Failed'
            order.save()

    except Exception as e:
        print("Callback error:", str(e))

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Callback received successfully"})
