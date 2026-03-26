from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Product, Order, UserProfile
from .email_utils import send_order_status_email

# ==================== PRODUCTOS ====================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'stock', 'is_on_sale', 'created_at']
    list_display_links = ['id', 'name']
    list_filter = ['is_on_sale', 'category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['stock', 'is_on_sale']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


# ==================== ÓRDENES ====================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'product', 'total', 'status_colored', 'created_at']
    list_display_links = ['order_number', 'customer_name']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email']
    list_editable = ['status']
    readonly_fields = ['order_number', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información de la Orden', {
            'fields': ('order_number', 'product', 'status', 'total')
        }),
        ('Datos del Cliente', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Datos de la Cuenta (solo para SENT)', {
            'fields': ('account_email', 'account_password', 'account_instructions'),
            'classes': ('collapse',),
            'description': 'Completa estos campos cuando la orden esté en estado ENVIADO'
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def status_colored(self, obj):
        colors = {
            'PENDING': '#ffaa00',
            'PAID': '#00ff00',
            'SENT': '#0070f3',
            'DELIVERED': '#00ff00',
            'CANCELLED': '#ff0000',
        }
        color = colors.get(obj.status, '#ffffff')
        status_display = dict(Order.STATUS).get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: #000; padding: 5px 10px; border-radius: 15px; font-size: 12px;">{}</span>',
            color, status_display
        )
    status_colored.short_description = 'Estado'
    
    def save_model(self, request, obj, form, change):
        """Guarda la orden y envía email si el estado cambió"""
        if change:
            original = Order.objects.get(pk=obj.pk)
            old_status = original.status
            new_status = obj.status
            
            # Guardar primero
            super().save_model(request, obj, form, change)
            
            # Enviar email solo si el estado cambió
            if old_status != new_status:
                send_order_status_email(obj, old_status)
                self.message_user(request, f'Email de estado "{new_status}" enviado a {obj.customer_email}')
        else:
            super().save_model(request, obj, form, change)


# ==================== PERFILES ====================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city']
    search_fields = ['user__username', 'user__email', 'phone']


# ==================== USUARIOS ====================
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    list_editable = ['is_active']
    actions = ['delete_selected']

# ==================== PERSONALIZACIÓN ====================
admin.site.site_header = 'Khaos Store Admin'
admin.site.site_title = 'Khaos Store'
admin.site.index_title = 'Panel de Administración'