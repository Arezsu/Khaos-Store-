from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Product, Order, UserProfile

# ==================== PRODUCTOS ====================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'stock', 'is_on_sale', 'image_preview', 'created_at']
    list_display_links = ['id', 'name']
    list_filter = ['is_on_sale', 'category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['stock', 'is_on_sale']
    readonly_fields = ['created_at']
    list_per_page = 25
    ordering = ['-created_at']
    
    def image_preview(self, obj):
        """Muestra una miniatura de la imagen en el listado"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">Sin imagen</span>')
    image_preview.short_description = 'Imagen'

# ==================== ÓRDENES ====================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'product', 'total', 'status', 'created_at']
    list_display_links = ['order_number', 'customer_name']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email']
    list_editable = ['status']
    readonly_fields = ['order_number', 'created_at']
    list_per_page = 25
    ordering = ['-created_at']

# ==================== PERFILES ====================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'birth_date']
    list_display_links = ['user']
    search_fields = ['user__username', 'user__email', 'phone', 'city']
    list_per_page = 25
    ordering = ['user__username']

# ==================== USUARIOS ====================
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
    list_display_links = ['username', 'email']
    list_filter = ['is_staff', 'is_active', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_editable = ['is_active']
    list_per_page = 25
    ordering = ['-date_joined']
    actions = ['delete_selected']
    
    def delete_selected(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Se han eliminado {count} usuario(s) correctamente.')
    delete_selected.short_description = "Eliminar usuarios seleccionados"

# ==================== PERSONALIZACIÓN ====================
admin.site.site_header = 'Khaos Store - Panel de Administración'
admin.site.site_title = 'Khaos Store Admin'
admin.site.index_title = 'Bienvenido al Panel de Administración de Khaos Store'