from django.urls import path
from .views import stk_push_payment

urlpatterns = [
    path('pay/', stk_push_payment, name='stk-push'),
]
