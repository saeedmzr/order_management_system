# api/schema_serializers.py
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Order Creation Example',
            value={
                'items': [
                    {'product': 1, 'quantity': 2},
                    {'product': 3, 'quantity': 1}
                ]
            },
            request_only=True,
            response_only=False
        ),
        OpenApiExample(
            'Order Response Example',
            value={
                'id': 1,
                'customer': {
                    'id': 1,
                    'username': 'customer1',
                    'email': 'customer@example.com'
                },
                'status': 'Pending',
                'total_price': 99.99,
                'created_at': '2023-01-01T12:00:00Z',
                'updated_at': '2023-01-01T12:00:00Z',
                'items': [
                    {
                        'id': 1,
                        'product': {
                            'id': 1,
                            'name': 'Product 1',
                            'price': 49.99
                        },
                        'quantity': 2,
                        'price': 49.99
                    }
                ]
            },
            request_only=False,
            response_only=True
        )
    ]
)
class OrderSchemaSerializer(serializers.Serializer):
    pass