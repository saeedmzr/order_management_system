# orders/views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from .permissions import IsOrderOwnerOrAdmin
from .filters import OrderFilter


@extend_schema(tags=['Orders Endpoints'])
class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for orders with filtering, searching, and ordering.
    Accessible by authenticated users, with admin seeing all orders.
    """
    queryset = Order.objects.all()  # Default queryset (overridden in get_queryset)
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,    # For field filtering (using filterset_class)
        filters.SearchFilter,    # For search_fields
        filters.OrderingFilter,  # For ordering_fields
    ]
    filterset_class = OrderFilter  # Your custom filter class
    search_fields = ['status', 'customer__username']
    ordering_fields = ['created_at', 'total_price']

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=user)

    def get_permissions(self):
        """Apply stricter permissions for update/delete actions."""
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOrderOwnerOrAdmin]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Automatically assign the current user as the order customer."""
        serializer.save(customer=self.request.user)