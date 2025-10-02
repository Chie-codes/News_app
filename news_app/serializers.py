"""
serializers.py

This module defines Django REST Framework serializers for the News App.

- ArticleSerializer: Serializes Article model fields for API endpoints.
- PublisherSerializer: Serializes Publisher model fields for API endpoints.
- NewsletterSerializer: Serializes Newsletter model fields for API endpoints.
"""

from rest_framework import serializers
from .models import Article, Publisher, Newsletter


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model, used in API endpoints."""
    
    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "journalist",
            "publisher",
            "approved",
            "published",
            "is_draft",
            "created_at",
            "published_at",
        ]
        read_only_fields = [
            "approved",
            "published",
            "created_at",
            "published_at",
        ]


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for Publisher model, used in API endpoints."""
    
    class Meta:
        model = Publisher
        fields = [
            "id",
            "name",
            "members",
        ]


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for Newsletter model, used in API endpoints."""
    
    class Meta:
        model = Newsletter
        fields = [
            "id",
            "title",
            "content",
            "journalist",
            "created_at",
        ]
        read_only_fields = ["created_at"]
