from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer, AccountManager

# Extend the default UserAdmin to show your custom fields
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Customer)
admin.site.register(AccountManager)
