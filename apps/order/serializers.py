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
        fields = ['product__name', 'quantity', 'price']
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

    def validate(self, data):
        request = self.context['request']
        order = self.instance
        user = request.user

        # Users can only update their own orders
        if not user.is_staff and order.customer != user:
            raise serializers.ValidationError("You can only update your own orders.")

        # Only admin can change status to COMPLETED
        if 'status' in data and data['status'] == 'COMPLETED' and not user.is_staff:
            raise serializers.ValidationError("Only admin can complete orders.")

        return data

    def update(self, instance, validated_data):
        request = self.context['request']
        items_data = validated_data.pop('items', None)

        # Update status if provided
        if 'status' in validated_data:
            instance.status = validated_data['status']

        # Update items if provided
        if items_data is not None:
            # Clear existing items
            instance.items.all().delete()

            # Create new items
            total_price = 0
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                price = product.price * quantity
                total_price += price

                OrderItem.objects.create(
                    order=instance,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

            instance.total_price = total_price

        instance.save()
        return instance