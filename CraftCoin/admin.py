from django.contrib import admin
from .models import CustomUser, IPAddress, CartItem, Order, OrderItem, ServersTop

admin.site.register(CustomUser)
admin.site.register(IPAddress)
admin.site.register(CartItem)
admin.site.register(ServersTop)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['folio', 'user', 'total_price', 'created_at']
    inlines = [OrderItemInline]
    search_fields = ['folio', 'user__username', 'minecraft_name', 'discord_name'] 