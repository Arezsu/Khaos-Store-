from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Order
from django.contrib.auth.models import User
import random
import string


@api_view(['GET'])
@permission_classes([AllowAny])
def get_products(request):
    """Listar todos los productos"""
    products = Product.objects.all()
    data = []
    for p in products:
        data.append({
            'id': p.id,
            'name': p.name,
            'price': p.get_price(),
            'category': p.category,
            'stock': p.stock,
            'image': p.image,
            'description': p.description
        })
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_detail(request, product_id):
    """Obtener detalle de un producto"""
    try:
        product = Product.objects.get(id=product_id)
        data = {
            'id': product.id,
            'name': product.name,
            'price': product.get_price(),
            'category': product.category,
            'stock': product.stock,
            'image': product.image,
            'description': product.description,
            'rating': product.rating,
            'reviews_count': product.reviews_count
        }
        return Response(data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Registrar un nuevo usuario"""
    try:
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return Response({'error': 'Faltan campos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'El usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'El email ya esta registrado'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        
        return Response({
            'success': True,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])  # Acepta GET y POST
@permission_classes([AllowAny])  # CAMBIADO: ahora no requiere autenticación
def create_order(request):
    """Crear una orden (ahora SIN autenticación requerida)"""
    
    # Si es GET, mostrar información útil
    if request.method == 'GET':
        return Response({
            'message': 'Usa POST para crear una orden',
            'campos_requeridos': {
                'product_id': 'ID del producto (ej: 1)',
                'quantity': 'Cantidad (ej: 1)',
                'phone': 'Teléfono (ej: 3001234567)',
                'address': 'Dirección (ej: Calle 123)',
                'city': 'Ciudad (ej: Ibague)',
                'payment_method': 'Método de pago (NEQUI, DAVIPLATA, TARJETA, EFECTY)'
            }
        })
    
    # Crear orden (POST)
    try:
        data = request.data
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        phone = data.get('phone', '0000000000')
        address = data.get('address', 'No especificada')
        city = data.get('city', 'No especificada')
        payment_method = data.get('payment_method', 'NEQUI')
        
        # Validar que existe product_id
        if not product_id:
            return Response({'error': 'Se requiere product_id'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar el producto
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': f'Producto con id {product_id} no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validar stock
        if product.stock < quantity:
            return Response({
                'error': f'Stock insuficiente. Stock disponible: {product.stock}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generar número de orden único
        order_number = 'KHAOS-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Crear la orden (sin usuario asociado, o con usuario anónimo)
        order = Order.objects.create(
            order_number=order_number,
            user=None,  # Usuario anónimo
            product=product,
            customer_name='Cliente API',  # Nombre genérico
            customer_email='api@cliente.com',  # Email genérico
            customer_phone=phone,
            address=address,
            city=city,
            payment_method=payment_method,
            total=product.get_price() * quantity,
            status='PENDING'
        )
        
        # Reducir stock
        product.stock -= quantity
        product.save()
        
        # Respuesta exitosa
        return Response({
            'success': True,
            'message': 'Orden creada exitosamente',
            'order_number': order.order_number,
            'total': float(order.total),
            'status': order.status,
            'producto': product.name,
            'cantidad': quantity,
            'total_pagado': f'${float(order.total):,} COP'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': f'Error al crear orden: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)