import stripe
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Item, Order, Discount, Tax

def get_stripe_api_key(currency):
    """Возвращает секретный ключ Stripe для заданной валюты."""
    return settings.STRIPE_KEYS.get(currency, {}).get('secret')

def item_detail(request, id):
    """Страница товара с кнопкой Buy."""
    item = get_object_or_404(Item, id=id)
    public_key = settings.STRIPE_KEYS.get(item.currency, {}).get('public')
    return render(request, 'stripe_app/item_detail.html', {
        'item': item,
        'stripe_public_key': public_key,
    })

def buy_item(request, id):
    """Создаёт Stripe Checkout Session для товара и возвращает session.id."""
    item = get_object_or_404(Item, id=id)
    stripe.api_key = get_stripe_api_key(item.currency)
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[item.get_stripe_price_data()],
        mode='payment',
        success_url=request.build_absolute_uri('/success/'),
        cancel_url=request.build_absolute_uri('/cancel/'),
    )
    return JsonResponse({'id': session.id})

def order_detail(request, id):
    """Страница заказа с кнопкой Buy."""
    order = get_object_or_404(Order, id=id)
    # Предположим, что все товары в заказе имеют одинаковую валюту
    currency = order.items.first().currency if order.items.exists() else 'usd'
    public_key = settings.STRIPE_KEYS.get(currency, {}).get('public')
    return render(request, 'stripe_app/order_detail.html', {
        'order': order,
        'stripe_public_key': public_key,
    })

def buy_order(request, id):
    """Создаёт Stripe Checkout Session для заказа с учётом скидок и налогов."""
    order = get_object_or_404(Order, id=id)
    if not order.items.exists():
        return JsonResponse({'error': 'Order has no items'}, status=400)
    
    currency = order.items.first().currency
    stripe.api_key = get_stripe_api_key(currency)
    
    line_items = order.get_line_items_for_stripe()
    
    session_params = {
        'payment_method_types': ['card'],
        'line_items': line_items,
        'mode': 'payment',
        'success_url': request.build_absolute_uri('/success/'),
        'cancel_url': request.build_absolute_uri('/cancel/'),
    }
    
    # Добавляем скидку, если есть
    if order.discount and order.discount.stripe_coupon_id:
        session_params['discounts'] = [{'coupon': order.discount.stripe_coupon_id}]
    
    # Добавляем налог, если есть
    if order.tax and order.tax.stripe_tax_rate_id:
        session_params['tax_rates'] = [order.tax.stripe_tax_rate_id]
    
    session = stripe.checkout.Session.create(**session_params)
    return JsonResponse({'id': session.id})