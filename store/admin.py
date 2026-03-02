from django.contrib import admin
from .models import Product, Order, UserProfile

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'is_on_sale', 'created_at']
    list_filter = ['is_on_sale', 'category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['stock', 'is_on_sale']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'price', 'image', 'description')
        }),
        ('Inventario', {
            'fields': ('stock', 'is_on_sale', 'sale_price')
        }),
        ('Clasificación', {
            'fields': ('category', 'rating', 'reviews_count')
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'product', 'total', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email']
    list_editable = ['status']
    readonly_fields = ['order_number', 'created_at']
    fieldsets = (
        ('Información de la Orden', {
            'fields': ('order_number', 'product', 'status', 'total')
        }),
        ('Cliente', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Envío', {
            'fields': ('address', 'city')
        }),
        ('Pago', {
            'fields': ('payment_method', 'user')
        }),
        ('Fechas', {
            'fields': ('created_at',)
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city']
    search_fields = ['user__username', 'user__email', 'phone']
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información de Contacto', {
            'fields': ('phone', 'address', 'city')
        }),
        ('Preferencias', {
            'fields': ('favorite_games',)
        }),
    )