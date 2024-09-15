from django.urls import path
from django.conf.urls import handler500
from . import views
from .views import custom_error_view
handler500 = custom_error_view

urlpatterns = [
    
    path('', views.Index, name='index'),
    path('servers-top/', views.Servers_Top, name='servers-top'),
    path('ganar-coins/', views.Ganar_Coins, name='ganar-coins'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('perfil/', views.user_profile, name='perfil'),
    path('logout/', views.custom_logout, name='logout'),
    path('multiple-accounts-warning/', views.multiple_accounts_warning, name='multiple_accounts_warning'),
    path('verify/<int:user_id>/<str:verification_code>/', views.verify, name='verify'),
    path('terminos-condiciones/', views.terminos, name='terminos'),
    path('politicas-privacidad/', views.privacidad, name='privacidad'),
    path('politicas-cookies/', views.cookies, name='cookies'),
    path('dmca/', views.dmca, name='dmca'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<int:user_id>/<str:reset_code>/', views.password_reset_confirm, name='password_reset_confirm'),
    path("password_reset_send_email/", views.password_reset_send_email, name="password_reset_send_email"),
    path("password_reset_code_invalid/", views.password_reset_code_invalid, name="password_reset_code_invalid"),
    path("password_reset_correct/", views.password_reset_correct, name="password_reset_correct"),
    path("email/", views.email, name="email"),
    path('new-servers/', views.app_list, name='app_list'),
    path('search/', views.search_servers, name='search_servers'),
    
    # Rutas específicas del carrito y checkout
    path('cart/', views.cart, name='cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('add-to-cart/<str:app>/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    # Rutas para las apps de productos (deben ir al final)
    path('<str:app>/', views.modality_list, name='modality_list'),
    path('<str:app>/<str:modality>/', views.category_list, name='category_list'),
    path('<str:app>/<str:modality>/<str:category>/', views.product_list, name='product_list'),
    path('<str:app>/<str:modality>/<str:category>/<slug:item>/', views.product_detail, name='product_detail'),
]