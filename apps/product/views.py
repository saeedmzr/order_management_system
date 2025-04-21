# products/views.py
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets,filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Product
from .serializers import ProductSerializer
from ..base.permissions import IsAdminOrReadOnly


@extend_schema(tags=['Products Endpoints'])

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name',"description"]