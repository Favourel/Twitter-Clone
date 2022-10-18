from django.test import TestCase
from .models import *
from users.models import User
from django.shortcuts import reverse


class PostTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        self.user_2 = User.objects.create(
            username='fred', email='fred@gmail.com', password='top_secret')
        self.post_1 = Post.objects.create(
            content='Loren ipsum text 1', author=self.user_1)
        self.post_1.like.set([self.user_1, self.user_2])
        self.post_2 = Post.objects.create(
            content='Loren ipsum text 2', os='mac', author=self.user_1)
        self.blog_repost_1 = BlogRepost.objects.create(
            post=self.post_1, user=self.user_1, text="A test"
        )

    def test_post_str(self):
        self.assertEqual(str(self.post_1), "jacob post")
        self.assertEqual(self.post_1.like.count(), 2)

    def test_post_comment_str(self):
        blog_comment = BlogComment.objects.create(
            post=self.post_1, user=self.user_1, comment="A test"
        )
        self.assertEqual(str(blog_comment), "jacob comment")

    def test_repost_str(self):
        self.assertEqual(str(self.blog_repost_1), "jacob repost")

    def test_repost_comment_str(self):
        repost_comment = RepostComment.objects.create(
            post=self.blog_repost_1, user=self.user_1, comment="A test"
        )
        self.assertEqual(str(repost_comment), "jacob comment")

    def test_notification_str(self):
        notification = Notification.objects.create(
            user=self.user_1, sender=self.user_2, blog=self.post_1, notification_type=1
        )
        self.assertEqual(str(notification), "fred notification")

    def test_post_notification_str(self):
        notification = PostNotification.objects.create(
            user=self.user_1, sender=self.user_2, blog=self.post_1, notification_type=2, is_seen=False
        )
        self.assertEqual(str(notification), "fred notification")

    def test_recent_search_str(self):
        notification = RecentSearch.objects.create(
            user=self.user_1, search=self.user_2, search_word="Fred"
        )
        self.assertEqual(str(notification), "jacob search")

    def test_get_absolute_url(self):
        self.post_pk = Post.objects.get(pk=1)
        self.assertEqual("/post/1/", self.post_pk.get_absolute_url())

    def test_get_repost_url(self):
        self.post_pk = Post.objects.get(pk=1)
        self.assertEqual("/repost/1/add/", self.post_pk.get_repost_url())

    def test_get_api_like_url(self):
        self.post_pk = Post.objects.get(pk=1)
        self.assertEqual("/api/1/add/", self.post_pk.get_api_like_url())

    def test_get_repost_absolute_url(self):
        self.repost_pk = BlogRepost.objects.get(pk=1)
        self.assertEqual("/repost/1/", self.repost_pk.get_repost_absolute_url())

    def test_get_repost_api_like_url(self):
        self.repost_pk = BlogRepost.objects.get(pk=1)
        self.assertEqual("/repost/1/add_like/", self.repost_pk.get_repost_api_like_url())

    def test_get_repost_url_(self):
        self.repost_pk = BlogRepost.objects.get(pk=1)
        self.assertEqual("/repost-/1/add/", self.repost_pk.get_repost_url_())
