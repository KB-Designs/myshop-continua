from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .utils import lipa_na_mpesa

def stk_push_payment(request):
    phone = request.GET.get('phone')  # Use a form in real case
    amount = request.GET.get('amount')

    response = lipa_na_mpesa(phone, int(amount))
    return JsonResponse(response)

