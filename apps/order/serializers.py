# orders/serializers.py
from django.db import transaction
from rest_framework.exceptions import ValidationError
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
        fields = ['product', 'product_id', 'quantity', 'price']
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

    def validate(self, data):
        product = data['product']
        quantity = data['quantity']

        if quantity <= 0:
            raise ValidationError("Quantity must be at least 1")

        if product.quantity < quantity:
            raise ValidationError(
                f"Not enough stock. Only {product.quantity} available"
            )

        return data

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        product = data['product']
        quantity = data['quantity']

        data['price'] = product.price
        data['item_price'] = product.price * quantity
        return data


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

    def validate_items(self, value):
        if not value or len(value) == 0:
            raise ValidationError("At least one product is required")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        with transaction.atomic():
            # Validate all items first
            products_to_update = []
            order_items_to_create = []

            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']

                if product.quantity < quantity:
                    raise ValidationError(
                        f"Not enough stock for product {product.id}. "
                        f"Available: {product.quantity}, Requested: {quantity}"
                    )

                # Prepare product quantity update
                product.quantity -= quantity
                products_to_update.append(product)

                # Prepare order item creation
                order_items_to_create.append(OrderItem(
                    product=product,
                    quantity=quantity,
                    price=item_data['price']
                ))

            # Calculate total price
            total_price = sum(item['item_price'] for item in items_data)

            # Create the order
            order = Order.objects.create(
                customer=user,
                total_price=total_price,
                status='pending'
            )

            # Bulk update product quantities
            Product.objects.bulk_update(products_to_update, ['quantity'])

            # Set order for all items and bulk create
            for item in order_items_to_create:
                item.order = order
            OrderItem.objects.bulk_create(order_items_to_create)

        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, required=False)
    status = serializers.ChoiceField(choices=Order.ORDER_STATUS, required=False)

    class Meta:
        model = Order
        fields = ['status', 'items']
        read_only_fields = ['customer']

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        user = self.context['request'].user

        with transaction.atomic():
            if items_data is not None:
                # Prepare data for bulk operations
                products_to_update = []
                new_order_items = []

                # First return quantities of old items
                old_items = list(instance.items.select_related('product').all())
                for old_item in old_items:
                    product = old_item.product
                    product.quantity += old_item.quantity
                    products_to_update.append(product)

                # Validate new items
                for item_data in items_data:
                    product = item_data['product']
                    quantity = item_data['quantity']

                    if product.quantity < quantity:
                        raise ValidationError(
                            f"Not enough stock for product {product.id}. "
                            f"Available: {product.quantity}, Requested: {quantity}"
                        )

                    # Prepare product quantity update
                    product.quantity -= quantity
                    products_to_update.append(product)

                    # Prepare new order item
                    new_order_items.append(OrderItem(
                        order=instance,
                        product=product,
                        quantity=quantity,
                        price=item_data['price']
                    ))

                # Calculate new total price
                total_price = sum(item['item_price'] for item in items_data)
                instance.total_price = total_price

                # Perform bulk operations
                Product.objects.bulk_update(products_to_update, ['quantity'])
                instance.items.all().delete()
                OrderItem.objects.bulk_create(new_order_items)

            if 'status' in validated_data:
                if not user.is_admin:
                    raise PermissionDenied("Only admin can update order status")
                instance.status = validated_data['status']

        instance.save()
        return instance