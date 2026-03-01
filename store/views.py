from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
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
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Crear perfil
        UserProfile.objects.create(
            user=user,
            phone=phone
        )
        
        # Iniciar sesión automáticamente
        login(request, user)
        messages.success(request, '¡Registro exitoso! Bienvenido a KHAOS STORE')
        return redirect('home')
    
    return render(request, 'store/register.html')

def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/checkout.html', {'product': product})

def process_payment(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Crear la orden
        order = Order.objects.create(
            product=product,
            customer_name=request.POST['name'],
            customer_email=request.POST['email'],
            customer_phone=request.POST['phone'],
            address=request.POST['address'],
            city=request.POST['city'],
            payment_method=request.POST['payment_method'],
            total=product.get_price(),
            user=request.user if request.user.is_authenticated else None
        )
        
        # Enviar correo de confirmación
        order.send_confirmation_email()
        
        # Enviar key del juego (simulado)
        order.send_game_key()
        
        # Guardar en sesión
        request.session['last_order'] = order.order_number
        
        messages.success(request, '¡Pago exitoso! Revisa tu correo para la key del juego')
        return redirect('success', order_id=order.order_number)
    
    return redirect('home')

def success(request, order_id):
    return render(request, 'store/success.html', {'order_id': order_id})


@login_required(login_url='login')  # <--- AGREGÁ ESTO
def profile(request):
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/profile.html', {
        'profile': user_profile,
        'orders': orders
    })