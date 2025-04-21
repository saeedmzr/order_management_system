from django.db import transaction
from products.models import Product
from .models import Order, OrderItem


class OrderCreationService:
    @staticmethod
    def validate_products_data(products_data):
        if not products_data:
            raise ValueError("At least one product is required")

        if not isinstance(products_data, list):
            raise ValueError("Products must be provided as a list")

    @staticmethod
    def process_product_item(item):
        try:
            product = Product.objects.get(pk=item['product_id'])
            quantity = int(item['quantity'])

            if quantity <= 0:
                raise ValueError(f"Invalid quantity for product {product.id}")

            return {
                'product': product,
                'quantity': quantity,
                'price': product.price,
                'item_price': product.price * quantity
            }
        except Product.DoesNotExist:
            raise ValueError(f"Product with ID {item['product_id']} not found")

    @classmethod
    def create_order(cls, user, products_data):
        cls.validate_products_data(products_data)

        with transaction.atomic():
            # Calculate total and prepare order items
            order_items = []
            total_price = 0

            for item in products_data:
                processed_item = cls.process_product_item(item)
                order_items.append(processed_item)
                total_price += processed_item['item_price']

            # Create order
            order = Order.objects.create(
                customer=user,
                total_price=total_price,
                status='pending'
            )

            # Create order items
            for item in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price']
                )

            return order