from django.urls import path, include

urlpatterns = [
    path('users/', include(('apps.users.urls', 'users'))),
    path("products/",include(('apps.product.urls', 'product'))),
    path("orders/",include(('apps.order.urls', 'order'))),
]
