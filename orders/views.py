from django.shortcuts import render, redirect
from django.contrib import messages
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from django.shortcuts import get_object_or_404
from .models import Order
from orders.tasks import order_created




def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()
            # launch asynchronous task
            order_created.delay(order.id)

            # ✅ Add message
            messages.success(request, f"✅ Your order #{order.id} has been placed successfully!")

            # ✅ Redirect to separate thank-you page
            return redirect('orders:order_created', order_id=order.id)
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})

def order_created_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order/created.html', {'order': order})
