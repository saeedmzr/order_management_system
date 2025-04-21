# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem

from ..product.models import Product
from ..product.serializers import ProductSerializer
from ..users.serializers import UserSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['product','product_id', 'quantity', 'price']
        read_only_fields = ['price']


class OrderItemCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = UserSerializer(read_only=True)
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'status', 'total_price',
            'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['customer', 'total_price', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ['items']

class OrderUpdateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ['status', 'items']
        read_only_fields = ['customer']
