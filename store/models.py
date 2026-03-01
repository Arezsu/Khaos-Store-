from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random
import string

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    is_on_sale = models.BooleanField(default=False)
    sale_price = models.FloatField(null=True, blank=True)
    stock = models.IntegerField(default=10)
    category = models.CharField(max_length=100, default='Acción')
    rating = models.FloatField(default=5.0)
    reviews_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_price(self):
        return self.sale_price if self.is_on_sale else self.price

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    favorite_games = models.ManyToManyField(Product, blank=True)
    
    def __str__(self):
        return self.user.username

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
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    total = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        return 'KHAOS-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def send_confirmation_email(self):
        subject = f'🎮 Confirmación de compra - KHAOS STORE #{self.order_number}'
        message = f"""
        ¡Gracias por tu compra en KHAOS STORE!
        
        Datos de la compra:
        • Número de orden: {self.order_number}
        • Producto: {self.product.name}
        • Total: ${self.total}
        • Método de pago: {self.get_payment_method_display()}
        
        En los próximos segundos recibirás un correo con las instrucciones para descargar tu juego.
        
        Si tienes alguna duda, contáctanos en soporte@khaosstore.com
        
        ¡A jugar!
        KHAOS STORE
        """
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [self.customer_email],
            fail_silently=False,
        )
    
    def send_game_key(self):
        # Simular envío de key del juego
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
        
        Tu clave también está disponible en tu perfil.
        
        KHAOS STORE
        """
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [self.customer_email],
            fail_silently=False,
        )
    
    def __str__(self):
        return f"Order #{self.order_number}"