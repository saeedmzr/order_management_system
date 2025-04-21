from django.test import TestCase
from apps.product.models import Product
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from apps.users.models import User


class ProductModelTests(TestCase):

    def test_create_product(self):
        simple_product_name = "product test"
        simple_product_description = "product test description"
        product = Product.objects.create(
            name=simple_product_name,
            description='product description 1',
            price=15000000
        )
        self.assertEqual(product.name, simple_product_name)
        self.assertEqual(product.price, 15000000)


class ProductViewSetTests(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='product test',
            description='product test description',
            price=15000000,
        )

        # Create users with different roles
        self.admin = User.objects.create_superuser(
            username='admin1',
            email="admin@admin.com",
            password='adminpass',
            is_admin=True
        )

        self.customer = User.objects.create_user(
            username='customer1',
            email="user@admin.com",
            password='customerpass',
            is_admin=False
        )

    def test_product_list(self):
        url = "/api/products/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_product_create_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = "/api/products/"
        data = {
            'name': 'موبایل',
            'price': 8000000,
            'description': "product test description"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_product_create_as_customer(self):
        self.client.force_authenticate(user=self.customer)
        url = "/api/products/"
        data = {
            'name': 'موبایل',
            'price': 8000000,
            'description': "product test description"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)