from django.db import models

from apps.base.models import BaseModel
from apps.product.models import Product
from apps.users.models import User


class Order(BaseModel):
    ORDER_STATUS = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default='PENDING')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"

    def update_total_price(self):
        self.total_price = sum(item.price * item.quantity for item in self.items.all())
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} for order #{self.order.id}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.price = self.product.price
        super().save(*args, **kwargs)
        self.order.update_total_price()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.order.update_total_price()