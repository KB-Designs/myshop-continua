from django.db import models
from shop.models import Product

# Choices for payment method
PAYMENT_METHOD_CHOICES = [
    ('mpesa', 'Lipa na M-Pesa'),
    ('cod', 'Cash on Delivery'),
]

# Choices for county
COUNTY_CHOICES = [
    ('Nairobi', 'Nairobi'),
    ('Mombasa', 'Mombasa'),
    ('Kisumu', 'Kisumu'),
    # Add more counties as needed
]

# Optional mapping to use in forms.py
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
    pickup_station = models.CharField(max_length=100)  # Set dynamically in the form
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
