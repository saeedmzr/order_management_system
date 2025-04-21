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

        self.list_url = '/api/orders/'
        self.detail_url = f'/api/orders/{self.order.id}/'
    def test_order_create(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            'items': [
                {'product_id': self.product1.id, 'quantity': 2},
                {'product_id': self.product2.id, 'quantity': 1}
            ]
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(OrderItem.objects.count(), 3)


    # --- CREATE TESTS ---
    def test_order_create_as_customer(self):
        """Customer should be able to create orders"""
        self.client.force_authenticate(user=self.customer)
        data = {
            'items': [
                {'product_id': self.product1.id, 'quantity': 2},
                {'product_id': self.product2.id, 'quantity': 1}
            ]
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(OrderItem.objects.count(), 3)

    def test_order_create_as_admin(self):
        """Admin should be able to create orders"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'items': [
                {'product_id': self.product1.id, 'quantity': 1}
            ]
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_order_create_unauthenticated(self):
        """Unauthenticated users should not be able to create orders"""
        data = {
            'items': [
                {'product_id': self.product1.id, 'quantity': 1}
            ]
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- LIST TESTS ---
    def test_order_list_as_customer(self):
        """Customer should only see their own orders"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['customer']['username'], self.customer.username)

    def test_order_list_as_admin(self):
        """Admin should see all orders"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_order_list_unauthenticated(self):
        """Unauthenticated users should not see any orders"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- RETRIEVE TESTS ---
    def test_order_retrieve_as_owner(self):
        """Order owner should be able to view their order"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)

    def test_order_retrieve_as_admin(self):
        """Admin should be able to view any order"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_retrieve_as_non_owner(self):
        """Non-owner customers should not see others' orders"""
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- UPDATE TESTS ---

    def test_order_update_as_admin(self):
        """Admin should be able to update any order"""
        self.client.force_authenticate(user=self.admin)
        data = {'status': 'PROCESSING'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'PROCESSING')

    def test_order_update_as_non_owner(self):
        """Non-owner customers should not update others' orders"""
        self.client.force_authenticate(user=self.other_customer)
        data = {'status': 'CANCELLED'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- DELETE TESTS ---
    def test_order_delete_as_owner(self):
        """Order owner should be able to delete their order"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

    def test_order_delete_as_admin(self):
        """Admin should be able to delete any order"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_order_delete_as_non_owner(self):
        """Non-owner customers should not delete others' orders"""
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Order.objects.count(), 1)

    # --- EDGE CASES ---

    def test_order_update_with_invalid_status(self):
        """Should fail when trying to set invalid status"""
        self.client.force_authenticate(user=self.admin)
        data = {'status': 'INVALID_STATUS'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
