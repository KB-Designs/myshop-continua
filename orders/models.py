from django.db import models
from shop.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from coupons.models import Coupon


# Payment method choices
PAYMENT_METHOD_CHOICES = [
    ('mpesa', 'Lipa na M-Pesa'),
    ('cod', 'Cash on Delivery'),
]

# County choices
COUNTY_CHOICES = [
    ('Nairobi', 'Nairobi'),
    ('Mombasa', 'Mombasa'),
    ('Kisumu', 'Kisumu'),
    # Add more counties as needed
]

# Pickup station choices for the form — not stored in DB directly
PICKUP_STATION_CHOICES = {
    'Nairobi': ['CBD', 'Westlands'],
    'Mombasa': ['Nyali', 'Likoni'],
    'Kisumu': ['Milimani', 'Kondele'],
}

class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    county = models.CharField(max_length=100, choices=COUNTY_CHOICES)
    pickup_station = models.CharField(max_length=100)  # Filled via dropdown in form
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    
    paid = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed')
    ], default='Pending')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=255, blank=True, null=True)
    mpesa_phone = models.CharField(max_length=15, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey(Coupon,
                                related_name='orders',
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL)
    discount = models.IntegerField(default=0,
                                    validators=[MinValueValidator(0),
                                                MaxValueValidator(100)])
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Order {self.id} - {self.first_name} {self.last_name}'

    def get_total_cost(self):
        total_cost= sum(item.get_cost() for item in self.items.all())
        return total_cost - total_cost * (self.discount / Decimal(100))

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def get_cost(self):
        return self.price * self.quantity
