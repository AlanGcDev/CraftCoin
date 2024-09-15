from django.contrib import admin
from .models import Product, ServerInfo

admin.site.register(Product)
admin.site.register(ServerInfo)