from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.core.validators import MinLengthValidator, RegexValidator, MinValueValidator, MaxValueValidator
from datetime import date
from django.utils.text import slugify  # Para el slug del producto

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)  # Añadido para admin
    price = models.FloatField(validators=[MinValueValidator(0)])
    image = models.URLField(max_length=500, verbose_name='URL de imagen')
    image_url = models.URLField(max_length=500, blank=True, null=True)  # Campo adicional
    description = models.TextField()
    is_on_sale = models.BooleanField(default=False)
    sale_price = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    stock = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    category = models.CharField(max_length=100, default='Acción')
    rating = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    reviews_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)  # Para activar/desactivar productos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_price(self):
        return self.sale_price if self.is_on_sale else self.price


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(
        max_length=10, 
        blank=True, 
        validators=[MinLengthValidator(10), RegexValidator(r'^\d{10}$', 'El teléfono debe tener exactamente 10 dígitos')]
    )
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    favorite_games = models.ManyToManyField(Product, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.URLField(blank=True, null=True)  # Avatar opcional
    
    def __str__(self):
        return self.user.username
    
    def is_adult(self):
        if not self.birth_date:
            return False
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return age >= 18


class Order(models.Model):
    PAYMENT_METHODS = [
        ('NEQUI', 'Nequi'),
        ('BANCOLOMBIA', 'Bancolombia'),
        ('DAVIPLATA', 'Daviplata'),
        ('CARD', 'Tarjeta de Crédito/Débito'),
        ('PAYPAL', 'PayPal'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PAID', 'Pagado'),
        ('SENT', 'Enviado'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    # Campos principales
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Datos del cliente
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(
        max_length=10,
        validators=[MinLengthValidator(10), RegexValidator(r'^\d{10}$', 'El teléfono debe tener exactamente 10 dígitos')]
    )
    address = models.TextField()
    city = models.CharField(max_length=100)
    
    # Información de pago
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, default='PENDING')
    payment_id = models.CharField(max_length=100, blank=True)
    total = models.FloatField(validators=[MinValueValidator(0)])
    
    # Estado de la orden
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Datos de la cuenta (se llenan cuando el estado es SENT)
    account_email = models.EmailField(blank=True, null=True, verbose_name='Email de la cuenta')
    account_password = models.CharField(max_length=200, blank=True, null=True, verbose_name='Contraseña de la cuenta')
    account_instructions = models.TextField(blank=True, null=True, verbose_name='Instrucciones adicionales')
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        return 'KHAOS-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def send_pending_email(self):
        """Envía email de orden pendiente con instrucciones de pago"""
        try:
            subject = f'🎮 Orden Pendiente #{self.order_number} - KHAOS STORE'
            message = f"""
¡Hola {self.customer_name}!

Tu orden #{self.order_number} ha sido creada exitosamente.

📝 DATOS DEL PEDIDO:
• Producto: {self.product.name}
• Cantidad: {self.quantity}
• Total: ${self.total}
• Método de pago: {self.get_payment_method_display()}

💰 PARA REALIZAR EL PAGO:
• Nequi: 333 7452514
• Bancolombia: 333 7452514
• Referencia: {self.order_number}

⚠️ IMPORTANTE:
1. Realiza el pago por el valor total
2. Envía el comprobante a soportekhaosstore@gmail.com
3. Tu orden será activada dentro de 24 horas

Estado actual: PENDIENTE DE PAGO

¿Preguntas? Contáctanos: soportekhaosstore@gmail.com

KHAOS STORE
"""
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.customer_email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error enviando email pendiente: {e}")
            return False
    
    def send_account_email(self):
        """Envía email con datos de la cuenta cuando se confirma el pago"""
        try:
            # Usar los datos almacenados en el modelo
            account_email = self.account_email or "cuenta_psn@ejemplo.com"
            account_password = self.account_password or "contraseña_temporal"
            instructions = self.account_instructions or ""
            
            subject = f'🎮 ¡Tu juego está listo! Orden #{self.order_number}'
            message = f"""
🎮 PlayStation Network - KHAOS STORE

¡Hola {self.customer_name}!

Tu pago ha sido confirmado. Aquí están los datos para acceder a tu juego:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 JUEGO: {self.product.name}
📧 EMAIL: {account_email}
🔑 CONTRASEÑA: {account_password}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 INSTRUCCIONES:
{instructions if instructions else "1. En tu PlayStation, ve a 'Configuración' → 'Usuarios y cuentas'\n2. Selecciona 'Iniciar sesión' y usa los datos de arriba\n3. Una vez dentro, ve a 'Biblioteca' → 'Tus colecciones'\n4. Descarga el juego\n5. ¡Disfruta!"}

⚠️ IMPORTANTE:
• NO cambies la contraseña hasta que hayas descargado el juego
• Si tienes problemas, contáctanos inmediatamente

¿Problemas? Responde a este correo o escribe a soportekhaosstore@gmail.com

KHAOS STORE
"""
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.customer_email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error enviando email de cuenta: {e}")
            return False
    
    def __str__(self):
        return f"Order #{self.order_number}"