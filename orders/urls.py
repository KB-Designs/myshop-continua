from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('created/<int:order_id>/', views.order_created_view, name='order_created'), 
    path('ajax/load-pickup-stations/', views.load_pickup_stations, name='ajax_load_pickup_stations'), # ✅ new route
]
