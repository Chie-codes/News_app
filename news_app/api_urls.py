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

    # Create a new draft
    path("drafts/create/", api_views.DraftCreateView.as_view(), name="api_draft_create"),

    # Update or delete a specific draft (by ID)
    path("drafts/<int:pk>/", api_views.DraftUpdateView.as_view(), name="api_draft_update"),

    # List all articles under a specific publisher
    path("publishers/<int:pk>/articles/", api_views.PublisherArticleListView.as_view(), name="api_publisher_articles"),
]
