from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.ps5_launcher, name='ps5_launcher'),
    path('tienda/', views.home, name='home'),
    path('producto/<int:product_id>/', views.product_detail, name='product_detail'),
    
    path('registro/', views.register, name='register'),
    path('ingresar/', views.user_login, name='login'),
    path('salir/', views.custom_logout, name='logout'),
    path('perfil/', views.profile, name='profile'),
    path('cambiar-contrasena/', views.change_password, name='change_password'),
    
    path('recuperar-contrasena/', 
         auth_views.PasswordResetView.as_view(
             template_name='store/password_reset.html',
             email_template_name='emails/password_reset_email.html',
             subject_template_name='emails/password_reset_subject.txt',
             success_url='/recuperar-contrasena/enviado/'
         ),
         name='password_reset'),
    
    path('recuperar-contrasena/enviado/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='store/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='store/password_reset_confirm.html',
             success_url='/reset/completado/'
         ),
         name='password_reset_confirm'),
    
    path('reset/completado/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='store/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    path('carrito/', views.cart_view, name='cart_view'),
    path('carrito/agregar/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/actualizar/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('carrito/eliminar/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    
    path('comprar/<int:product_id>/', views.checkout_single, name='checkout'),
    path('comprar/carrito/', views.checkout_cart, name='checkout_cart'),
    path('procesar-pago/<int:product_id>/', views.process_payment, name='process_payment'),
    path('procesar-pago/carrito/', views.process_payment, {'product_id': None}, name='process_payment_cart'),
    path('exito/<str:order_id>/', views.success, name='success'),
    
    path('resena/agregar/<int:product_id>/', views.add_review, name='add_review'),
    
    path('cancelar-orden/<int:order_id>/', views.cancel_order, name='cancel_order'),
]