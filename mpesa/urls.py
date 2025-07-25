from django.urls import path
from . import views

app_name = 'mpesa'

urlpatterns = [
    #path("lipa-na-mpesa/", views.lipa_na_mpesa, name="lipa_na_mpesa"),
    #path("callback/", views.mpesa_callback, name="mpesa_callback"),
    path('stk-push/', views.stk_push, name='stk_push')

]
