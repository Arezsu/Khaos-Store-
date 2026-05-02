from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Product, Order, UserProfile, Cart, CartItem, Review


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
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'description', 'price', 'category')
        }),
        ('Imagen y video', {
            'fields': ('image', 'trailer_url', 'video_file'),
            'classes': ('collapse',)
        }),
        ('Inventario', {
            'fields': ('stock', 'is_on_sale', 'sale_price')
        }),
        ('Calificaciones', {
            'fields': ('rating', 'reviews_count'),
            'classes': ('collapse',)
        }),
    )


# ==================== CARRITO ====================
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['get_total']
    
    def get_total(self, obj):
        return f"${obj.get_total()}"
    get_total.short_description = "Subtotal"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'get_total', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']
    inlines = [CartItemInline]
    readonly_fields = ['get_total', 'get_total_items']
    
    def get_total(self, obj):
        return f"${obj.get_total()}"
    get_total.short_description = "Total"
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = "Items"


# ==================== ÓRDENES ====================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'product', 'total', 'status', 'created_at']
    list_display_links = ['order_number', 'customer_name']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email']
    list_editable = ['status']
    readonly_fields = ['order_number', 'created_at']
    ordering = ['-created_at']
    fieldsets = (
        ('Información del pedido', {
            'fields': ('order_number', 'user', 'product', 'cart', 'status')
        }),
        ('Datos del cliente', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Envío', {
            'fields': ('address', 'city')
        }),
        ('Pago', {
            'fields': ('payment_method', 'total')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ==================== RESEÑAS ====================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'comment_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = "Comentario"


# ==================== PERFILES ====================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'birth_date']
    search_fields = ['user__username', 'user__email', 'phone']


# ==================== USUARIOS ====================
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    list_editable = ['is_active']


# ==================== PERSONALIZACIÓN ====================
admin.site.site_header = 'Khaos Store Admin'
admin.site.site_title = 'Khaos Store'
admin.site.index_title = 'Panel de Administración'