"""
models.py

Defines the data models for the News App.

Models:
- CustomUser: Extends AbstractUser with roles (Reader, Journalist, Editor, Publisher)
- Publisher: Represents a publishing organization with members
- Article: Represents articles written by journalists and managed by editors/publishers
- Newsletter: Represents newsletters sent by journalists to readers
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone


class CustomUser(AbstractUser):
    """
    Custom user model with roles:
    - Reader: subscribes to publishers/journalists
    - Journalist: writes articles & newsletters
    - Editor: approves articles (and can publish if part of a publisher)
    - Publisher: manages a team of journalists/editors
    """

    ROLE_CHOICES = [
        ("reader", "Reader"),
        ("journalist", "Journalist"),
        ("editor", "Editor"),
        ("publisher", "Publisher"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="reader")

    # Readers can subscribe to multiple publishers
    subscriptions_publishers = models.ManyToManyField(
        "Publisher", blank=True, related_name="subscribers"
    )

    # Readers can follow multiple journalists
    subscriptions_journalists = models.ManyToManyField(
        "self", blank=False, symmetrical=False, related_name="followers"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


class Publisher(models.Model):
    """
    Publisher with members (editors and journalists).
    Editors can approve/publish, Journalists can submit drafts.
    """

    name = models.CharField(max_length=255)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="publishers",
        blank=True,
    )

    def editors(self):
        """Return all members with the editor role."""
        return self.members.filter(role="editor")

    def journalists(self):
        """Return all members with the journalist role."""
        return self.members.filter(role="journalist")

    def has_member(self, user):
        """Check if a user is part of this publisher (editor or journalist)."""
        return self.members.filter(id=user.id).exists()

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Article model representing a news article written by a journalist.
    Can belong to a publisher, be approved, published, or saved as a draft.
    """

    title = models.CharField(max_length=255)
    content = models.TextField()

    journalist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
        null=True,
        blank=True,
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="articles",
        null=True,
        blank=True,
    )

    approved = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def can_publish(self, user):
        """
        Determine if a given user can publish this article.
        Editors can publish if they belong to the same publisher.
        Publishers can always publish articles under their organization.
        Independent journalists can publish their own articles.
        """
        if self.publisher:
            return (
                user.role == "publisher" and self.publisher.has_member(user)
            ) or (
                user.role == "editor" and self.publisher.has_member(user)
            )
        return user == self.journalist and user.role == "journalist"

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """
    Newsletter created by a journalist and sent to readers.
    """

    title = models.CharField(max_length=255)
    content = models.TextField()

    journalist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "journalist"},
        related_name="newsletters",
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.title
