from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, UserProfile

def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        phone = request.POST.get('phone', '')
        
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado')
            return redirect('register')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        UserProfile.objects.create(
            user=user,
            phone=phone
        )
        
        login(request, user)
        messages.success(request, '¡Registro exitoso! Bienvenido a KHAOS STORE')
        
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('home')
    
    return render(request, 'store/register.html')

@login_required(login_url='login')
def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/checkout.html', {'product': product})

@login_required(login_url='login')
def process_payment(request, product_id):
    # Solo aceptar POST
    if request.method != 'POST':
        return redirect('home')
    
    try:
        print("=" * 50)
        print("🔍 INICIANDO PROCESO DE PAGO")
        print(f"Producto ID: {product_id}")
        print(f"Usuario: {request.user.username}")
        
        # Obtener producto
        product = get_object_or_404(Product, id=product_id)
        print(f"✅ Producto encontrado: {product.name} - Stock: {product.stock}")
        
        # Verificar stock
        if product.stock <= 0:
            messages.error(request, 'Producto agotado')
            return redirect('home')
        
        # Validar campos obligatorios
        required_fields = ['name', 'email', 'phone', 'address', 'city']
        for field in required_fields:
            if not request.POST.get(field):
                messages.error(request, f'El campo {field} es obligatorio')
                return redirect('checkout', product_id=product.id)
        
        # Crear la orden
        print("📝 Creando orden...")
        order = Order.objects.create(
            product=product,
            customer_name=request.POST.get('name', ''),
            customer_email=request.POST.get('email', ''),
            customer_phone=request.POST.get('phone', ''),
            address=request.POST.get('address', ''),
            city=request.POST.get('city', ''),
            payment_method=request.POST.get('payment_method', 'CARD'),
            total=product.get_price(),
            user=request.user,
            status='PAID'
        )
        print(f"✅ Orden creada: {order.order_number}")
        
        # Restar stock
        product.stock -= 1
        product.save()
        print(f"✅ Stock actualizado: {product.stock} unidades restantes")
        
        # --------------------------------------------------
        # EMAILS DESACTIVADOS TEMPORALMENTE PARA QUE EL PAGO FUNCIONE
        # --------------------------------------------------
        print("📧 Envío de emails desactivado - el pago se completa igualmente")
        # order.send_confirmation_email()  # COMENTADO
        # order.send_game_key()            # COMENTADO
        print("✅ Emails omitidos por configuración temporal")
        # --------------------------------------------------
        
        # Guardar en sesión
        request.session['last_order'] = order.order_number
        request.session.modified = True
        
        print(f"✅ PAGO COMPLETADO EXITOSAMENTE - Orden: {order.order_number}")
        print("=" * 50)
        
        messages.success(request, '¡Pago exitoso! La orden ha sido creada correctamente.')
        return redirect('success', order_id=order.order_number)
        
    except Exception as e:
        print("❌ ERROR CRÍTICO EN PAGO:")
        print(str(e))
        import traceback
        traceback.print_exc()
        print("=" * 50)
        
        messages.error(request, 'Error al procesar el pago. Por favor intenta de nuevo.')
        return redirect('home')

def success(request, order_id):
    return render(request, 'store/success.html', {'order_id': order_id})

@login_required(login_url='login')
def profile(request):
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/profile.html', {
        'profile': user_profile,
        'orders': orders
    })