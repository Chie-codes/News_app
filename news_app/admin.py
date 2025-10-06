from django.contrib import admin
from .models import CustomUser, Publisher, Article, Newsletter
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the CustomUser model.
    Extends Django's built-in UserAdmin to display extra fields such as 'role'.
    """
    model = CustomUser
    list_display = ["username", "email", "role", "is_staff"]  # Show these fields in admin list view


# Register remaining models so they appear in the Django admin site
admin.site.register(Publisher)   # Manage publishers in the admin interface
admin.site.register(Article)     # Manage articles in the admin interface
admin.site.register(Newsletter)  # Manage newsletters in the admin interface
