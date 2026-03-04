from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.core.validators import MinLengthValidator, RegexValidator, MinValueValidator, MaxValueValidator
from datetime import date

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nombre')
    price = models.FloatField(validators=[MinValueValidator(0)], verbose_name='Precio')
    image = models.ImageField(upload_to='products/', verbose_name='Imagen')
    description = models.TextField(verbose_name='Descripción')
    is_on_sale = models.BooleanField(default=False, verbose_name='En oferta')
    sale_price = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Precio de oferta')
    stock = models.IntegerField(default=10, validators=[MinValueValidator(0)], verbose_name='Stock')
    category = models.CharField(max_length=100, default='Acción', verbose_name='Categoría')
    rating = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name='Valoración')
    reviews_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Cantidad de reseñas')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_price(self):
        """Devuelve el precio actual (normal o de oferta)"""
        return self.sale_price if self.is_on_sale and self.sale_price else self.price

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Usuario')
    phone = models.CharField(
        max_length=10, 
        blank=True, 
        validators=[MinLengthValidator(10), RegexValidator(r'^\d{10}$', 'El teléfono debe tener exactamente 10 dígitos')],
        verbose_name='Teléfono'
    )
    address = models.TextField(blank=True, verbose_name='Dirección')
    city = models.CharField(max_length=100, blank=True, verbose_name='Ciudad')
    favorite_games = models.ManyToManyField(Product, blank=True, verbose_name='Juegos favoritos')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Fecha de nacimiento')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuarios'
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def is_adult(self):
        """Verifica si el usuario es mayor de 18 años"""
        if not self.birth_date:
            return False
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return age >= 18
    
    def get_age(self):
        """Calcula la edad del usuario"""
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

class Order(models.Model):
    PAYMENT_METHODS = [
        ('CARD', '💳 Tarjeta de Crédito/Débito'),
        ('PAYPAL', '🅿️ PayPal'),
        ('NEQUI', '📱 Nequi'),
    ]
    
    STATUS = [
        ('PENDING', '⏳ Pendiente'),
        ('PAID', '✅ Pagado'),
        ('SENT', '📤 Enviado'),
        ('DELIVERED', '📦 Entregado'),
        ('CANCELLED', '❌ Cancelado'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, verbose_name='Número de orden')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='orders', verbose_name='Usuario')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders', verbose_name='Producto')
    customer_name = models.CharField(max_length=200, verbose_name='Nombre del cliente')
    customer_email = models.EmailField(verbose_name='Email del cliente')
    customer_phone = models.CharField(
        max_length=10, 
        validators=[MinLengthValidator(10), RegexValidator(r'^\d{10}$', 'El teléfono debe tener 10 dígitos')],
        verbose_name='Teléfono del cliente'
    )
    address = models.TextField(verbose_name='Dirección')
    city = models.CharField(max_length=100, verbose_name='Ciudad')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name='Método de pago')
    total = models.FloatField(validators=[MinValueValidator(0)], verbose_name='Total')
    status = models.CharField(max_length=20, choices=STATUS, default='PENDING', verbose_name='Estado')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Genera un número de orden único"""
        return 'KHAOS-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def send_confirmation_email(self):
        """Envía email de confirmación de compra"""
        try:
            subject = f'🎮 Confirmación de compra - KHAOS STORE #{self.order_number}'
            message = f"""
            ¡Gracias por tu compra en KHAOS STORE!
            
            📋 DATOS DE LA COMPRA:
            • Número de orden: {self.order_number}
            • Producto: {self.product.name}
            • Total: ${self.total:,.2f}
            • Método de pago: {self.get_payment_method_display()}
            
            📦 ESTADO: {self.get_status_display()}
            
            En los próximos minutos recibirás la key de tu juego en un correo separado.
            
            Si tienes alguna duda, contáctanos:
            📧 soporte@khaosstore.com
            📱 333 7452514
            
            ¡A jugar!
            🎮 KHAOS STORE
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.customer_email],
                fail_silently=False,
            )
            print(f"✅ Email de confirmación enviado a {self.customer_email}")
            return True
        except Exception as e:
            print(f"❌ Error enviando confirmación: {e}")
            return False
    
    def send_game_key(self):
        """Envía la key del juego al cliente"""
        try:
            # Generar una key aleatoria (simulada)
            game_key = '-'.join([''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(4)])
            
            subject = f'🔑 Tu juego {self.product.name} ya está listo - KHAOS STORE'
            message = f"""
            ¡Hola {self.customer_name}!
            
            Tu juego {self.product.name} ya está disponible.
            
            🔐 TU CLAVE DE ACTIVACIÓN:
            ═══════════════════════
            {game_key}
            ═══════════════════════
            
            📝 INSTRUCCIONES:
            1. Abre la cuenta en tu Playstation
            2. Creas cuenta e inicias sesion y ingresas la cuenta recuerda no compartirla si la compartes se te sera eliminada
            3. Ingresa la clave: {game_key}
            4. ¡Descarga y disfruta!
            
            Esta clave también está disponible en tu perfil de KHAOS STORE.
            
            ¿Problemas? Contáctanos:
            📧 soporte@khaosstore.com
            📱 333 7452514
            
            🎮 KHAOS STORE
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.customer_email],
                fail_silently=False,
            )
            print(f"✅ Email con key enviado a {self.customer_email}")
            return True
        except Exception as e:
            print(f"❌ Error enviando key: {e}")
            return False
    
    def __str__(self):
        return f"Orden #{self.order_number} - {self.product.name}"