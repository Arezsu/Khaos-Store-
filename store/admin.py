from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, UserProfile

# ==================== PRODUCTOS ====================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Listado
    list_display = ['id', 'name', 'price_display', 'stock', 'is_on_sale', 'image_preview', 'created_at']
    list_display_links = ['id', 'name']
    list_filter = ['is_on_sale', 'category', 'created_at', 'stock']
    search_fields = ['name', 'description', 'category']
    list_editable = ['stock', 'is_on_sale']
    readonly_fields = ['created_at']
    list_per_page = 25
    ordering = ['-created_at']
    sortable_by = ['name', 'price', 'stock', 'created_at']
    
    # Campos agrupados
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'price', 'image', 'description'),
        }),
        ('Inventario y Precios', {
            'fields': ('stock', 'is_on_sale', 'sale_price'),
        }),
        ('Clasificación', {
            'fields': ('category', 'rating', 'reviews_count'),
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    # Métodos personalizados
    def price_display(self, obj):
        if obj.is_on_sale and obj.sale_price:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">${}</span> '
                '<span style="color: #00ff00; font-weight: bold;">${}</span>',
                obj.price, obj.sale_price
            )
        return format_html('<span style="color: #ff00ff;">${}</span>', obj.price)
    price_display.short_description = 'Precio'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">Sin imagen</span>')
    image_preview.short_description = 'Imagen'
    
    # Acciones masivas
    actions = ['mark_as_on_sale', 'remove_from_sale', 'increase_stock']
    
    def mark_as_on_sale(self, request, queryset):
        updated = queryset.update(is_on_sale=True)
        self.message_user(request, f'{updated} producto(s) marcado(s) como en oferta.')
    mark_as_on_sale.short_description = 'Marcar como en oferta'
    
    def remove_from_sale(self, request, queryset):
        updated = queryset.update(is_on_sale=False)
        self.message_user(request, f'{updated} producto(s) ya no están en oferta.')
    remove_from_sale.short_description = 'Quitar oferta'
    
    def increase_stock(self, request, queryset):
        for product in queryset:
            product.stock += 10
            product.save()
        self.message_user(request, f'Stock aumentado para {queryset.count()} producto(s).')
    increase_stock.short_description = 'Aumentar stock +10'


# ==================== ÓRDENES ====================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Listado
    list_display = ['order_number', 'customer_name', 'product', 'total_display', 'status_badge', 'payment_method', 'created_at']
    list_display_links = ['order_number', 'customer_name']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'customer_phone']
    list_editable = ['status']
    readonly_fields = ['order_number', 'created_at']
    list_per_page = 25
    ordering = ['-created_at']
    
    # Campos agrupados
    fieldsets = (
        ('Información de la Orden', {
            'fields': ('order_number', 'product', 'status', 'total'),
        }),
        ('Datos del Cliente', {
            'fields': ('customer_name', 'customer_email', 'customer_phone'),
        }),
        ('Envío', {
            'fields': ('address', 'city'),
        }),
        ('Pago', {
            'fields': ('payment_method', 'user'),
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    # Métodos personalizados
    def total_display(self, obj):
        return format_html('<span style="color: #00ff00; font-weight: bold;">${}</span>', obj.total)
    total_display.short_description = 'Total'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#ffaa00',
            'PAID': '#00ff00',
            'SENT': '#00ffff',
            'DELIVERED': '#ff00ff',
            'CANCELLED': '#ff0000',
        }
        color = colors.get(obj.status, '#ffffff')
        return format_html(
            '<span style="background-color: {}; color: #000; padding: 3px 10px; border-radius: 15px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    # Acciones masivas
    actions = ['mark_as_paid', 'mark_as_sent', 'mark_as_delivered']
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='PAID')
        self.message_user(request, f'{updated} orden(es) marcada(s) como pagadas.')
    mark_as_paid.short_description = 'Marcar como pagado'
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(status='SENT')
        self.message_user(request, f'{updated} orden(es) marcada(s) como enviadas.')
    mark_as_sent.short_description = 'Marcar como enviado'
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='DELIVERED')
        self.message_user(request, f'{updated} orden(es) marcada(s) como entregadas.')
    mark_as_delivered.short_description = 'Marcar como entregado'


# ==================== PERFILES ====================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Listado
    list_display = ['user', 'phone', 'city', 'favorite_games_count', 'birth_date', 'is_adult_badge']
    list_display_links = ['user']
    list_filter = ['city', 'birth_date']
    search_fields = ['user__username', 'user__email', 'phone', 'city']
    list_per_page = 25
    ordering = ['user__username']
    
    # Campos agrupados
    fieldsets = (
        ('Usuario', {
            'fields': ('user',),
        }),
        ('Información de Contacto', {
            'fields': ('phone', 'address', 'city'),
        }),
        ('Datos Personales', {
            'fields': ('birth_date',),
        }),
        ('Preferencias', {
            'fields': ('favorite_games',),
        }),
    )
    
    # Métodos personalizados
    def favorite_games_count(self, obj):
        count = obj.favorite_games.count()
        return format_html('<span style="color: #ff00ff;">{}</span>', count)
    favorite_games_count.short_description = 'Favoritos'
    
    def is_adult_badge(self, obj):
        if obj.is_adult():
            return format_html('<span style="background-color: #00ff00; color: #000; padding: 3px 10px; border-radius: 15px;">Mayor de edad</span>')
        return format_html('<span style="background-color: #ffaa00; color: #000; padding: 3px 10px; border-radius: 15px;">Menor de edad</span>')
    is_adult_badge.short_description = 'Edad'
    
    # Acciones masivas
    actions = ['send_welcome_message']
    
    def send_welcome_message(self, request, queryset):
        for profile in queryset:
            print(f"Enviando mensaje de bienvenida a {profile.user.email}")
        self.message_user(request, f'Mensaje enviado a {queryset.count()} usuario(s).')
    send_welcome_message.short_description = 'Enviar mensaje de bienvenida'


# ==================== PERSONALIZACIÓN DEL PANEL ====================
admin.site.site_header = 'Khaos Store - Panel de Administración'
admin.site.site_title = 'Khaos Store Admin'
admin.site.index_title = 'Bienvenido al Panel de Administración de Khaos Store'