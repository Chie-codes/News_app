from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from .models import Article, Publisher
from .serializers import ArticleSerializer


class ArticleListView(generics.ListAPIView):
    """
    List all approved + published articles.
    """
    queryset = Article.objects.filter(approved=True, published=True)
    serializer_class = ArticleSerializer


class ArticleDetailView(generics.RetrieveAPIView):
    """
    Get details of a single approved + published article by ID.
    """
    queryset = Article.objects.filter(approved=True, published=True)
    serializer_class = ArticleSerializer
    lookup_field = "pk"   # ensures /<id>/ works


class DraftListView(generics.ListAPIView):
    """
    List all drafts (unpublished articles) belonging to the logged-in journalist.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "journalist":
            return Article.objects.filter(journalist=user, published=False)
        return Article.objects.none()


class DraftCreateView(generics.CreateAPIView):
    """
    Allow journalists to create new draft articles.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "journalist":
            raise PermissionError("Only journalists can create drafts.")
        serializer.save(journalist=user, is_draft=True, published=False, approved=False)


class DraftUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """
    Allow journalists to update or delete their own drafts before approval/publishing.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "journalist":
            return Article.objects.filter(journalist=user, published=False)
        return Article.objects.none()


class PublisherArticleListView(generics.ListAPIView):
    """
    List all approved + published articles under a specific publisher.
    """
    serializer_class = ArticleSerializer

    def get_queryset(self):
        publisher_id = self.kwargs["pk"]
        publisher = get_object_or_404(Publisher, pk=publisher_id)
        return Article.objects.filter(
            publisher=publisher, approved=True, published=True
        )
