from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from .models import Order, OrderItem

class OrderService:
    @classmethod
    def create_order(cls, user, products_data):
        """
        Simplified create_order that just passes data to the serializer
        """
        serializer = OrderCreateSerializer(
            data={'items': products_data},
            context={'request': user}
        )
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @classmethod
    def update_order(cls, order, user, data):
        """
        Simplified update_order that just passes data to the serializer
        """
        serializer = OrderUpdateSerializer(
            order,
            data=data,
            partial=True,
            context={'request': user}
        )
        serializer.is_valid(raise_exception=True)
        return serializer.save()