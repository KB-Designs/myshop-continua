# mpesa/urls.py
from django.urls import path
from .views import stk_push_request, token_view

app_name = 'mpesa'

urlpatterns = [
    path('token/', token_view, name='mpesa_token'),
    path("stk-push/", stk_push_request, name="stk_push"),
]
