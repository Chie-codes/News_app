from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import Group, Permission
from django.apps import apps
from .models import Article


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """
    Ensure default groups and permissions always exist after migrations.
    Runs only for this app (news_app).
    """
    if sender.name != "news_app":
        return

    # Use singular group names
    reader_group, _ = Group.objects.get_or_create(name="Reader")
    journalist_group, _ = Group.objects.get_or_create(name="Journalist")
    editor_group, _ = Group.objects.get_or_create(name="Editor")
    publisher_group, _ = Group.objects.get_or_create(name="Publisher")

    # Get models dynamically
    Article = apps.get_model("news_app", "Article")
    Newsletter = apps.get_model("news_app", "Newsletter")

    # Get permissions
    article_perms = Permission.objects.filter(
        content_type__app_label="news_app",
        content_type__model="article"
    )
    newsletter_perms = Permission.objects.filter(
        content_type__app_label="news_app",
        content_type__model="newsletter"
    )

    # --- Assign Editor permissions ---
    editor_group.permissions.clear()
    editor_group.permissions.add(*[
        p for p in article_perms if p.codename in ["view_article", "change_article", "delete_article"]
    ], *[
        p for p in newsletter_perms if p.codename in ["view_newsletter", "change_newsletter", "delete_newsletter"]
    ])

    # --- Assign Journalist permissions ---
    journalist_group.permissions.clear()
    journalist_group.permissions.add(*[
        p for p in article_perms if p.codename in ["add_article", "view_article", "change_article", "delete_article"]
    ], *[
        p for p in newsletter_perms if p.codename in ["add_newsletter", "view_newsletter", "change_newsletter", "delete_newsletter"]
    ])

    # Reader and Publisher groups intentionally empty for now


@receiver(post_save, sender=Article)
def notify_article_approved(sender, instance, created, **kwargs):
    """
    Notify the journalist when their article is approved.
    Only fires when an existing article changes to approved=True.
    """
    if not created and instance.approved:
        if instance.journalist and instance.journalist.email:
            send_mail(
                subject=f"Your article '{instance.title}' was approved!",
                message="Congratulations, your article is now live.",
                from_email="admin@newsapp.com",
                recipient_list=[instance.journalist.email],
                fail_silently=True,  # safer in dev (avoid breaking on email failure)
            )
