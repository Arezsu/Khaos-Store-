from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import random
import string
import logging

logger = logging.getLogger(__name__)


def generate_game_key():
    """Genera una clave de juego aleatoria"""
    return '-'.join([''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(4)])


def send_email(subject, to_email, template_name, context):
    """
    Envía un correo electrónico usando una plantilla HTML.
    
    Args:
        subject (str): Asunto del correo
        to_email (str/list): Destinatario(s)
        template_name (str): Ruta de la plantilla (ej: 'emails/welcome.html')
        context (dict): Datos para la plantilla
    
    Returns:
        bool: True si se envió correctamente, False si hubo error
    """
    try:
        # Renderizar la plantilla HTML
        html_content = render_to_string(template_name, context)
        # Versión en texto plano (sin HTML)
        text_content = strip_tags(html_content)
        
        # Crear el correo con ambas versiones
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email] if isinstance(to_email, str) else to_email
        )
        email.attach_alternative(html_content, "text/html")
        
        # Enviar
        email.send()
        logger.info(f"Correo enviado a {to_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Error al enviar correo a {to_email}: {str(e)}")
        return False


def send_welcome_email(user):
    """Envía correo de bienvenida al registrarse"""
    try:
        subject = '🎮 ¡Bienvenido a Khaos Store!'
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Montserrat', Arial, sans-serif;
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
                    border: 2px solid #ff00ff;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #ff00ff;
                    padding-bottom: 20px;
                }}
                .logo {{
                    font-family: 'Press Start 2P', monospace;
                    font-size: 24px;
                    background: linear-gradient(45deg, #ff00ff, #00ffff);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                .content {{ color: #fff; line-height: 1.6; }}
                .button {{
                    display: inline-block;
                    background: linear-gradient(45deg, #ff00ff, #00ffff);
                    color: #000;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-size: 12px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">KHAOS_STORE</div>
                </div>
                <div class="content">
                    <h2 style="color: #ff00ff;">¡Bienvenido a Khaos Store, {user.username}! 🎮</h2>
                    <p>Nos alegra tenerte en nuestra comunidad gamer.</p>
                    <p>Tu cuenta ha sido creada exitosamente. Ahora puedes:</p>
                    <ul>
                        <li>Explorar nuestro catálogo de juegos</li>
                        <li>Realizar tus compras de forma segura</li>
                        <li>Recibir keys de activación al instante</li>
                        <li>Ver tu historial de compras</li>
                    </ul>
                    <div style="text-align: center;">
                        <a href="https://khaos-store.onrender.com" class="button">COMENZAR A COMPRAR</a>
                    </div>
                    <p>Si tienes alguna duda, contáctanos a soportekhaosstore@gmail.com</p>
                    <p>¡Prepárate para vivir la experiencia gamer definitiva!</p>
                </div>
                <div class="footer">
                    <p>© 2026 Khaos Store - Todos los derechos reservados</p>
                    <p>soportekhaosstore@gmail.com | 333 7452514</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_body,
            fail_silently=False,
        )
        print(f"✅ Email de bienvenida enviado a {user.email}")
        return True
    except Exception as e:
        print(f"❌ Error enviando email de bienvenida: {e}")
        return False


def send_pending_email(order):
    """Envía email de orden pendiente con instrucciones de pago"""
    try:
        products_list = order.get_products_display() if hasattr(order, 'get_products_display') else order.product.name
        
        subject = f'🎮 Orden Pendiente #{order.order_number} - KHAOS STORE'
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Montserrat', Arial, sans-serif;
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
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #ffaa00;
                    padding-bottom: 20px;
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
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-size: 12px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="color: #ffaa00;">KHAOS STORE</h2>
                </div>
                <div class="order-number">
                    <strong>NÚMERO DE ORDEN</strong><br>
                    <span style="font-size: 20px;">{order.order_number}</span>
                </div>
                <p><strong>Productos:</strong> {products_list}</p>
                <p><strong>Total:</strong> <span class="amount">${order.total}</span></p>
                <p><strong>Método de pago:</strong> {order.get_payment_method_display()}</p>
                
                <div class="payment-info">
                    <h3>💰 PARA REALIZAR EL PAGO:</h3>
                    <p><strong>Nequi:</strong> 333 7452514</p>
                    <p><strong>Bancolombia:</strong> 333 7452514</p>
                    <p><strong>Referencia:</strong> {order.order_number}</p>
                </div>
                
                <p><strong>⚠️ IMPORTANTE:</strong></p>
                <ol>
                    <li>Realiza el pago por el valor total</li>
                    <li>Envía el comprobante a soportekhaosstore@gmail.com</li>
                    <li>Tu orden será activada dentro de 24 horas</li>
                </ol>
                
                <p>Estado actual: <strong>PENDIENTE DE PAGO</strong></p>
                <p>¿Preguntas? Contáctanos: soportekhaosstore@gmail.com</p>
            </div>
            <div class="footer">
                <p>© 2026 Khaos Store | soportekhaosstore@gmail.com | 333 7452514</p>
            </div>
        </body>
        </html>
        """
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_body,
            fail_silently=False,
        )
        print(f"✅ Email pendiente enviado a {order.customer_email}")
        return True
    except Exception as e:
        print(f"❌ Error enviando email pendiente: {e}")
        return False


def send_payment_confirmation(order):
    """Envía email de confirmación de pago con clave de juego"""
    try:
        game_key = generate_game_key()
        products_list = order.get_products_display() if hasattr(order, 'get_products_display') else order.product.name
        
        subject = f'✅ ¡Pago Confirmado! Orden #{order.order_number} - KHAOS STORE'
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Montserrat', Arial, sans-serif;
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
                    border: 2px solid #00ff00;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #00ff00;
                    padding-bottom: 20px;
                }}
                .order-number {{
                    background: rgba(0, 255, 0, 0.2);
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .amount {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #00ff00;
                }}
                .game-key {{
                    background: #000;
                    padding: 20px;
                    border-radius: 10px;
                    font-family: monospace;
                    font-size: 20px;
                    text-align: center;
                    letter-spacing: 2px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-size: 12px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="color: #00ff00;">KHAOS STORE</h2>
                </div>
                <h2>¡Pago Confirmado, {order.customer_name}! 🎉</h2>
                
                <div class="order-number">
                    <strong>NÚMERO DE ORDEN</strong><br>
                    <span style="font-size: 20px;">{order.order_number}</span>
                </div>
                
                <p><strong>Productos:</strong> {products_list}</p>
                <p><strong>Total pagado:</strong> <span class="amount">${order.total}</span></p>
                
                <h3>🎮 TU CLAVE DE ACTIVACIÓN</h3>
                <div class="game-key">
                    {game_key}
                </div>
                
                <p><strong>📌 INSTRUCCIONES:</strong></p>
                <ol>
                    <li>Abre la plataforma de juegos (Steam, Epic Games, etc.)</li>
                    <li>Ve a "Canjear código" o "Activar producto"</li>
                    <li>Ingresa la clave de activación</li>
                    <li>¡Disfruta tu juego!</li>
                </ol>
                
                <p>¿Problemas? Contáctanos: soportekhaosstore@gmail.com</p>
            </div>
            <div class="footer">
                <p>© 2026 Khaos Store | soportekhaosstore@gmail.com | 333 7452514</p>
            </div>
        </body>
        </html>
        """
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_body,
            fail_silently=False,
        )
        print(f"✅ Email de confirmación enviado a {order.customer_email}")
        return True
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False


def send_order_confirmation(order):
    """Alias para send_payment_confirmation (consistencia)"""
    return send_payment_confirmation(order)