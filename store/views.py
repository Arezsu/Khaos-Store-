from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from .models import Product, Order, UserProfile, Cart, CartItem, Review
from .email_utils import send_welcome_email
from datetime import date
import re


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def get_or_create_cart(request):
    """Obtiene o crea un carrito para el usuario actual"""
    from .models import Order
    
    if request.user.is_authenticated:
        # Buscar carritos del usuario que NO tienen orden asociada
        user_carts = Cart.objects.filter(user=request.user)
        
        # Buscar un carrito sin orden
        cart = None
        for c in user_carts:
            if not Order.objects.filter(cart=c).exists():
                cart = c
                break
        
        # Si no hay carrito sin orden, crear uno nuevo
        if not cart:
            cart = Cart.objects.create(user=request.user)
        
        # Si el usuario tenía carrito anónimo, fusionar
        if request.session.session_key:
            anonymous_cart = Cart.objects.filter(
                session_key=request.session.session_key
            ).first()
            if anonymous_cart and anonymous_cart != cart:
                # Verificar que el carrito anónimo no tenga orden
                if not Order.objects.filter(cart=anonymous_cart).exists():
                    for item in anonymous_cart.items.all():
                        cart_item, created = CartItem.objects.get_or_create(
                            cart=cart,
                            product=item.product,
                            defaults={'quantity': item.quantity}
                        )
                        if not created:
                            cart_item.quantity += item.quantity
                            cart_item.save()
                    anonymous_cart.delete()
        return cart
        
    else:
        # Usuario anónimo
        if not request.session.session_key:
            request.session.create()
        
        # Buscar carrito anónimo sin orden
        session_carts = Cart.objects.filter(session_key=request.session.session_key)
        
        cart = None
        for c in session_carts:
            if not Order.objects.filter(cart=c).exists():
                cart = c
                break
        
        if not cart:
            cart = Cart.objects.create(session_key=request.session.session_key)
        
        return cart


# ============================================
# VISTAS PÚBLICAS
# ============================================

def home(request):
    products = Product.objects.all()
    
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )
    
    category = request.GET.get('category', '')
    if category:
        products = products.filter(category=category)
    
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'categories': categories,
    }
    
    return render(request, 'store/home.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'reviews': reviews,
        'user_review': user_review,
        'avg_rating': product.get_avg_rating(),
        'reviews_count': product.get_reviews_count(),
        'related_products': related_products,
    }
    
    return render(request, 'store/product_detail.html', context)


# ============================================
# VISTAS DE CARRITO
# ============================================

def cart_view(request):
    cart = get_or_create_cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = get_or_create_cart(request)
        
        quantity = int(request.POST.get('quantity', 1))
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} agregado al carrito')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_total_items': cart.get_total_items(),
                'cart_total': float(cart.get_total()),
                'message': f'{product.name} agregado al carrito'
            })
        
        return redirect('cart_view')
    
    return redirect('home')


def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        
        cart = cart_item.cart
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'item_total': float(cart_item.get_total()),
                'cart_total': float(cart.get_total()),
                'cart_total_items': cart.get_total_items()
            })
        
        return redirect('cart_view')


def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, 'Producto eliminado del carrito')
    return redirect('cart_view')


# ============================================
# VISTAS DE CHECKOUT
# ============================================

def checkout_single(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/checkout.html', {'product': product, 'is_cart': False})


def checkout_cart(request):
    cart = get_or_create_cart(request)
    
    if not cart or not cart.items.exists():
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('cart_view')
    
    return render(request, 'store/checkout.html', {'cart': cart, 'is_cart': True})


def process_payment(request, product_id=None):
    if request.method != 'POST':
        return redirect('home')
    
    try:
        is_cart = request.POST.get('is_cart') == 'true'
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method', 'NEQUI')
        
        if not name or not email or not phone:
            messages.error(request, 'Todos los campos son obligatorios')
            if is_cart:
                return redirect('checkout_cart')
            else:
                return redirect('checkout', product_id=product_id)
        
        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, 'El teléfono debe tener 10 dígitos')
            if is_cart:
                return redirect('checkout_cart')
            else:
                return redirect('checkout', product_id=product_id)
        
        if is_cart:
            cart = get_or_create_cart(request)
            if not cart or not cart.items.exists():
                messages.error(request, 'Carrito vacío')
                return redirect('cart_view')
            
            # Verificar stock
            for item in cart.items.all():
                if item.product.stock < item.quantity:
                    messages.error(request, f'No hay suficiente stock de {item.product.name}')
                    return redirect('cart_view')
            
            # CREAR ORDEN SIN PRODUCT (solo con cart)
            order = Order.objects.create(
                cart=cart,
                customer_name=name,
                customer_email=email,
                customer_phone=phone,
                address='No requerida',
                city='No requerida',
                payment_method=payment_method,
                total=cart.get_total(),
                user=request.user if request.user.is_authenticated else None,
                status='PENDING'
                # NO incluir product aquí
            )
        else:
            product = get_object_or_404(Product, id=product_id)
            
            if product.stock <= 0:
                messages.error(request, 'Producto agotado')
                return redirect('home')
            
            # CREAR ORDEN CON PRODUCT (individual)
            order = Order.objects.create(
                product=product,
                customer_name=name,
                customer_email=email,
                customer_phone=phone,
                address='No requerida',
                city='No requerida',
                payment_method=payment_method,
                total=product.get_price(),
                user=request.user if request.user.is_authenticated else None,
                status='PENDING'
            )
        
        order.send_pending_email()
        
        request.session['last_order'] = order.order_number
        
        messages.success(request, 'Orden creada. Revisa tu correo para los datos de pago.')
        return redirect('success', order_id=order.order_number)
        
    except Exception as e:
        print(f"Error en pago: {e}")
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        if is_cart:
            return redirect('cart_view')
        else:
            return redirect('home')


def success(request, order_id):
    return render(request, 'store/success.html', {'order_id': order_id})


# ============================================
# VISTAS DE RESEÑAS
# ============================================

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 3))
        comment = request.POST.get('comment', '').strip()
        
        if not comment:
            messages.error(request, 'Por favor escribe un comentario')
            return redirect('product_detail', product_id=product_id)
        
        review, created = Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': rating,
                'comment': comment
            }
        )
        
        avg_rating = product.get_avg_rating()
        product.rating = avg_rating
        product.reviews_count = product.get_reviews_count()
        product.save()
        
        messages.success(request, '¡Gracias por tu reseña!' if created else 'Reseña actualizada')
        return redirect('product_detail', product_id=product_id)
    
    return redirect('product_detail', product_id=product_id)


# ============================================
# VISTAS DE AUTENTICACIÓN
# ============================================

def register(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            phone = request.POST.get('phone', '')
            birth_year = request.POST.get('birth_year')
            birth_month = request.POST.get('birth_month')
            birth_day = request.POST.get('birth_day')
            
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
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            try:
                if birth_year and birth_month and birth_day:
                    birth_date = date(int(birth_year), int(birth_month), int(birth_day))
                    UserProfile.objects.create(
                        user=user,
                        phone=phone,
                        birth_date=birth_date
                    )
                else:
                    UserProfile.objects.create(
                        user=user,
                        phone=phone
                    )
            except:
                UserProfile.objects.create(
                    user=user,
                    phone=phone
                )
            
            login(request, user)
            request.session.save()
            
            send_welcome_email(user)
            
            return JsonResponse({'success': True, 'redirect': '/'})
            
        except Exception as e:
            print(f"ERROR EN REGISTRO: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    # Crear listas para los selects del formulario
    current_year = date.today().year
    years = list(range(current_year - 50, current_year + 1))
    years.reverse()
    
    months = list(range(1, 13))
    days = list(range(1, 32))
    
    return render(request, 'store/register.html', {
        'years': years,
        'months': months,
        'days': days
    })


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido de vuelta {username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'store/login.html')


def custom_logout(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente!')
    return redirect('home')


# ============================================
# VISTAS DE PERFIL Y CAMBIO DE CONTRASEÑA
# ============================================

@login_required
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


@login_required
def change_password(request):
    """Vista para cambiar contraseña desde el perfil"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '¡Tu contraseña ha sido cambiada exitosamente!')
            return redirect('profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'store/change_password.html', {'form': form})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'PENDING':
        order.status = 'CANCELLED'
        order.save()
        messages.success(request, f'Orden #{order.order_number} cancelada correctamente.')
    else:
        messages.error(request, 'No se puede cancelar esta orden porque ya fue procesada.')
    
    return redirect('profile')