from .models import Cart, Order

def cart_context(request):
    """Contexto global para el carrito disponible en todas las plantillas"""
    cart = None
    
    if request.user.is_authenticated:
        # Buscar carritos del usuario que NO tienen orden asociada
        user_carts = Cart.objects.filter(user=request.user)
        
        # Filtrar los que no tienen orden
        cart = None
        for c in user_carts:
            if not Order.objects.filter(cart=c).exists():
                cart = c
                break
        
        # Si no hay carrito sin orden, crear uno nuevo
        if not cart:
            cart = Cart.objects.create(user=request.user)
            
    elif request.session.session_key:
        # Usuario anónimo
        session_carts = Cart.objects.filter(session_key=request.session.session_key)
        
        cart = None
        for c in session_carts:
            if not Order.objects.filter(cart=c).exists():
                cart = c
                break
        
        if not cart:
            cart = Cart.objects.create(session_key=request.session.session_key)
    
    if cart:
        return {
            'cart': cart,
            'cart_total_items': cart.get_total_items(),
            'cart_total': cart.get_total()
        }
    
    return {
        'cart': None,
        'cart_total_items': 0,
        'cart_total': 0
    }