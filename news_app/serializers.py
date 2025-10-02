from rest_framework import serializers
from .models import Article, Publisher, Newsletter


class ArticleSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Publisher
        fields = [
            "id",
            "name",
            "members",
        ]


class NewsletterSerializer(serializers.ModelSerializer):
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
