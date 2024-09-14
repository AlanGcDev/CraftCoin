from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import random, string
import base64

class CustomUser(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=100, blank=True, null=True)
    verification_code_created_at = models.DateTimeField(null=True, blank=True)
    coins = models.IntegerField(default=0)
    profile_picture = models.BinaryField(null=True, blank=True, editable=True)  # Añade editable=True
    profile_picture_type = models.CharField(max_length=10, null=True, blank=True)
    password_reset_code = models.CharField(max_length=100, blank=True, null=True)
    password_reset_code_created_at = models.DateTimeField(null=True, blank=True)
    
    def is_verification_code_valid(self):
        if not self.verification_code_created_at:
            return False
        return (timezone.now() - self.verification_code_created_at) < timedelta(hours=24)

    def set_verification_code(self):
        self.verification_code = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        self.verification_code_created_at = timezone.now()
        self.save()

    def set_password_reset_code(self):
        self.password_reset_code = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        self.password_reset_code_created_at = timezone.now()
        self.save()

    def is_password_reset_code_valid(self):
        if not self.password_reset_code_created_at:
            return False
        return (timezone.now() - self.password_reset_code_created_at) < timedelta(hours=1)

    def add_coin(self):
        self.coins += 1
        self.save(update_fields=['coins'])
        
    def get_profile_picture_base64(self):
        if self.profile_picture:
            return f"data:{self.profile_picture_type};base64,{base64.b64encode(self.profile_picture).decode('utf-8')}"
        return None

# ... (el resto del archivo permanece igual)
    
class IPAddress(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ip_address
    
class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    app_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.quantity} of {self.product_name} from {self.app_name}"

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    minecraft_name = models.CharField(max_length=100)
    discord_name = models.CharField(max_length=100, blank=True, null=True)
    folio = models.CharField(max_length=20, unique=True)
    secret_key = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.folio} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    app_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.quantity} of {self.product_name} from {self.app_name} in Order {self.order.folio}"

class ServersTop(models.Model):
    app_name = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=255)
    port = models.IntegerField()
    image = models.ImageField(upload_to='servers-tops/')

    def __str__(self):
        return f"{self.app_name} - {self.ip_address}:{self.port}"    