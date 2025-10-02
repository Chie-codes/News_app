from django.contrib import admin
from .models import CustomUser, Publisher, Article, Newsletter
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["username", "email", "role", "is_staff"]


admin.site.register(Publisher)
admin.site.register(Article)
admin.site.register(Newsletter)
