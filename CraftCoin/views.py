from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Q
from difflib import SequenceMatcher
from mcstatus import JavaServer
from .forms import CustomUserCreationForm
from .models import CustomUser, IPAddress, CartItem
import logging
from django.apps import apps
from django.http import Http404
from django.contrib import messages
import random, string
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .forms import UserProfileForm, PasswordResetRequestForm, PasswordResetConfirmForm
from .models import CustomUser, CartItem, Order, OrderItem
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .decorators import login_required_with_message

logger = logging.getLogger(__name__)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

@transaction.atomic
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            ip_address = get_client_ip(request)
            if IPAddress.objects.filter(ip_address=ip_address).exists():
                return redirect('multiple_accounts_warning')
            
            user = form.save(commit=False)
            user.is_active = False
            user.is_email_verified = False
            user.save()
            IPAddress.objects.create(ip_address=ip_address)
            user.set_verification_code()
            try:
                send_verification_email(request, user)
                return render(request, 'Login/Register_Done.html')
            except Exception as e:
                logger.error(f"Error al enviar correo de verificación: {str(e)}")
                user.delete()
                IPAddress.objects.filter(ip_address=ip_address).delete()
                return redirect('register')
    else:
        form = CustomUserCreationForm()
    return render(request, 'Login/Register.html', {'form': form})

def multiple_accounts_warning(request):
    return render(request, 'Login/multiple_accounts_warning.html')

def login_view(request):
    next_url = request.GET.get('next', '')
    action = request.GET.get('action', '')
    
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_active and user.is_email_verified:
                auth_login(request, user)
                if next_url:
                    return redirect(next_url)
                return redirect('index')
            else:
                messages.error(request, "Tu cuenta no está activa o verificada.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'next': next_url,
        'action': action,
    }
    
    return render(request, 'Login/Login.html', context)

def verify(request, user_id, verification_code):
    try:
        user = CustomUser.objects.get(pk=user_id)
        if user.is_email_verified:
            return redirect('login')
        
        if user.is_verification_code_valid() and user.verification_code == verification_code:
            user.is_email_verified = True
            user.is_active = True
            user.verification_code = None
            user.save()
            return render(request, 'Login/verification_success.html')
        
        logger.warning(f"Verificación fallida para usuario: {user.username}")
        return render(request, 'Login/verification_failed.html')
    except CustomUser.DoesNotExist:
        logger.error(f"Intento de verificación para usuario no existente. ID: {user_id}")
        return render(request, 'Login/verification_failed.html')

def send_verification_email(request, user):
    subject = 'Verifica tu cuenta'
    context = {
        'user': user,
        'verification_url': request.build_absolute_uri(reverse('verify', args=[user.id, user.verification_code]))
    }
    html_message = render_to_string('emails/verification_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to = user.email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    logger.info(f"Correo de verificación enviado a: {to}")

def get_short_url(request):
    return render(request, 'earn_coins.html')
 
def email(request):
    return render(request, 'emails/password_reset_email.html')

def Index(request):
    return render(request, "Index.html")

def Servers_Top(request):
    apps_to_check = ['Server1', 'Server2']  # Agrega aquí todos los nombres de tus apps
    server_info_list = []

    for app_name in apps_to_check:
        try:
            ServerInfo = apps.get_model(app_name, 'ServerInfo')
            server_infos = ServerInfo.objects.all()
            for server_info in server_infos:
                server_info_list.append({
                    'app_name': app_name,
                    'ip_address': server_info.ip_address,
                    'port': server_info.port,
                    'image': server_info.image if server_info.image else None
                })
        except LookupError:
            # Si la app no existe, simplemente la saltamos
            continue

    return render(request, 'Servers-Top.html', {'server_info_list': server_info_list})

def New_Servers(request):
    return render(request, "New-Servers.html")

@login_required_with_message
@require_http_methods(["GET", "POST"])
@csrf_exempt
def Ganar_Coins(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            request.user.add_coin()
            return JsonResponse({'success': True, 'coins': request.user.coins})
        else:
            return JsonResponse({'success': False, 'message': 'Usuario no autenticado'})
    return render(request, "Ganar-Coins.html")


@login_required_with_message
def user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            changed_data = form.changed_data

            if changed_data:
                user = form.save(commit=False)
                
                if 'username' in changed_data:
                    user.username = form.cleaned_data['username']
                
                if 'profile_picture' in changed_data and form.cleaned_data['profile_picture']:
                    user.profile_picture = form.cleaned_data['profile_picture']
                    user.profile_picture_type = 'image/png'
                
                user.save()
                
                update_messages = []
                if 'username' in changed_data:
                    update_messages.append('nombre de usuario')
                if 'profile_picture' in changed_data and form.cleaned_data['profile_picture']:
                    update_messages.append('imagen de perfil')
                
                if update_messages:
                    messages.success(request, f"{' y '.join(update_messages).capitalize()} actualizado(s) con éxito.")
                else:
                    messages.info(request, 'No se realizaron cambios en tu perfil.')
            else:
                messages.info(request, 'No se realizaron cambios en tu perfil.')
            
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'Login/Perfil.html', {'form': form})


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                user.set_password_reset_code()
                send_password_reset_email(request, user)
                messages.success(request, 'Se ha enviado un correo con instrucciones para restablecer tu contraseña.')
                return redirect('password_reset_send_email')
            except CustomUser.DoesNotExist:
                messages.error(request, 'No existe una cuenta con ese correo electrónico.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'Login/password_reset_request.html', {'form': form})

def password_reset_confirm(request, user_id, reset_code):
    try:
        user = CustomUser.objects.get(pk=user_id)
        if not user.is_password_reset_code_valid() or user.password_reset_code != reset_code:
            messages.error(request, 'El enlace de restablecimiento de contraseña no es válido o ha expirado.')
            return redirect('password_reset_code_invalid')

        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.password_reset_code = None
                user.password_reset_code_created_at = None
                user.save()
                messages.success(request, 'Tu contraseña ha sido cambiada con éxito.')
                return redirect('password_reset_correct')
        else:
            form = PasswordResetConfirmForm()
        return render(request, 'Login/password_reset_confirm.html', {'form': form})
    except CustomUser.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('login')

def send_password_reset_email(request, user):
    subject = 'Restablece tu contraseña'
    
    # Generar la URL de restablecimiento de contraseña
    reset_url = request.build_absolute_uri(reverse('password_reset_confirm', args=[user.id, user.password_reset_code]))
    
    # Contexto para la plantilla HTML
    context = {
        'user': user,
        'reset_url': reset_url,
    }
    
    # Cargar la plantilla HTML
    html_message = render_to_string('emails/password_reset_email.html', context)
    
    # Generar un mensaje de texto simple (opcional)
    plain_message = strip_tags(html_message)
    
    # Configuración del correo
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    # Enviar el correo
    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

def custom_logout(request):
    logout(request)
    return redirect('/')

def terminos(request):
    return render(request, 'Login/terminos.html') 

def privacidad(request):
    return render(request, "Login/politicas.html")

def cookies(request):
    return render(request, "Login/Cookies.html")

def password_reset_send_email(request):
    return render(request, "Login/password_reset_send_email.html")

def password_reset_code_invalid(request):
    return render(request, "Login/password_reset_code_invalid.html")

def password_reset_correct(request):
    return render(request, "Login/password_reset_correct.html")

def dmca(request):
    return render(request, "Login/DMCA.html")

def get_connected_users(server_ip, port):
    try:
        # Conectarse al servidor de Minecraft usando mcstatus
        server = JavaServer.lookup(f"{server_ip}:{port}")
        
        # Obtener el estado del servidor
        status = server.status()
        
        # Retornar la cantidad de jugadores conectados
        return status.players.online
    except Exception as e:
        # Loguear el error en caso de que algo falle
        print(f"Error al obtener usuarios conectados del servidor {server_ip}:{port} - {str(e)}")
        return None



def app_list(request):
    apps_to_check = ['Server1', 'Server2']  # Agrega el nombre de tus apps secundarias aquí
    server_info_list = []

    for app_name in apps_to_check:
        ServerInfo = apps.get_model(app_name, 'ServerInfo')
        server_info = ServerInfo.objects.first()  # Obtenemos el primer servidor de cada app
        if server_info:
            # Agregamos la URL de la imagen al diccionario
            server_info_list.append({
                'app_name': app_name,
                'ip_address': server_info.ip_address,
                'port': server_info.port,
                'image_url': server_info.image.url if server_info.image else None  # Asegúrate de manejar el caso cuando no haya imagen
            })

    return render(request, 'New-Servers.html', {'server_info_list': server_info_list})


def modality_list(request, app):
    try:
        Product = apps.get_model(app, 'Product')
        products = Product.objects.all()  # Obtén todos los productos
        modalities = Product.objects.values_list('modality', flat=True).distinct()
        return render(request, 'modality_list.html', {
            'app': app,
            'modalities': modalities,
            'products': products  # Pasa los productos al contexto
        })
    except LookupError:
        raise Http404(f"No se encontró la aplicación '{app}'")

def category_list(request, app, modality):
    try:
        Product = apps.get_model(app, 'Product')
        # Filtra los productos por modalidad
        products = Product.objects.filter(modality=modality)
        categories = products.values_list('category', flat=True).distinct()
        return render(request, 'category_list.html', {
            'app': app,
            'modality': modality,
            'categories': categories,
            'products': products  # Pasa los productos al contexto
        })
    except LookupError:
        raise Http404(f"No se encontró la aplicación '{app}'")


def product_list(request, app, modality, category):
    Product = apps.get_model(app, 'Product')
    products = Product.objects.filter(modality=modality, category=category)
    return render(request, 'product_list.html', {'app': app, 'modality': modality, 'category': category, 'products': products})

def product_detail(request, app, modality, category, item):
    Product = apps.get_model(app, 'Product')
    product = get_object_or_404(Product, slug=item, modality=modality, category=category)
    return render(request, 'product_detail.html', {'product': product, 'app': app})
@login_required_with_message
def add_to_cart(request, app, product_id):
    if not request.user.is_authenticated:
        return redirect(f'/login/?next=/add-to-cart/{app}/{product_id}/')
    
    Product = apps.get_model(app, 'Product')
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product_id=product.id,
        app_name=app,
        defaults={'product_name': product.name, 'product_price': product.price}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.name} added to cart.")
    return redirect('cart')

@login_required_with_message
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Obtener la información de la imagen para cada item del carrito
    for item in cart_items:
        try:
            Product = apps.get_model(item.app_name, 'Product')
            product = Product.objects.get(id=item.product_id)
            item.image_url = product.image.url if product.image else None
        except Exception as e:
            # Si hay algún error al obtener la imagen, establecemos image_url como None
            item.image_url = None
            print(f"Error al obtener la imagen para el producto {item.product_name}: {str(e)}")
    
    total = cart_items.aggregate(
        total=Sum(F('product_price') * F('quantity'))
    )['total'] or 0
    
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

@login_required_with_message
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    action = request.POST.get('action')
    if action == 'increase':
        item.quantity += 1
    elif action == 'decrease':
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
            return redirect('cart')
    item.save()
    return redirect('cart')

@login_required_with_message
def checkout(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user)
        total = cart_items.aggregate(
            total=Sum(F('product_price') * F('quantity'))
        )['total'] or 0
        
        if request.user.coins < total:
            messages.error(request, "No tienes suficientes monedas para completar esta compra.")
            return redirect('cart')
        
        minecraft_name = request.POST.get('minecraft_name')
        discord_name = request.POST.get('discord_name')
        
        if not minecraft_name:
            messages.error(request, "El nombre de Minecraft es obligatorio.")
            return redirect('cart')
        
        folio = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        
        order = Order.objects.create(
            user=request.user,
            total_price=total,
            minecraft_name=minecraft_name,
            discord_name=discord_name,
            folio=folio,
            secret_key=secret_key
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_id=item.product_id,
                product_name=item.product_name,
                product_price=item.product_price,
                quantity=item.quantity,
                app_name=item.app_name
            )
        
        request.user.coins -= total
        request.user.save()
        
        cart_items.delete()
        
        # Enviar correo electrónico con el ticket de compra
        send_order_confirmation_email(request, order)
        
        messages.success(request, f"Pedido realizado con éxito. Tu número de folio es {folio}.")
        return redirect('order_confirmation', order_id=order.id)
    
    return redirect('cart')

@login_required_with_message
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})


@login_required_with_message
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})

def send_order_confirmation_email(request, order):
    subject = f'Tu pedido de CraftCoin - Folio {order.folio}'
    
    # Obtener información detallada de los productos
    order_items = []
    for item in order.orderitem_set.all():
        try:
            Product = apps.get_model(item.app_name, 'Product')
            product = Product.objects.get(id=item.product_id)
            order_items.append({
                'app_name': item.app_name,
                'modality': product.modality,
                'category': product.category,
                'name': item.product_name,
                'quantity': item.quantity,
                'price': item.product_price,
            })
        except Exception as e:
            logger.error(f"Error al obtener detalles del producto: {str(e)}")
            order_items.append({
                'app_name': item.app_name,
                'name': item.product_name,
                'quantity': item.quantity,
                'price': item.product_price,
            })

    context = {
        'order': order,
        'user': request.user,
        'order_items': order_items,
    }
    
    # Correo para el usuario
    html_message = render_to_string('emails/order_confirmation_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = request.user.email
    
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
    
    # Correo para el administrador
    admin_subject = f'Nuevo pedido - Folio {order.folio}'
    admin_html_message = render_to_string('emails/admin_order_notification_email.html', context)
    admin_plain_message = strip_tags(admin_html_message)
    admin_email = 'craftcoin.pedidos@gmail.com'
    
    send_mail(admin_subject, admin_plain_message, from_email, [admin_email], html_message=admin_html_message)


def search_servers(request):
    query = request.GET.get('q', '').strip().lower()
    apps_to_check = ['Server1', 'Server2']  # Asegúrate de que esta lista contenga los nombres correctos de tus apps
    results = []

    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    if query:
        for app_name in apps_to_check:
            try:
                ServerInfo = apps.get_model(app_name, 'ServerInfo')
                app_results = ServerInfo.objects.filter(
                    Q(ip_address__icontains=query) |
                    Q(port__icontains=query)
                )
                
                # Verificar si el nombre de la app coincide o es similar
                if query in app_name.lower() or similar(query, app_name.lower()) > 0.6:
                    app_results = ServerInfo.objects.all()

                for server in app_results:
                    results.append({
                        'app_name': app_name,
                        'ip_address': server.ip_address,
                        'port': server.port,
                        'image': server.image if server.image else None
                    })
            except LookupError:
                continue

    return render(request, 'search_results.html', {'results': results, 'query': query})