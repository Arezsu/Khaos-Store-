from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Product, Order, UserProfile
from .email_utils import send_order_status_email

# ==================== PRODUCTOS ====================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'stock', 'is_active', 'created_at']
    list_display_links = ['name']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category']
    list_editable = ['price', 'stock', 'is_active']
    list_per_page = 25
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Precio y Stock', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Imágenes', {
            'fields': ('image', 'image_url'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from django.utils.text import slugify
            obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)


# ==================== ÓRDENES ====================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'product', 'total', 'status', 'status_colored', 'created_at']
    list_display_links = ['order_number', 'customer_name']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'product__name']
    list_editable = ['status']
    readonly_fields = ['order_number', 'created_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('Información de la Orden', {
            'fields': ('order_number', 'product', 'quantity', 'status', 'total')
        }),
        ('Datos del Cliente', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Datos de la Cuenta (solo para SENT)', {
            'fields': ('account_email', 'account_password', 'account_instructions'),
            'classes': ('collapse',),
            'description': 'Completa estos campos cuando la orden esté en estado ENVIADO'
        }),
        ('Información de Pago', {
            'fields': ('payment_method', 'payment_status', 'payment_id'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def status_colored(self, obj):
        colors = {
            'PENDING': '#ffaa00',
            'PAID': '#28a745',
            'SENT': '#0070f3',
            'DELIVERED': '#17a2b8',
            'CANCELLED': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        status_display = dict(Order.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-block;">{}</span>',
            color, status_display
        )
    status_colored.short_description = 'Estado (color)'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')
    
    def save_model(self, request, obj, form, change):
        if change:
            try:
                original = Order.objects.get(pk=obj.pk)
                old_status = original.status
                new_status = obj.status
                
                super().save_model(request, obj, form, change)
                
                if old_status != new_status:
                    success = send_order_status_email(obj, old_status)
                    if success:
                        self.message_user(
                            request,
                            f'✓ Email de estado "{new_status}" enviado correctamente a {obj.customer_email}',
                            level='SUCCESS'
                        )
                    else:
                        self.message_user(
                            request,
                            f'⚠️ Orden guardada pero hubo un error al enviar el email a {obj.customer_email}',
                            level='WARNING'
                        )
            except Order.DoesNotExist:
                super().save_model(request, obj, form, change)
        else:
            super().save_model(request, obj, form, change)
            self.message_user(
                request,
                f'✓ Nueva orden #{obj.order_number} creada correctamente',
                level='SUCCESS'
            )
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.status in ['PAID', 'SENT', 'DELIVERED']:
            return False
        return super().has_delete_permission(request, obj)


# ==================== PERFILES DE USUARIO ====================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'get_user_email']
    list_display_links = ['user']
    search_fields = ['user__username', 'user__email', 'phone', 'city']
    list_filter = ['city']
    raw_id_fields = ['user']
    list_per_page = 25
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    get_user_email.admin_order_field = 'user__email'
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información de Contacto', {
            'fields': ('phone', 'city', 'address')
        }),
        ('Información Adicional', {
            'fields': ('birth_date', 'avatar'),
            'classes': ('collapse',)
        }),
    )


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
    
    actions = ['activate_users', 'deactivate_users', 'make_staff']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} usuarios activados.")
    activate_users.short_description = "Activar usuarios seleccionados"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} usuarios desactivados.")
    deactivate_users.short_description = "Desactivar usuarios seleccionados"
    
    def make_staff(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(request, f"{updated} usuarios promovidos a staff.")
    make_staff.short_description = "Promover a staff"
    
    # Usamos los fieldsets originales de UserAdmin para evitar duplicados
    fieldsets = UserAdmin.fieldsets

# ==================== PERSONALIZACIÓN ====================
admin.site.site_header = 'Khaos Store Admin'
admin.site.site_title = 'Khaos Store'
admin.site.index_title = 'Panel de Administración'
admin.site.site_url = '/'