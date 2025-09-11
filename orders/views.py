from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from orders.tasks import order_created
from .models import Order


@login_required  # ⬅ blocks anonymous users
def order_create(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            # Attach the logged-in user
            order.user = request.user  

            # Handle coupon if applied
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount

            order.save()    

            # Save order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )

            # Clear cart and coupon session
            cart.clear()
            if 'coupon_id' in request.session:
                del request.session['coupon_id']

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

def thank_you(request, order_id):
    order = get_object_or_404(Order, id=order_id, paid=True)
    return render(request, 'orders/thank_you.html', {'order': order})