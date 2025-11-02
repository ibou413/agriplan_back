from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('profile_image', 'professional_activity', 'region', 'account_type'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'classes': ('wide',),
            'fields': ('profile_image', 'professional_activity', 'region', 'account_type'),
        }),
    )

    list_display = ['username', 'first_name', 'last_name', 'account_type', 'region']
    list_filter = ['account_type', 'region']

admin.site.register(CustomUser, CustomUserAdmin)
