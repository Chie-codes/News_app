"""
URL configuration for news_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin site
    path("admin/", admin.site.urls),
    # News app URLs (articles, dashboard, auth)
    path("", include("news_app.urls")),
    # API endpoints (if you implement REST API)
    path("api/news/", include("news_app.api_urls", namespace="news_api")),

]
