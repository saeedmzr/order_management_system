from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from apps.product.models import Product
from .models import Order, OrderItem


class OrderService:
    @staticmethod
    def validate_products_data(products_data):
        if not products_data:
            raise ValueError("At least one product is required")

        if not isinstance(products_data, list):
            raise ValueError("Products must be provided as a list")

    @staticmethod
    def process_product_item(item):
        try:
            product = item.get("product",{})
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

    @classmethod
    def update_order(cls,order,user,data):
        """
        Updates an order with proper permission checks
        Args:
            order: Order instance to update
            user: User making the request
            data: Dictionary containing update data (status, items)
        Returns:
            Updated order instance
        Raises:
            PermissionDenied: If user doesn't have permission
            ValueError: For invalid data
        """
        # Permission checks
        if not user.is_staff and order.customer != user:
            raise PermissionDenied("You can only update your own orders.")

        # Status update validation
        if 'status' in data:
            OrderService._validate_status_update(data['status'], user)
            order.status = data['status']

        with transaction.atomic():
            order.items.all().delete()
            total_price = 0
            for item_data in data['items']:
                try:
                    product = item_data['product']
                except Product.DoesNotExist:
                    raise ValueError(f"Product with ID {item_data['product_id']} does not exist")

                quantity = item_data['quantity']
                if quantity < 1:
                    raise ValueError("Quantity must be at least 1")

                price = product.price * quantity
                total_price += price

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

            order.total_price = total_price

            order.save()

        return order

    @staticmethod
    def _validate_status_update(new_status, user):
        """Validate status changes based on user permissions"""
        if new_status == 'COMPLETED' and not user.is_staff:
            raise PermissionDenied("Only admin can complete orders.")
