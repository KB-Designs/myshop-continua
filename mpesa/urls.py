from django.urls import path
from . import views

urlpatterns = [
    path("lipa-na-mpesa/", views.lipa_na_mpesa, name="lipa_na_mpesa"),
    path("callback/", views.mpesa_callback, name="mpesa_callback"),
]
