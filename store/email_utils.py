from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.utils.html import format_html
from django.template.loader import render_to_string

def generate_game_key():
    """Genera una clave de juego aleatoria"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def send_order_status_email(order, previous_status=None):
    """
    Envía email según el estado de la orden
    Estados: PENDING, PAID, SENT, DELIVERED, CANCELLED
    """
    # [Todo tu código existente de send_order_status_email aquí]
    # ... (mantén todo tu código actual)
    
def send_welcome_email(user_email, user_name):
    """
    Envía un email de bienvenida a nuevos usuarios
    """
    subject = f"🎮 ¡Bienvenido a KHAOS_STORE, {user_name}!"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bienvenido a KHAOS_STORE</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', 'Montserrat', Arial, sans-serif;
                background: linear-gradient(135deg, #003791 0%, #0044b3 100%);
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            }}
            .header {{
                background: linear-gradient(135deg, #003791 0%, #0044b3 100%);
                padding: 40px 30px;
                text-align: center;
                border-bottom: 4px solid #00aaff;
            }}
            .logo {{
                font-family: 'Press Start 2P', monospace;
                font-size: 32px;
                font-weight: bold;
                color: #ffffff;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            }}
            .logo span {{
                color: #00aaff;
            }}
            .welcome-icon {{
                font-size: 80px;
                margin: 20px 0;
            }}
            .content {{
                padding: 40px;
                color: #333;
            }}
            .title {{
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 20px;
                color: #003791;
                text-align: center;
            }}
            .message-box {{
                background: #f5f5f5;
                padding: 25px;
                border-radius: 15px;
                margin: 20px 0;
                border-left: 4px solid #00aaff;
            }}
            .feature-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin: 30px 0;
            }}
            .feature {{
                text-align: center;
                padding: 20px;
                background: #f8f8f8;
                border-radius: 15px;
                transition: transform 0.3s;
            }}
            .feature:hover {{
                transform: translateY(-5px);
            }}
            .feature-icon {{
                font-size: 40px;
                margin-bottom: 10px;
            }}
            .feature-title {{
                font-weight: bold;
                color: #003791;
                margin-bottom: 10px;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #003791 0%, #0044b3 100%);
                color: #ffffff;
                padding: 14px 30px;
                text-decoration: none;
                border-radius: 50px;
                font-weight: bold;
                margin-top: 20px;
                transition: all 0.3s;
            }}
            .button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 55, 145, 0.4);
            }}
            .footer {{
                background: #f8f8f8;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
                border-top: 1px solid #eee;
            }}
            @media (max-width: 600px) {{
                .content {{
                    padding: 20px;
                }}
                .feature-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">KHAOS<span>_STORE</span></div>
                <div class="welcome-icon">🎮✨</div>
            </div>
            
            <div class="content">
                <h1 class="title">¡Bienvenido a la familia KHAOS, {user_name}! 🎉</h1>
                
                <div class="message-box">
                    <p style="font-size: 16px; line-height: 1.6;">
                        Gracias por unirte a KHAOS_STORE, tu tienda de confianza para juegos 
                        y entretenimiento. Estamos emocionados de tenerte con nosotros y de 
                        ofrecerte las mejores experiencias de juego.
                    </p>
                </div>
                
                <div class="feature-grid">
                    <div class="feature">
                        <div class="feature-icon">🎮</div>
                        <div class="feature-title">Juegos Exclusivos</div>
                        <p style="font-size: 12px;">Accede a los mejores títulos</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">⚡</div>
                        <div class="feature-title">Entrega Inmediata</div>
                        <p style="font-size: 12px;">Recibe tus claves al instante</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">💳</div>
                        <div class="feature-title">Pago Seguro</div>
                        <p style="font-size: 12px;">Transacciones protegidas</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🎁</div>
                        <div class="feature-title">Ofertas Especiales</div>
                        <p style="font-size: 12px;">Descuentos exclusivos</p>
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <a href="https://khaos-store.onrender.com" class="button">🛒 COMENZAR A COMPRAR</a>
                </div>
                
                <div style="margin-top: 30px; padding: 15px; background: #f0f8ff; border-radius: 10px; text-align: center;">
                    <p style="margin: 0; font-size: 14px; color: #003791;">
                        💡 ¿Tienes preguntas? Contáctanos a soportekhaosstore@gmail.com
                    </p>
                </div>
            </div>
            
            <div class="footer">
                <p>© 2026 KHAOS STORE - Todos los derechos reservados</p>
                <p>soportekhaosstore@gmail.com | 333 7452514</p>
                <p style="margin-top: 10px; font-size: 11px;">Este es un correo automático, por favor no responder.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_body,
            fail_silently=False,
        )
        print(f"✅ Email de bienvenida enviado a {user_email}")
        return True
    except Exception as e:
        print(f"❌ Error enviando email de bienvenida: {e}")
        return False

def send_payment_confirmation(user_email, order_details):
    """
    Envía un email de confirmación de pago
    order_details debe contener: order_number, product_name, total, payment_method, created_at
    """
    subject = f"💰 Confirmación de Pago - Orden #{order_details.get('order_number', 'N/A')}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Confirmación de Pago</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', 'Montserrat', Arial, sans-serif;
                background: linear-gradient(135deg, #003791 0%, #0044b3 100%);
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            }}
            .header {{
                background: linear-gradient(135deg, #003791 0%, #0044b3 100%);
                padding: 30px;
                text-align: center;
                border-bottom: 4px solid #00ff00;
            }}
            .logo {{
                font-family: 'Press Start 2P', monospace;
                font-size: 28px;
                font-weight: bold;
                color: #ffffff;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            }}
            .logo span {{
                color: #00ff00;
            }}
            .success-icon {{
                font-size: 70px;
                margin: 20px 0;
            }}
            .status-badge {{
                display: inline-block;
                background: #00ff00;
                color: #003791;
                padding: 8px 20px;
                border-radius: 50px;
                font-weight: bold;
                margin-top: 15px;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .content {{
                padding: 40px;
                color: #333;
            }}
            .title {{
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 20px;
                color: #003791;
                text-align: center;
            }}
            .order-info {{
                background: #f5f5f5;
                padding: 20px;
                border-radius: 15px;
                margin: 20px 0;
                border-left: 4px solid #00ff00;
            }}
            .order-number {{
                font-size: 24px;
                font-weight: bold;
                color: #003791;
                font-family: monospace;
                letter-spacing: 2px;
            }}
            .details {{
                margin: 20px 0;
            }}
            .detail-row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }}
            .detail-label {{
                font-weight: bold;
                color: #666;
            }}
            .detail-value {{
                color: #333;
                font-weight: 500;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #003791 0%, #0044b3 100%);
                color: #ffffff;
                padding: 14px 30px;
                text-decoration: none;
                border-radius: 50px;
                font-weight: bold;
                margin-top: 20px;
                transition: all 0.3s;
            }}
            .button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 55, 145, 0.4);
            }}
            .footer {{
                background: #f8f8f8;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
                border-top: 1px solid #eee;
            }}
            @media (max-width: 600px) {{
                .content {{
                    padding: 20px;
                }}
                .title {{
                    font-size: 22px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">KHAOS<span>_STORE</span></div>
                <div class="success-icon">✅💳</div>
                <div class="status-badge">PAGO CONFIRMADO</div>
            </div>
            
            <div class="content">
                <h1 class="title">¡Pago Recibido con Éxito! 🎉</h1>
                <p style="text-align: center; margin-bottom: 20px;">
                    Gracias por tu compra. Tu pago ha sido procesado correctamente.
                </p>
                
                <div class="order-info">
                    <div style="text-align: center; margin-bottom: 15px;">
                        <span style="font-size: 12px; color: #666;">NÚMERO DE ORDEN</span>
                        <div class="order-number">#{order_details.get('order_number', 'N/A')}</div>
                    </div>
                    
                    <div class="details">
                        <div class="detail-row">
                            <span class="detail-label">🎮 Producto</span>
                            <span class="detail-value">{order_details.get('product_name', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">💰 Total</span>
                            <span class="detail-value">${order_details.get('total', 0)}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">💳 Método de pago</span>
                            <span class="detail-value">{order_details.get('payment_method', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">📅 Fecha</span>
                            <span class="detail-value">{order_details.get('created_at', 'N/A')}</span>
                        </div>
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <a href="https://khaos-store.onrender.com/profile" class="button">📦 VER MI ORDEN</a>
                </div>
                
                <div style="margin-top: 30px; padding: 15px; background: #f0f8ff; border-radius: 10px; text-align: center;">
                    <p style="margin: 0; font-size: 14px; color: #003791;">
                        🎮 Tu juego será entregado en los próximos minutos. Revisa tu email.
                    </p>
                </div>
            </div>
            
            <div class="footer">
                <p>© 2026 KHAOS STORE - Todos los derechos reservados</p>
                <p>soportekhaosstore@gmail.com | 333 7452514</p>
                <p style="margin-top: 10px; font-size: 11px;">Este es un correo automático, por favor no responder.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_body,
            fail_silently=False,
        )
        print(f"✅ Email de confirmación de pago enviado a {user_email}")
        return True
    except Exception as e:
        print(f"❌ Error enviando email de confirmación de pago: {e}")
        return False