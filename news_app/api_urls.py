"""
api_urls.py

Defines the API endpoints for the News App using Django REST Framework.

Endpoints:
- /articles/ : List all approved and published articles
- /articles/<id>/ : Retrieve details of a specific approved and published article
- /drafts/ : List all drafts belonging to the logged-in journalist
- /drafts/create/ : Create a new draft (journalists only)
- /drafts/<id>/ : Update or delete a specific draft
- /publishers/<id>/articles/ : List all approved and published articles under a specific publisher
"""

from django.urls import path
from . import api_views

app_name = "news_api"

urlpatterns = [
    # List all approved + published articles
    path("articles/", api_views.ArticleListView.as_view(), name="api_articles"),

    # Get a single approved + published article by ID
    path("articles/<int:pk>/", api_views.ArticleDetailView.as_view(), name="api_article_detail"),

    # List all drafts (unpublished) by the logged-in journalist
    path("drafts/", api_views.DraftListView.as_view(), name="api_drafts"),

    # Create a new draft (journalists only)
    path("drafts/create/", api_views.DraftCreateView.as_view(), name="api_draft_create"),

    # Update or delete a specific draft (by ID)
    path("drafts/<int:pk>/", api_views.DraftUpdateView.as_view(), name="api_draft_update"),

    # List all approved + published articles under a specific publisher
    path("publishers/<int:pk>/articles/", api_views.PublisherArticleListView.as_view(), name="api_publisher_articles"),
]
