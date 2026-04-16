from django.db import models

class Item(models.Model):
    CURRENCY_CHOICES = (
        ('usd', 'USD'),
        ('eur', 'EUR'),
        ('rub', 'RUB'),
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField(help_text="Цена в минимальных единицах валюты (копейки/центы)")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='usd')
    
    def __str__(self):
        return f"{self.name} - {self.price} {self.currency.upper()}"
    
    def get_stripe_price_data(self):
        """Возвращает словарь price_data для Stripe Checkout Session."""
        return {
            'price_data': {
                'currency': self.currency,
                'product_data': {
                    'name': self.name,
                },
                'unit_amount': self.price,
            },
            'quantity': 1,
        }

class Discount(models.Model):
    """Модель скидки (купоны Stripe)"""
    name = models.CharField(max_length=100)
    stripe_coupon_id = models.CharField(max_length=100, unique=True)
    percent_off = models.PositiveIntegerField(blank=True, null=True)
    amount_off = models.PositiveIntegerField(blank=True, null=True)
    currency = models.CharField(max_length=3, choices=Item.CURRENCY_CHOICES, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Tax(models.Model):
    """Модель налога (Tax Rate в Stripe)"""
    name = models.CharField(max_length=100)
    stripe_tax_rate_id = models.CharField(max_length=100, unique=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    inclusive = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.percentage}%)"

class Order(models.Model):
    items = models.ManyToManyField(Item, through='OrderItem')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_total_price(self):
        """Общая стоимость всех товаров в заказе (без учёта скидки и налога)."""
        total = sum(item.price for item in self.items.all())
        return total
    
    def get_total_with_discount(self):
        total = self.get_total_price()
        if self.discount:
            if self.discount.percent_off:
                total = total * (100 - self.discount.percent_off) // 100
            elif self.discount.amount_off:
                total -= self.discount.amount_off
        return max(total, 0)
    
    def get_total_with_tax(self):
        total_with_discount = self.get_total_with_discount()
        if self.tax:
            total_with_tax = total_with_discount * (100 + self.tax.percentage) // 100
            return total_with_tax
        return total_with_discount
    
    def __str__(self):
        return f"Order {self.id} - Total: {self.get_total_with_tax()}"
    
    def get_line_items_for_stripe(self):
        """Формирует список line_items для Stripe Checkout Session."""
        line_items = []
        for order_item in self.orderitem_set.all():
            line_items.append(order_item.item.get_stripe_price_data())
        return line_items

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)