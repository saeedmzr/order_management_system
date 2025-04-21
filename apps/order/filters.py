# orders/filters.py
import django_filters
from .models import Order
from django.db.models import Q


class OrderFilter(django_filters.FilterSet):
    date_range = django_filters.DateFromToRangeFilter(field_name='created_at')
    min_price = django_filters.NumberFilter(field_name='total_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='total_price', lookup_expr='lte')
    status = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Order
        fields = ['status', 'created_at', 'total_price']