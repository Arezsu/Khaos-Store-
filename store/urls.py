from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),
    path('process-payment/<int:product_id>/', views.process_payment, name='process_payment'),
    path('success/<str:order_id>/', views.success, name='success'),
]