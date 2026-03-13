from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import Product, Order, UserProfile
from datetime import date
import traceback

def home(request):
    try:
        query = request.GET.get('q', '')
        if query:
            products = Product.objects.filter(name__icontains=query)
        else:
            products = Product.objects.all()
        return render(request, 'store/home.html', {'products': products, 'query': query})
    except Exception as e:
        print(f"ERROR EN HOME: {e}")
        return render(request, 'store/home.html', {'products': [], 'query': ''})

def register(request):
    if request.method == 'POST':
        try:
            print("=" * 50)
            print("INICIANDO PROCESO DE REGISTRO")
            
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            phone = request.POST.get('phone', '')
            birth_year = request.POST.get('birth_year')
            birth_month = request.POST.get('birth_month')
            birth_day = request.POST.get('birth_day')
            
            print(f"Datos recibidos: {username}, {email}, {phone}, {birth_year}-{birth_month}-{birth_day}")
            
            # Validaciones básicas
            if not username or not email or not password:
                messages.error(request, 'Todos los campos son obligatorios')
                return redirect('register')
            
            if password != confirm_password:
                messages.error(request, 'Las contraseñas no coinciden')
                return redirect('register')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El usuario ya existe')
                return redirect('register')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'El email ya está registrado')
                return redirect('register')
            
            if len(phone) != 10 or not phone.isdigit():
                messages.error(request, 'El teléfono debe tener exactamente 10 dígitos')
                return redirect('register')
            
            # Validar fecha
            try:
                birth_date = date(int(birth_year), int(birth_month), int(birth_day))
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                if age < 18:
                    messages.error(request, 'Debes ser mayor de 18 años para registrarte')
                    return redirect('register')
            except (ValueError, TypeError) as e:
                print(f"Error en fecha: {e}")
                messages.error(request, 'Fecha de nacimiento inválida')
                return redirect('register')
            
            # Crear usuario
            print("Creando usuario...")
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            print(f"Usuario creado: {user.id}")
            
            # Crear perfil
            print("Creando perfil...")
            try:
                profile = UserProfile.objects.create(
                    user=user,
                    phone=phone,
                    birth_date=birth_date
                )
                print(f"Perfil creado para: {profile.user.username}")
            except Exception as e:
                print(f"Error creando perfil: {e}")
                user.delete()
                messages.error(request, 'Error al crear el perfil')
                return redirect('register')
            
            # Iniciar sesión
            print("Iniciando sesión...")
            login(request, user)
            print("Sesión iniciada correctamente")
            
            messages.success(request, '¡Registro exitoso! Bienvenido a KHAOS STORE')
            
            # Redirigir
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                print(f"Redirigiendo a: {next_url}")
                return redirect(next_url)
            
            print("Redirigiendo a home")
            return redirect('home')
            
        except IntegrityError as e:
            print(f"ERROR DE INTEGRIDAD: {e}")
            messages.error(request, 'Error en la base de datos. Intenta de nuevo.')
            return redirect('register')
            
        except Exception as e:
            print(f"❌ ERROR CRÍTICO: {e}")
            traceback.print_exc()
            messages.error(request, 'Error en el registro. Por favor intenta de nuevo.')
            return redirect('register')
    
    return render(request, 'store/register.html')

@login_required(login_url='login')
def checkout(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        return render(request, 'store/checkout.html', {'product': product})
    except Exception as e:
        print(f"ERROR EN CHECKOUT: {e}")
        messages.error(request, 'Producto no encontrado')
        return redirect('home')

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
        
        try:
            order.send_confirmation_email()
            order.send_game_key()
        except Exception as e:
            print(f"Error en emails: {e}")
        
        request.session['last_order'] = order.order_number
        
        messages.success(request, '¡Pago exitoso! Revisa tu correo')
        return redirect('success', order_id=order.order_number)
        
    except Exception as e:
        print(f"Error en pago: {e}")
        traceback.print_exc()
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
        traceback.print_exc()
        messages.error(request, 'Error al cargar el perfil')
        return redirect('home')