# store/email_utils.py
from django.core.mail import send_mail
from django.conf import settings
import random
import string

def generate_game_key():
    """Genera una clave de juego aleatoria"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def send_welcome_email(user):
    """Envía email de bienvenida después del registro"""
    try:
        subject = "🎮 ¡Bienvenido a Khaos Store!"
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
                    <p>Si tienes alguna duda, contáctanos a soportekhaosstore@gmail.com </p>
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

def send_payment_confirmation(order):
    """Envía email de confirmación de pago después de una compra"""
    try:
        game_key = generate_game_key()
        subject = f"✅ ¡Pago confirmado! Orden #{order.order_number}"
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
                    padding: 10px;
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
                    padding: 15px;
                    border-radius: 10px;
                    font-family: monospace;
                    font-size: 18px;
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
                <div class="content">
                    <h2>¡Pago Confirmado, {order.customer_name}! 🎉</h2>
                    <p>Tu compra ha sido procesada exitosamente.</p>
                    
                    <div class="order-number">
                        <strong>NÚMERO DE ORDEN</strong><br>
                        <span style="font-size: 20px;">{order.order_number}</span>
                    </div>
                    
                    <p><strong>Producto:</strong> {order.product.name}</p>
                    <p><strong>Total pagado:</strong> <span class="amount">${order.total}</span></p>
                    <p><strong>Método de pago:</strong> {order.get_payment_method_display()}</p>
                    
                    <h3>🎮 TU CLAVE DE ACTIVACIÓN</h3>
                    <div class="game-key">
                        {game_key}
                    </div>
                    <p style="font-size: 12px; color: #ffaa00;">*Guarda esta clave, la necesitarás para activar tu juego.</p>
                    
                    <p>Instrucciones de activación:</p>
                    <ol>
                        <li>Abre la plataforma de juegos (Steam, Epic Games, etc.)</li>
                        <li>Ve a "Canjear código" o "Activar producto"</li>
                        <li>Ingresa la clave de activación</li>
                        <li>¡Disfruta tu juego!</li>
                    </ol>
                    
                    <p>¿Problemas? Contáctanos a soportekhaosstore@gmail.com</p>
                </div>
                <div class="footer">
                    <p>© 2026 Khaos Store | soportekhaosstore@gmail.com | 333 7452514</p>
                </div>
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