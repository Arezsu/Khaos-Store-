from django.urls import path
from . import api_views

urlpatterns = [
    path('products/', api_views.get_products, name='api_products'),
    path('products/<int:product_id>/', api_views.get_product_detail, name='api_product_detail'),
    path('register/', api_views.register_user, name='api_register'),
    path('orders/', api_views.create_order, name='api_create_order'),
]