from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator, MinValueValidator, MaxValueValidator
from datetime import date
import random
import string


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField(validators=[MinValueValidator(0)])
    image = models.URLField(max_length=500, verbose_name='URL de imagen')
    description = models.TextField()
    is_on_sale = models.BooleanField(default=False)
    sale_price = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    stock = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    category = models.CharField(max_length=100, default='Accion')
    rating = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    reviews_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    trailer_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL del video de YouTube o Vimeo")
    video_file = models.FileField(upload_to='products/videos/', blank=True, null=True, help_text="Video local MP4")
    
    def __str__(self):
        return self.name
    
    def get_price(self):
        return self.sale_price if self.is_on_sale else self.price
    
    def get_avg_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / reviews.count()
        return float(self.rating)
    
    def get_reviews_count(self):
        return self.reviews.count()
    
    def is_available(self):
        return self.stock > 0
    
    def has_stock(self, quantity=1):
        return self.stock >= quantity
    
    def reduce_stock(self, quantity=1):
        if self.has_stock(quantity):
            self.stock -= quantity
            self.save()
            return True
        return False


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(
        max_length=10, 
        blank=True, 
        validators=[MinLengthValidator(10), RegexValidator(r'^\d{10}$', 'El telefono debe tener exactamente 10 digitos')]
    )
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    favorite_games = models.ManyToManyField(Product, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.user.username
    
    def is_adult(self):
        if not self.birth_date:
            return False
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return age >= 18


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"
    
    def __str__(self):
        if self.user:
            return f"Carrito de {self.user.username}"
        return f"Carrito temporal {self.session_key}"
    
    def get_total(self):
        return sum(item.get_total() for item in self.items.all())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    class Meta:
        verbose_name = "Item del carrito"
        verbose_name_plural = "Items del carrito"
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total(self):
        return self.product.get_price() * self.quantity


class Order(models.Model):
    PAYMENT_METHODS = [
        ('CARD', 'Tarjeta de Credito/Debito'),
        ('PAYPAL', 'PayPal'),
        ('NEQUI', 'Nequi'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PAID', 'Pagado'),
        ('SENT', 'Enviado'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='orders')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=10, validators=[MinLengthValidator(10), RegexValidator(r'^\d{10}$')])
    address = models.TextField()
    city = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    total = models.FloatField(validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        return 'KHAOS-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    def get_products_list(self):
        if self.cart:
            return [item for item in self.cart.items.all()]
        elif self.product:
            return [{'product': self.product, 'quantity': 1, 'get_total': lambda: self.product.get_price()}]
        return []
    
    def get_products_display(self):
        products = []
        if self.cart:
            for item in self.cart.items.all():
                products.append(f"{item.product.name} x{item.quantity}")
        elif self.product:
            products.append(self.product.name)
        return ", ".join(products)
    
    def send_pending_email(self):
        """Envia email de orden pendiente con instrucciones de pago y boton de WhatsApp"""
        try:
            products_list = self.get_products_display()
            whatsapp_link = "https://wa.link/1pelm8"
            
            subject = f'Orden Pendiente #{self.order_number} - KHAOS STORE'
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Orden Pendiente - KHAOS STORE</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #0f0c29;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: auto;
                        background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border-radius: 20px;
                        padding: 30px;
                        border: 2px solid #ffaa00;
                        box-shadow: 0 0 20px rgba(255, 170, 0, 0.3);
                    }}
                    .header {{
                        text-align: center;
                        border-bottom: 2px solid #ffaa00;
                        padding-bottom: 20px;
                        margin-bottom: 20px;
                    }}
                    .logo {{
                        font-family: 'Courier New', monospace;
                        font-size: 28px;
                        font-weight: bold;
                        color: #ffaa00;
                    }}
                    .order-number {{
                        background: rgba(255, 170, 0, 0.2);
                        padding: 15px;
                        border-radius: 10px;
                        text-align: center;
                        margin: 20px 0;
                    }}
                    .amount {{
                        font-size: 32px;
                        font-weight: bold;
                        color: #ffaa00;
                    }}
                    .payment-info {{
                        background: #000;
                        padding: 20px;
                        border-radius: 10px;
                        margin: 20px 0;
                    }}
                    .whatsapp-btn {{
                        display: block;
                        background-color: #25D366;
                        color: white;
                        text-align: center;
                        padding: 14px 20px;
                        margin: 30px 0;
                        border-radius: 50px;
                        text-decoration: none;
                        font-weight: bold;
                        font-size: 18px;
                        transition: all 0.3s ease;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                    }}
                    .whatsapp-btn:hover {{
                        background-color: #128C7E;
                        transform: scale(1.02);
                        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        font-size: 12px;
                        color: #888;
                        border-top: 1px solid #333;
                        padding-top: 20px;
                    }}
                    .note {{
                        font-size: 12px;
                        color: #ffaa00;
                        text-align: center;
                        margin-top: 15px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">KHAOS STORE</div>
                        <p>Orden Pendiente de Pago</p>
                    </div>
                    
                    <div class="order-number">
                        <strong>NUMERO DE ORDEN</strong><br>
                        <span style="font-size: 24px;">{self.order_number}</span>
                    </div>
                    
                    <p><strong>Producto(s):</strong> {products_list}</p>
                    <p><strong>Total a pagar:</strong> <span class="amount">${self.total}</span></p>
                    <p><strong>Metodo de pago seleccionado:</strong> {self.get_payment_method_display()}</p>
                    
                    <div class="payment-info">
                        <h3 style="margin-top: 0; color: #ffaa00;">INSTRUCCIONES DE PAGO</h3>
                        <p>Realiza el pago por el valor total a las siguientes cuentas:</p>
                        <ul>
                            <li><strong>Nequi:</strong> 333 7452514</li>
                            <li><strong>Bancolombia:</strong> 333 7452514</li>
                        </ul>
                        <p><strong>Referencia:</strong> {self.order_number}</p>
                    </div>
                    
                    <a href="{whatsapp_link}" class="whatsapp-btn" target="_blank">
                        ENVIAR COMPROBANTE POR WHATSAPP
                    </a>
                    
                    <p><strong>IMPORTANTE:</strong></p>
                    <ol>
                        <li>Realiza el pago por el valor total</li>
                        <li>Haz clic en el boton de WhatsApp</li>
                        <li>Adjunta el comprobante de pago en el chat</li>
                        <li>Tu orden sera activada dentro de 24 horas</li>
                    </ol>
                    
                    <div class="note">
                        Si no puedes usar el boton, envia el comprobante manualmente a soportekhaosstore@gmail.com
                    </div>
                    
                    <div class="footer">
                        <p>2026 Khaos Store | soportekhaosstore@gmail.com | 333 7452514</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            from django.core.mail import EmailMultiAlternatives
            from django.utils.html import strip_tags
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=strip_tags(html_body),
                from_email='Khaos Store <soportekhaosstore@gmail.com>',
                to=[self.customer_email]
            )
            email.attach_alternative(html_body, "text/html")
            email.send()
            return True
        except Exception as e:
            print(f"Error enviando email pendiente: {e}")
            return False
    
    def send_payment_confirmation(self):
        from .email_utils import send_payment_confirmation
        return send_payment_confirmation(self)
    
    def __str__(self): 
        return f"Order #{self.order_number}"


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 estrella'),
        (2, '2 estrellas'),
        (3, '3 estrellas'),
        (4, '4 estrellas'),
        (5, '5 estrellas'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Resena"
        verbose_name_plural = "Resenas"
        unique_together = ['product', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}: {self.rating}★"