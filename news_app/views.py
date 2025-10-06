"""
views.py

This module contains all the view functions for the News App, including:
- User registration and authentication
- Dashboard views based on user roles
- Article CRUD operations (create, edit, delete)
- Article approval and publishing workflows
- Public views for listing and viewing articles
- API endpoints for retrieving articles
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.utils.timezone import now

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import CustomUserCreationForm, ArticleForm
from .models import Article, Publisher
from .serializers import ArticleSerializer


# -----------------------
# User Registration
# -----------------------
def register(request):
    """
    Handle user registration.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the registration page or redirects to dashboard on success.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group_mapping = {
                "reader": "Readers",
                "journalist": "Journalists",
                "editor": "Editors",
                "publisher": "Publishers",
            }
            group_name = group_mapping.get(user.role)
            if group_name:
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
            login(request, user)
            return redirect("news_app:dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "news_app/register.html", {"form": form})


# -----------------------
# Dashboard
# -----------------------
@login_required
def dashboard(request):
    """
    Display the dashboard page according to the user's role.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the dashboard template with user-specific data.
    """
    user = request.user
    role = user.role

    my_articles = Article.objects.filter(journalist=user) if role == "journalist" else None
    pending_articles = Article.objects.filter(approved=False) if role == "editor" else None
    approved_articles = Article.objects.filter(approved=True, published=False) if role == "publisher" else None
    published_articles = Article.objects.filter(approved=True, published=True) if role == "reader" else None

    return render(request, "news_app/dashboard.html", {
        "is_journalist": role == "journalist",
        "is_editor": role == "editor",
        "is_reader": role == "reader",
        "is_publisher": role == "publisher",
        "my_articles": my_articles,
        "pending_articles": pending_articles,
        "approved_articles": approved_articles,
        "published_articles": published_articles,
    })


# -----------------------
# Article CRUD
# -----------------------
@login_required
def create_article(request):
    """
    Create a new article by a journalist.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the article creation page or redirects to dashboard.
    """
    if request.user.role != "journalist":
        return HttpResponseForbidden("You are not allowed to create articles.")
    
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.journalist = request.user
            article.is_draft = True
            article.save()
            return redirect("news_app:dashboard")
    else:
        form = ArticleForm()
    return render(request, "news_app/create_article.html", {"form": form})


@login_required
def article_edit(request, pk):
    """
    Edit an existing article. Only the author or editor can edit.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): Primary key of the article.

    Returns:
        HttpResponse: Renders the article update page or redirects on success.
    """
    article = get_object_or_404(Article, pk=pk)
    if request.user != article.journalist and request.user.role != "editor":
        return HttpResponseForbidden("You do not have permission to edit this article.")

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Article updated successfully.")
            return redirect("news_app:dashboard")
    else:
        form = ArticleForm(instance=article)
    return render(request, "news_app/update_article.html", {"form": form, "article": article})


@login_required
def article_delete(request, pk):
    """
    Delete an article. Only the author or editor can delete.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): Primary key of the article.

    Returns:
        HttpResponse: Renders delete confirmation page or redirects on success.
    """
    article = get_object_or_404(Article, pk=pk)
    if request.user != article.journalist and request.user.role != "editor":
        return HttpResponseForbidden("You do not have permission to delete this article.")

    if request.method == "POST":
        article.delete()
        messages.success(request, "Article deleted successfully.")
        return redirect("news_app:dashboard")

    return render(request, "news_app/delete_article.html", {"article": article})


# -----------------------
# Article Approval
# -----------------------
@login_required
def article_approve(request, pk):
    """
    Approve an article. Only editors can approve articles of their publisher.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): Primary key of the article.

    Returns:
        HttpResponseRedirect: Redirects to dashboard.
    """
    if request.user.role != "editor":
        return HttpResponseForbidden("Only editors can approve articles.")

    article = get_object_or_404(Article, pk=pk)

    if article.publisher and request.user not in article.publisher.members.all():
        return HttpResponseForbidden("You must be an editor of this publisher to approve.")

    if request.method == "POST":
        if not article.approved:
            article.approved = True
            article.is_draft = False
            article.save()
            send_mail(
                subject=f"Your article '{article.title}' was approved!",
                message="Congratulations! Your article has been approved by an editor.",
                from_email="admin@news.com",
                recipient_list=[article.journalist.email],
                fail_silently=True,
            )
            messages.success(request, f"Article '{article.title}' approved successfully.")
        else:
            messages.info(request, "Article is already approved.")

    return redirect("news_app:dashboard")


# -----------------------
# Article Publish
# -----------------------
@login_required
def article_publish(request, pk):
    """
    Publish an article. Editors or publishers can publish articles for their publishers.
    Independent journalists can publish their own articles.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): Primary key of the article.

    Returns:
        HttpResponseRedirect: Redirects to dashboard.
    """
    article = get_object_or_404(Article, pk=pk)

    if article.publisher:
        if request.user.role in ["publisher", "editor"] and request.user not in article.publisher.members.all():
            return HttpResponseForbidden("You must be a member/editor of this publisher to publish.")
    else:
        if request.user != article.journalist:
            return HttpResponseForbidden("Only the journalist can publish their independent article.")

    if request.method == "POST":
        article.published = True
        article.is_draft = False
        article.published_at = now()
        article.save()
        messages.success(request, f"Article '{article.title}' published successfully.")

    return redirect("news_app:dashboard")


@login_required
def publish_independent_article(request, pk):
    """
    Publish an independent article by its authoring journalist.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): Primary key of the article.

    Returns:
        HttpResponseRedirect: Redirects to dashboard.
    """
    article = get_object_or_404(Article, pk=pk)

    if article.publisher:
        return HttpResponseForbidden("This article belongs to a publisher. Use the normal publish flow.")
    if request.user != article.journalist:
        return HttpResponseForbidden("Only the journalist can publish this article.")

    if request.method == "POST":
        article.published = True
        article.is_draft = False
        article.published_at = now()
        article.save()
        messages.success(request, f"Your article '{article.title}' has been published.")
    
    return redirect("news_app:dashboard")


# -----------------------
# Public Views
# -----------------------
def article_list(request):
    """
    Display a list of approved and published articles.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders article list page.
    """
    articles = Article.objects.filter(approved=True, published=True).order_by("-created_at")
    return render(request, "news_app/article_list.html", {"articles": articles})


@login_required
def article_detail(request, pk):
    """
    Display a single article. Readers cannot view unpublished articles.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): Primary key of the article.

    Returns:
        HttpResponse: Renders article detail page.
    """
    article = get_object_or_404(Article, pk=pk)
    
    if request.user.role == "reader" and not article.published:
        return HttpResponseForbidden("You cannot view unpublished articles.")

    return render(request, "news_app/article_detail.html", {"article": article})


# -----------------------
# API Endpoints
# -----------------------
@api_view(["GET"])
def api_articles(request):
    """
    API endpoint to list all approved and published articles.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: Serialized list of articles.
    """
    articles = Article.objects.filter(approved=True, published=True).order_by("-created_at")
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def api_article_detail(request, pk):
    """
    API endpoint to retrieve a single approved and published article.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): Primary key of the article.

    Returns:
        Response: Serialized article data.
    """
    article = get_object_or_404(Article, pk=pk, approved=True, published=True)
    serializer = ArticleSerializer(article)
    return Response(serializer.data)
