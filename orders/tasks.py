# orders/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@shared_task
def order_created(order_id):
    """
    Sends an email notification to the customer after a successful order placement.
    
    Args:
        order_id (int): The ID of the order that was created.
    
    Returns:
        int: Number of successfully delivered messages (1 if sent successfully).
    """
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Order Confirmation - Order No. {order.id}'
        message = (
            f'Dear {order.first_name},\n\n'
            f'Thank you for your order!\n'
            f'Your order ID is {order.id}.\n\n'
            f'We will notify you once it is shipped.\n\n'
            f'Best regards,\n'
            f'MyShop Team'
        )
        return send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # ✅ Use configured sender email
            [order.email]
        )
    except Order.DoesNotExist:
        return 0
