from django.contrib import admin
from .models import Item, Discount, Tax, Order, OrderItem

admin.site.register(Item)
admin.site.register(Discount)
admin.site.register(Tax)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'get_total_price', 'discount', 'tax', 'created_at')