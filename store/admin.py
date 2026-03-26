from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
import os
import random
import string
from datetime import datetime
from .models import Product, Order, UserProfile


# Función para generar clave de juego
def generate_game_key():
    """Genera una clave de juego estilo PSN"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


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
    list_display = ['order_number', 'customer_name', 'product', 'total', 'status', 'created_at', 'email_draft_status']
    list_display_links = ['order_number', 'customer_name']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email']
    list_editable = ['status']
    readonly_fields = ['order_number', 'created_at']
    ordering = ['-created_at']
    
    def email_draft_status(self, obj):
        """Muestra si se generó el borrador del email"""
        draft_path = os.path.join(settings.BASE_DIR, 'borradores_correos', f'orden_{obj.order_number}.html')
        if os.path.exists(draft_path):
            return '✅ Borrador listo'
        return '⏳ No generado'
    email_draft_status.short_description = 'Borrador Email'
    email_draft_status.allow_tags = True
    
    def save_model(self, request, obj, form, change):
        """Sobrescribimos save_model para detectar cambio de estado"""
        old_status = None
        if change:
            # Obtener el estado anterior
            try:
                old_obj = Order.objects.get(pk=obj.pk)
                old_status = old_obj.status
            except Order.DoesNotExist:
                pass
        
        # Guardar el objeto
        super().save_model(request, obj, form, change)
        
        # Verificar si el estado cambió a 'PAID' (Pagado)
        if change and old_status != 'PAID' and obj.status == 'PAID':
            self.generate_email_draft(obj, request)
    
    def generate_email_draft(self, order, request):
        """Genera un archivo HTML del correo con estilo PlayStation"""
        try:
            # Generar clave de juego única
            game_key = generate_game_key()
            
            # Renderizar la plantilla HTML
            html_content = render_to_string('store/email_paid_draft.html', {
                'order': order,
                'game_key': game_key,
            })
            
            # Crear directorio si no existe
            drafts_dir = os.path.join(settings.BASE_DIR, 'borradores_correos')
            os.makedirs(drafts_dir, exist_ok=True)
            
            # Crear nombre de archivo
            filename = f"orden_{order.order_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(drafts_dir, filename)
            
            # Guardar el archivo HTML
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Mensaje de éxito con instrucciones
            self.message_user(
                request,
                f"""
✅ ¡BORRADOR DE CORREO GENERADO!

📁 Archivo: {filepath}
📧 Destinatario: {order.customer_email}
👤 Cliente: {order.customer_name}
🎮 Juego: {order.product.name}
🔑 Clave generada: {game_key}

📌 INSTRUCCIONES:
1. Abre el archivo HTML en tu navegador
2. Copia todo el contenido (Ctrl+A, Ctrl+C)
3. Abre tu Gmail/Outlook
4. Crea nuevo correo para: {order.customer_email}
5. Pega el contenido en formato HTML
6. Revisa y envía manualmente
                """,
                level='SUCCESS'
            )
            
            # También guardar la clave en un archivo separado para referencia
            key_file = os.path.join(drafts_dir, f"clave_{order.order_number}.txt")
            with open(key_file, 'w', encoding='utf-8') as f:
                f.write(f"Orden: {order.order_number}\nCliente: {order.customer_name}\nEmail: {order.customer_email}\nJuego: {order.product.name}\nClave: {game_key}\n")
            
        except Exception as e:
            self.message_user(
                request,
                f"❌ Error al generar borrador: {str(e)}",
                level='ERROR'
            )


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