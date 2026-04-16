from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def success_view(request):
    return HttpResponse("<h1>Payment Successful!</h1><p>Thank you for your purchase.</p>")

def cancel_view(request):
    return HttpResponse("<h1>Payment Cancelled</h1><p>You have cancelled the payment.</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('success/', success_view, name='success'),
    path('cancel/', cancel_view, name='cancel'),
    path('', include('stripe_app.urls')),
]