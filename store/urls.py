from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Vistas principales
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Autenticación
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # RECUPERACIÓN DE CONTRASEÑA
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='store/password_reset.html',
             email_template_name='emails/password_reset_email.html',
             subject_template_name='emails/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='store/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='store/password_reset_confirm.html',
             success_url='/reset/done/'
         ),
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='store/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # Carrito
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    
    # Checkout
    path('checkout/<int:product_id>/', views.checkout_single, name='checkout'),
    path('checkout/cart/', views.checkout_cart, name='checkout_cart'),
    path('process-payment/<int:product_id>/', views.process_payment, name='process_payment'),
    path('process-payment/cart/', views.process_payment, {'product_id': None}, name='process_payment_cart'),
    path('success/<str:order_id>/', views.success, name='success'),
    
    # Reseñas
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
    
    # Órdenes
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
]