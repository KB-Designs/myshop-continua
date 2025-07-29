from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
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

            # Optionally send email/task
            order_created.delay(order.id)

            # Handle M-Pesa redirect
            if order.payment_method == 'mpesa':
                request.session['mpesa_order_id'] = order.id
                request.session['mpesa_phone'] = order.phone
                return redirect('mpesa:stk_push')

            messages.success(request, f"✅ Your order #{order.id} has been placed successfully!")
            return redirect('orders:order_created', order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, 'orders/order/create.html', {
        'form': form,
        'cart': cart,
    })


def order_created_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order/created.html', {'order': order})


@require_GET
def load_pickup_stations(request):
    county = request.GET.get('county')
    pickup_options = {
        'Nairobi': ['CBD', 'Westlands'],
        'Mombasa': ['Nyali', 'Likoni'],
        'Kisumu': ['Milimani', 'Kondele'],
    }
    stations = pickup_options.get(county, [])
    return JsonResponse({'stations': stations})

def order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_created.html', {'order': order})