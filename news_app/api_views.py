"""
api_views.py

Defines API views for Articles in the News App using Django REST Framework.

Views:
- ArticleListView: List all approved and published articles.
- ArticleDetailView: Retrieve details of a single approved and published article.
- DraftListView: List all drafts belonging to the logged-in journalist.
- DraftCreateView: Create a new draft article.
- DraftUpdateView: Update or delete a journalist's own draft.
- PublisherArticleListView: List all approved and published articles for a specific publisher.
"""

from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from .models import Article, Publisher
from .serializers import ArticleSerializer


class ArticleListView(generics.ListAPIView):
    """
    API endpoint to list all approved and published articles.
    """
    queryset = Article.objects.filter(approved=True, published=True)
    serializer_class = ArticleSerializer


class ArticleDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve details of a single approved and published article by ID.
    """
    queryset = Article.objects.filter(approved=True, published=True)
    serializer_class = ArticleSerializer
    lookup_field = "pk"  # ensures /<id>/ works


class DraftListView(generics.ListAPIView):
    """
    API endpoint to list all unpublished draft articles for the logged-in journalist.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return drafts for the currently logged-in journalist.
        """
        user = self.request.user
        if user.role == "journalist":
            return Article.objects.filter(journalist=user, published=False)
        return Article.objects.none()


class DraftCreateView(generics.CreateAPIView):
    """
    API endpoint for journalists to create new draft articles.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Assign the logged-in journalist as the author and mark the article as draft.
        """
        user = self.request.user
        if user.role != "journalist":
            raise PermissionError("Only journalists can create drafts.")
        serializer.save(journalist=user, is_draft=True, published=False, approved=False)


class DraftUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for journalists to retrieve, update, or delete their own drafts before approval/publishing.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return drafts owned by the logged-in journalist.
        """
        user = self.request.user
        if user.role == "journalist":
            return Article.objects.filter(journalist=user, published=False)
        return Article.objects.none()


class PublisherArticleListView(generics.ListAPIView):
    """
    API endpoint to list all approved and published articles under a specific publisher.
    """
    serializer_class = ArticleSerializer

    def get_queryset(self):
        """
        Return approved and published articles for the given publisher ID.
        """
        publisher_id = self.kwargs["pk"]
        publisher = get_object_or_404(Publisher, pk=publisher_id)
        return Article.objects.filter(
            publisher=publisher, approved=True, published=True
        )
