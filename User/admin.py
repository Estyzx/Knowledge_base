from django.contrib import admin
from .models import  CustomUser
# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone', 'location')
    exclude = ('password','date_joined', 'last_login')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        ('个人信息',{'fields': ('username', 'phone', 'location')}),
        ('权限',{'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('其他',{'fields': ('date_joined', 'last_login')})
    )

admin.site.register(CustomUser, CustomUserAdmin)