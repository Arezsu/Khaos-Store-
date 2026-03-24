from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.core.validators import MinLengthValidator, RegexValidator, MinValueValidator, MaxValueValidator
from datetime import date

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField(validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    is_on_sale = models.BooleanField(default=False)
    sale_price = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    stock = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    category = models.CharField(max_length=100, default='Acción')
    rating = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    reviews_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    
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
    birth_date = models.DateField(null=True, blank=True)  # <--- ESTE CAMPO DEBE EXISTIR
    
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
        ('CARD', 'Tarjeta de Crédito/Débito'),
        ('PAYPAL', 'PayPal'),
        ('NEQUI', 'Nequi'),
    ]
    
    STATUS = [
        ('PENDING', 'Pendiente'),
        ('PAID', 'Pagado'),
        ('SENT', 'Enviado'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=10, validators=[MinLengthValidator(10), RegexValidator(r'^\d{10}$')])
    address = models.TextField()
    city = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    total = models.FloatField(validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        return 'KHAOS-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def send_confirmation_email(self):
        try:
            subject = f'🎮 Confirmación de compra - KHAOS STORE #{self.order_number}'
            message = f"""
¡Gracias por tu compra en KHAOS STORE!

Datos de la compra:
• Número de orden: {self.order_number}
• Producto: {self.product.name}
• Total: ${self.total}
• Método de pago: {self.get_payment_method_display()}

En los próximos minutos recibirás la key de tu juego.

Si tienes alguna duda, contáctanos al 333 7452514 o a soporte@khaosstore.com

¡A jugar!
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
            print(f"Error enviando confirmación: {e}")
            return False
    
    def send_game_key(self):
        try:
            game_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
            subject = f'🔑 Tu juego {self.product.name} ya está listo - KHAOS STORE'
            message = f"""
¡Hola {self.customer_name}!

Tu juego {self.product.name} ya está disponible.

Tu clave de activación: {game_key}

Instrucciones de activación:
1. Abre la plataforma correspondiente
2. Ve a "Canjear código"
3. Ingresa: {game_key}
4. ¡Disfruta tu juego!

¿Problemas? Contáctanos al 333 7452514

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
            print(f"Error enviando key: {e}")
            return False
    
    def __str__(self):
        return f"Order #{self.order_number}"