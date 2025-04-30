from django.contrib import admin
from .models import ServiceProvider, Product, Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'account_manager', 'created_at')  # Show created_at
    list_filter = ('created_at', 'account_manager')  # Allow filtering
    search_fields = ('customer__user__username', 'account_manager__user__username')

admin.site.register(ServiceProvider)
admin.site.register(Product)
