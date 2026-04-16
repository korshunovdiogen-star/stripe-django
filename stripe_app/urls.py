from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('item/<int:id>/', views.item_detail, name='item_detail'),
    path('buy/<int:id>/', views.buy_item, name='buy_item'),
    path('order/<int:id>/', views.order_detail, name='order_detail'),
    path('buy/order/<int:id>/', views.buy_order, name='buy_order'),
    path('create-payment-intent/<int:id>/', views.create_payment_intent, name='create_payment_intent'),
    path('payment-success/', TemplateView.as_view(template_name='stripe_app/payment_success.html'), name='payment_success'),
    path('create-order-payment-intent/<int:id>/', views.create_order_payment_intent, name='create_order_payment_intent'),
]