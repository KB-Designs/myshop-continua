from django.shortcuts import get_object_or_404, render, get_list_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm
from django.db.models import Q, Count
from orders.models import OrderItem
 

def product_list(request, category_slug=None):
    category=None
    categories=Category.objects.all()
    products=Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products=products.filter(category=category)
    return render(request, 
                  'shop/product/list.html',
                  {'category':category,
                   'categories':categories,
                   'products':products})

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()

    # Related products (same category, excluding current product)
    related_products = (
        Product.objects.filter(category=product.category, available=True)
        .exclude(id=product.id)[:4]
    )

    # Frequently bought together
    order_items = OrderItem.objects.filter(product=product)
    product_ids = (
        OrderItem.objects
        .filter(order__in=[item.order for item in order_items])
        .exclude(product=product)
        .values('product')
        .annotate(count=Count('product'))
        .order_by('-count')[:4]
    )
    frequently_bought = Product.objects.filter(id__in=[p['product'] for p in product_ids])

    return render(
        request,
        'shop/product/detail.html',
        {
            'product': product,
            'cart_product_form': cart_product_form,
            'related_products': related_products,
            'frequently_bought': frequently_bought,
        },
    )

def product_search(request):
    query = request.GET.get('q')
    results= []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query), available=True)

    return render(request,
                  'shop/product_search.html',
                  {'query': query,
                   'results': results})