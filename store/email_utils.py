from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.utils.html import format_html

def generate_game_key():
    """Genera una clave de juego aleatoria"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def send_order_status_email(order, previous_status=None):
    """
    Envía email según el estado de la orden
    Estados: PENDING, PAID, SENT, DELIVERED, CANCELLED
    """
    status_templates = {
        'PAID': {
            'subject': f"✅ ¡Pago Confirmado! - Orden #{order.order_number}",
            'title': 'PAGO CONFIRMADO',
            'color': '#00ff00',
            'icon': '✅',
            'message': 'Hemos recibido tu pago correctamente. Tu orden está siendo procesada.'
        },
        'SENT': {
            'subject': f"📦 ¡Tu orden ha sido enviada! - Orden #{order.order_number}",
            'title': 'ORDEN ENVIADA',
            'color': '#0070f3',
            'icon': '📦',
            'message': 'Tu cuenta de juego ha sido asignada. Revisa los datos a continuación.'
        },
        'DELIVERED': {
            'subject': f"🎮 ¡Tu juego está listo! - Orden #{order.order_number}",
            'title': 'ENTREGADO',
            'color': '#0070f3',
            'icon': '🎮',
            'message': 'Tu juego ya está disponible. ¡Disfruta tu experiencia de juego!'
        },
        'CANCELLED': {
            'subject': f"❌ Orden Cancelada - Orden #{order.order_number}",
            'title': 'ORDEN CANCELADA',
            'color': '#ff0000',
            'icon': '❌',
            'message': 'Tu orden ha sido cancelada. Si tienes dudas, contáctanos.'
        },
        'PENDING': {
            'subject': f"⏳ Orden Pendiente - Orden #{order.order_number}",
            'title': 'PENDIENTE DE PAGO',
            'color': '#ffaa00',
            'icon': '⏳',
            'message': 'Tu orden está pendiente de pago. Realiza el pago para confirmar tu compra.'
        }
    }
    
    template = status_templates.get(order.status, status_templates['PENDING'])
    
    # Generar key solo si es SENT
    game_key = generate_game_key() if order.status == 'SENT' else None
    
    try:
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{template['subject']}</title>
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
                    border-bottom: 4px solid #00aaff;
                }}
                .logo {{
                    font-family: 'Press Start 2P', monospace;
                    font-size: 28px;
                    font-weight: bold;
                    color: #ffffff;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                }}
                .logo span {{
                    color: #00aaff;
                }}
                .status-badge {{
                    display: inline-block;
                    background: {template['color']};
                    color: #ffffff;
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
                }}
                .order-info {{
                    background: #f5f5f5;
                    padding: 20px;
                    border-radius: 15px;
                    margin: 20px 0;
                    border-left: 4px solid {template['color']};
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
                .game-key-box {{
                    background: #f0f8ff;
                    border: 2px solid #003791;
                    border-radius: 15px;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .game-key {{
                    font-family: monospace;
                    font-size: 24px;
                    font-weight: bold;
                    letter-spacing: 2px;
                    color: #003791;
                    background: #fff;
                    padding: 10px;
                    border-radius: 10px;
                    border: 1px solid #ddd;
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
                .social-links {{
                    margin-top: 10px;
                }}
                .social-links a {{
                    color: #003791;
                    text-decoration: none;
                    margin: 0 10px;
                }}
                @media (max-width: 600px) {{
                    .content {{
                        padding: 20px;
                    }}
                    .title {{
                        font-size: 22px;
                    }}
                    .game-key {{
                        font-size: 18px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">KHAOS<span>_STORE</span></div>
                    <div class="status-badge">{template['icon']} {template['title']}</div>
                </div>
                
                <div class="content">
                    <h1 class="title">¡Hola, {order.customer_name}! 👋</h1>
                    <p>{template['message']}</p>
                    
                    <div class="order-info">
                        <div style="text-align: center; margin-bottom: 15px;">
                            <span style="font-size: 12px; color: #666;">NÚMERO DE ORDEN</span>
                            <div class="order-number">#{order.order_number}</div>
                        </div>
                        
                        <div class="details">
                            <div class="detail-row">
                                <span class="detail-label">🎮 Producto</span>
                                <span class="detail-value">{order.product.name}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">💰 Total</span>
                                <span class="detail-value">${order.total}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">💳 Método de pago</span>
                                <span class="detail-value">{order.get_payment_method_display()}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">📅 Fecha</span>
                                <span class="detail-value">{order.created_at|date:"d/m/Y H:i"}</span>
                            </div>
                        </div>
                    </div>
                    
                    {game_key_html}
                    
                    <div style="text-align: center;">
                        <a href="https://khaos-store.onrender.com/profile" class="button">📦 VER MIS COMPRAS</a>
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
                    <div class="social-links">
                        <a href="#">Instagram</a> | <a href="#">WhatsApp</a> | <a href="#">Facebook</a>
                    </div>
                    <p style="margin-top: 10px; font-size: 11px;">Este es un correo automático, por favor no responder.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Insertar la key si es necesario
        if game_key:
            game_key_html = f"""
            <div class="game-key-box">
                <h3 style="color: #003791; margin-bottom: 10px;">🎮 TU CLAVE DE ACTIVACIÓN</h3>
                <div class="game-key">{game_key}</div>
                <p style="margin-top: 10px; font-size: 12px; color: #666;">
                    *Guarda esta clave. La necesitarás para activar tu juego.
                </p>
            </div>
            """
            html_body = html_body.replace('{game_key_html}', game_key_html)
        else:
            html_body = html_body.replace('{game_key_html}', '')
        
        send_mail(
            subject=template['subject'],
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_body,
            fail_silently=False,
        )
        print(f"✅ Email de estado '{order.status}' enviado a {order.customer_email}")
        return True
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False