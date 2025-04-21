# orders/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderFilterView

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='orders')

urlpatterns = [
    path('filter/', OrderFilterView.as_view(), name='order-filter'),
] + router.urls