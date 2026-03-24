from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Order, UserProfile
from .email_utils import send_welcome_email, send_payment_confirmation
from datetime import date
import re

def home(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products, 'query': query})

def register(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            phone = request.POST.get('phone', '')
            
            # Validaciones
            if not username or not email or not password:
                return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios'}, status=400)
            
            if password != confirm_password:
                return JsonResponse({'success': False, 'error': 'Las contraseñas no coinciden'}, status=400)
            
            if len(password) < 4:
                return JsonResponse({'success': False, 'error': 'La contraseña debe tener al menos 4 caracteres'}, status=400)
            
            if not re.match(r'^[a-zA-Z0-9áéíóúüñÁÉÍÓÚÜÑ]+$', password):
                return JsonResponse({'success': False, 'error': 'La contraseña solo puede contener letras y números'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': 'El usuario ya existe'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'El email ya está registrado'}, status=400)
            
            if len(phone) != 10 or not phone.isdigit():
                return JsonResponse({'success': False, 'error': 'El teléfono debe tener 10 dígitos'}, status=400)
            
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
            
            # Iniciar sesión
            login(request, user)
            request.session.save()
            
            messages.success(request, f'¡Bienvenido {username}!')
            
            # EMAIL DESACTIVADO TEMPORALMENTE PARA EVITAR ERRORES
            # send_welcome_email(user)
            
            return JsonResponse({'success': True, 'redirect': '/'})
            
        except Exception as e:
            print(f"ERROR EN REGISTRO: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return render(request, 'store/register.html')

def custom_logout(request):
    logout(request)
    messages.success(request, '¡Has cerrado sesión correctamente!')
    return redirect('home')

@login_required(login_url='login')
def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/checkout.html', {'product': product})

@login_required(login_url='login')
def process_payment(request, product_id):
    if request.method != 'POST':
        return redirect('home')
    
    try:
        product = get_object_or_404(Product, id=product_id)
        
        if product.stock <= 0:
            messages.error(request, 'Producto agotado')
            return redirect('home')
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method', 'CARD')
        
        if not name or not email or not phone:
            messages.error(request, 'Todos los campos son obligatorios')
            return redirect('checkout', product_id=product.id)
        
        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, 'El teléfono debe tener 10 dígitos')
            return redirect('checkout', product_id=product.id)
        
        order = Order.objects.create(
            product=product,
            customer_name=name,
            customer_email=email,
            customer_phone=phone,
            address='No requerida',
            city='No requerida',
            payment_method=payment_method,
            total=product.get_price(),
            user=request.user,
            status='PAID'
        )
        
        product.stock -= 1
        product.save()
        
        # Enviar email de confirmación de pago
        send_payment_confirmation(order)
        
        request.session['last_order'] = order.order_number
        request.session.save()
        
        messages.success(request, '¡Pago exitoso! Revisa tu correo para la key del juego.')
        return redirect('success', order_id=order.order_number)
        
    except Exception as e:
        print(f"Error en pago: {e}")
        messages.error(request, 'Error al procesar el pago')
        return redirect('home')

def success(request, order_id):
    return render(request, 'store/success.html', {'order_id': order_id})

@login_required(login_url='login')
def profile(request):
    try:
        user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'store/profile.html', {
            'profile': user_profile,
            'orders': orders
        })
    except Exception as e:
        print(f"Error en profile: {e}")
        messages.error(request, 'Error al cargar el perfil')
        return redirect('home')