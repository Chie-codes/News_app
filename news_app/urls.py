"""
urls.py

This module defines all URL patterns for the News App, including:
- Public views (article list and detail)
- Journalist actions (create, edit, delete articles)
- Editor actions (approve articles)
- Publisher actions (publish articles)
- User authentication (register, login, logout)
- Dashboard
- API endpoints
"""

from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = "news_app"

urlpatterns = [
    # Home page: list of approved articles
    path("", views.article_list, name="article_list"),
    
    # Article detail page
    path("article/<int:pk>/", views.article_detail, name="article_detail"),
    
    # Journalist: create new article
    path("create-article/", views.create_article, name="create_article"),
    
    # Journalist & Editor: edit an article
    path("article/<int:pk>/edit/", views.article_edit, name="article_edit"),
    
    # Journalist & Editor: delete an article
    path("article/<int:pk>/delete/", views.article_delete, name="article_delete"),
    
    # Editor: approve article
    path("article/<int:pk>/approve/", views.article_approve, name="article_approve"),
    
    # Publisher: publish article
    path("article/<int:pk>/publish/", views.article_publish, name="article_publish"),
    path('article/<int:pk>/publish_independent/', views.publish_independent_article, name='publish_independent_article'),
    
    # User dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # User registration
    path("register/", views.register, name="register"),
    
    # Login & logout using Django's built-in auth views
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="news_app/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # API URLs
    path("api/", include("news_app.api_urls", namespace="news_api")),
]
