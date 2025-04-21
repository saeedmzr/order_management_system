# orders/views.py
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import viewsets, filters, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer, OrderCreateSerializer, OrderUpdateSerializer
from .permissions import IsOrderOwnerOrAdmin
from .filters import OrderFilter
from .services import  OrderService
from ..base.responses import Response
from ..product.models import Product


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
        if user.is_admin:
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
    @extend_schema(
        request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                'Order Creation Example',
                value={
                    'products': [
                        {'product_id': 1, 'quantity': 2},
                        {'product_id': 3, 'quantity': 1}
                    ]
                }
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new order with multiple products.
        Expected payload format:
        {
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 3, "quantity": 1}
            ]
        }
        """
        try:
            serialized_data = OrderCreateSerializer(data=request.data)
            serialized_data.is_valid(raise_exception=True)

            order = OrderService.create_order(
                user=request.user,
                products_data=serialized_data.validated_data.get("items",[]))

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Product.DoesNotExist:
            return Response({'error': 'Invalid product ID'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {'error': 'Order creation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = OrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_order = OrderService.update_order(
                order=order,
                user=request.user,
                data=serializer.validated_data
            )

            # Return the updated order
            return Response({
                'status': updated_order.status,
                'total_price': updated_order.total_price,
                'message': 'Order updated successfully'
            }, status=status.HTTP_200_OK)

        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({'error': 'Invalid product ID'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)