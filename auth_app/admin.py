from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id','fullname','email', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'fullname')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
    )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Persönliche Informationen', {'fields': ('fullname',)}),
        ('Berechtigungen', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Wichtige Daten', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'fullname', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )
    ordering = ('fullname',)