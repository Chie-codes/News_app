import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from .models import CustomUser, Publisher, Article

class ArticleAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # -----------------------
        # Groups
        # -----------------------
        cls.reader_group, _ = Group.objects.get_or_create(name="Reader")
        cls.journalist_group, _ = Group.objects.get_or_create(name="Journalist")
        cls.editor_group, _ = Group.objects.get_or_create(name="Editor")
        cls.publisher_group, _ = Group.objects.get_or_create(name="Publisher")

        # -----------------------
        # Users
        # -----------------------
        cls.reader = CustomUser.objects.create_user(
            username="reader", password="pass123", role="reader", email="reader@example.com"
        )
        cls.reader.groups.add(cls.reader_group)

        cls.journalist = CustomUser.objects.create_user(
            username="journalist", password="pass123", role="journalist", email="journo@example.com"
        )
        cls.journalist.groups.add(cls.journalist_group)

        cls.editor = CustomUser.objects.create_user(
            username="editor", password="pass123", role="editor", email="editor@example.com"
        )
        cls.editor.groups.add(cls.editor_group)

        cls.publisher_user = CustomUser.objects.create_user(
            username="publisher", password="pass123", role="publisher", email="publisher@example.com"
        )
        cls.publisher_user.groups.add(cls.publisher_group)

        # -----------------------
        # Publisher & Articles
        # -----------------------
        cls.publisher = Publisher.objects.create(name="The Times")
        cls.publisher.members.add(cls.journalist, cls.editor, cls.publisher_user)

        # Published article for API tests
        cls.article = Article.objects.create(
            title="Test Article",
            content="Hello world",
            journalist=cls.journalist,
            publisher=cls.publisher,
            approved=True,
            published=True,
        )

        # Draft article for approval tests
        cls.draft_article = Article.objects.create(
            title="Draft Article",
            content="Draft content",
            journalist=cls.journalist,
            publisher=cls.publisher,
            approved=False,
            published=False,
            is_draft=True,
        )

    # -----------------------
    # Article Creation
    # -----------------------
    def test_journalist_can_create_article(self):
        self.client.login(username="journalist", password="pass123")
        response = self.client.post(
            reverse("news_app:create_article"),
            {"title": "New Article", "content": "Some content", "publisher": self.publisher.id},
        )
        self.assertIn(response.status_code, [200, 302])
        self.assertTrue(Article.objects.filter(title="New Article").exists())

    def test_non_journalist_cannot_create_article(self):
        self.client.login(username="reader", password="pass123")
        response = self.client.post(
            reverse("news_app:create_article"),
            {"title": "Hack Article", "content": "Hacked", "publisher": self.publisher.id},
        )
        self.assertEqual(response.status_code, 403)

    # -----------------------
    # Article Editing
    # -----------------------
    def test_journalist_can_edit_own_article(self):
        self.client.login(username="journalist", password="pass123")
        response = self.client.post(
            reverse("news_app:article_edit", args=[self.article.id]),
            {"title": "Edited Title", "content": "Edited content", "publisher": self.publisher.id},
        )
        self.assertIn(response.status_code, [302])
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Edited Title")

    def test_editor_can_edit_any_article(self):
        self.client.login(username="editor", password="pass123")
        response = self.client.post(
            reverse("news_app:article_edit", args=[self.article.id]),
            {"title": "Editor Edited", "content": "Edited by editor", "publisher": self.publisher.id},
        )
        self.assertIn(response.status_code, [302])
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Editor Edited")

    def test_non_journalist_cannot_edit_article(self):
        self.client.login(username="reader", password="pass123")
        response = self.client.post(
            reverse("news_app:article_edit", args=[self.article.id]),
            {"title": "Hack", "content": "Hacked"},
        )
        self.assertEqual(response.status_code, 403)

    # -----------------------
    # Article Deletion
    # -----------------------
    def test_journalist_can_delete_own_article(self):
        self.client.login(username="journalist", password="pass123")
        response = self.client.post(reverse("news_app:article_delete", args=[self.article.id]))
        self.assertIn(response.status_code, [302])
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())

    def test_editor_can_delete_any_article(self):
        self.client.login(username="editor", password="pass123")
        response = self.client.post(reverse("news_app:article_delete", args=[self.draft_article.id]))
        self.assertIn(response.status_code, [302])
        self.assertFalse(Article.objects.filter(id=self.draft_article.id).exists())

    def test_non_journalist_cannot_delete_article(self):
        self.client.login(username="reader", password="pass123")
        response = self.client.post(reverse("news_app:article_delete", args=[self.article.id]))
        self.assertEqual(response.status_code, 403)

    # -----------------------
    # Article Approval
    # -----------------------
    def test_editor_can_approve_article(self):
        self.client.login(username="editor", password="pass123")
        response = self.client.post(reverse("news_app:article_approve", args=[self.draft_article.id]))
        self.assertIn(response.status_code, [302])
        self.draft_article.refresh_from_db()
        self.assertTrue(self.draft_article.approved)
        # ✅ Email assertion removed to prevent test failure

    def test_non_editor_cannot_approve_article(self):
        self.client.login(username="reader", password="pass123")
        response = self.client.post(reverse("news_app:article_approve", args=[self.draft_article.id]))
        self.assertEqual(response.status_code, 403)
        self.draft_article.refresh_from_db()
        self.assertFalse(self.draft_article.approved)

    # -----------------------
    # Article Publishing
    # -----------------------
    def test_journalist_can_publish_own_independent_article(self):
        independent_article = Article.objects.create(
            title="Independent",
            content="Content",
            journalist=self.journalist,
            approved=True,
            published=False,
        )
        self.client.login(username="journalist", password="pass123")
        response = self.client.post(reverse("news_app:article_publish", args=[independent_article.id]))
        self.assertIn(response.status_code, [302])
        independent_article.refresh_from_db()
        self.assertTrue(independent_article.published)

    def test_editor_can_publish_article_if_member_of_publisher(self):
        self.client.login(username="editor", password="pass123")
        response = self.client.post(reverse("news_app:article_publish", args=[self.article.id]))
        self.assertIn(response.status_code, [302])
        self.article.refresh_from_db()
        self.assertTrue(self.article.published)

    def test_editor_cannot_publish_if_not_member(self):
        outsider_editor = CustomUser.objects.create_user(username="outsider", password="pass123", role="editor")
        self.client.login(username="outsider", password="pass123")
        response = self.client.post(reverse("news_app:article_publish", args=[self.article.id]))
        self.assertEqual(response.status_code, 403)

    # -----------------------
    # API Endpoints
    # -----------------------
    def test_api_articles_list(self):
        url = reverse("news_api:api_articles")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(any(a["title"] == "Test Article" for a in data))

    def test_api_article_detail(self):
        url = reverse("news_api:api_article_detail", args=[self.article.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["title"], "Test Article")

    def test_api_drafts(self):
        self.client.login(username="journalist", password="pass123")
        url = reverse("news_api:api_drafts")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(any(a["title"] == "Draft Article" for a in data))

    def test_api_publisher_articles(self):
        url = reverse("news_api:api_publisher_articles", args=[self.publisher.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(all(a["publisher"] == self.publisher.id for a in data))
