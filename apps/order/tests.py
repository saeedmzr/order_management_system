from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.order.models import Order, OrderItem
from apps.product.models import Product
from apps.users.models import User

class OrderModelTests(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create(
            name='لپ‌تاپ',
            price=15000000,
            description="test",
        )
        self.product2 = Product.objects.create(
            name='موبایل',
            price=8000000,
            description="test",
        )

        self.customer = User.objects.create_user(
            username='customer2',
            email="user@admin.com",
            password='testpass',
            is_admin=False
        )

    def test_create_order(self):
        order = Order.objects.create(customer=self.customer)
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            price=self.product1.price
        )
        OrderItem.objects.create(
            order=order,
            product=self.product2,
            quantity=1,
            price=self.product2.price
        )

        order.update_total_price()

        self.assertEqual(order.total_price, (15000000 * 2) + 8000000)
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.status, 'PENDING')

    def test_order_status_flow(self):
        order = Order.objects.create(customer=self.customer)
        order.status = 'PROCESSING'
        order.save()

        self.assertEqual(order.status, 'PROCESSING')


class OrderViewSetTests(APITestCase):
    def setUp(self):
        # Create products
        self.product1 = Product.objects.create(
            name='لپ‌تاپ',
            price=15000000,
            description="test",
        )
        self.product2 = Product.objects.create(
            name='موبایل',
            price=8000000,
            description="test",
        )
        # Create users
        self.admin = User.objects.create_user(
            username='admin3',
            email="admin@admin.com",
            password='testpass',
            is_admin=True
        )

        self.customer = User.objects.create_user(
            username='customer3',
            email="user1@admin.com",
            password='testpass',
            is_admin=False
        )
        self.other_customer = User.objects.create_user(
            username='customer4',
            email="user2@admin.com",
            password='testpass12',
            is_admin=False
        )

        # Create orders
        self.order = Order.objects.create(customer=self.customer)
        OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=1,
            price=self.product1.price
        )

    def test_order_create(self):
        self.client.force_authenticate(user=self.customer)
        url = "/api/orders/"
        data = {
            'items': [
                {'product_id': self.product1.id, 'quantity': 2},
                {'product_id': self.product2.id, 'quantity': 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(OrderItem.objects.count(), 3)

    def test_order_list_as_customer(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_order_list_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_order_update_by_owner(self):
        self.client.force_authenticate(user=self.customer)
        url = f'/api/orders/{self.order.id}/'
        data = {'status': 'CANCELLED'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_update_by_non_owner(self):
        self.client.force_authenticate(user=self.other_customer)
        url = f'/api/orders/{self.order.id}/'
        data = {
            'items': [
                {'product_id': self.product1.id, 'quantity': 5},
            ]
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_complete_by_customer(self):
        self.client.force_authenticate(user=self.customer)
        url = f'/api/orders/{self.order.id}/'
        data = {'status': 'COMPLETED'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
