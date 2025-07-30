from django.urls import path
from . import views

app_name = 'mpesa'

urlpatterns = [
    path('stk-push/', views.stk_push, name='stk_push'),
    path('payment-status/<int:order_id>/', views.payment_status, name='payment_status'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
    path('payment-failed/<int:order_id>/', views.payment_failed, name='payment_failed'),
]
