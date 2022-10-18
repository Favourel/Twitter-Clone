from django.test import TestCase, Client
from users.models import User
from django.shortcuts import reverse
from .models import *
import json
from django.forms.models import model_to_dict


# Create your tests here.


class ViewTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        self.user_id = User.objects.get(username="jacob")
        self.user_2 = User.objects.create(
            username='fred', email='fred@gmail.com', password='top_secret')
        self.user_1.following.set([self.user_2])
        self.post_1 = Post.objects.create(
            content='Loren ipsum text 1', author=self.user_1)
        self.post_id = Post.objects.get(pk=1)
        self.blog_repost_1 = BlogRepost.objects.create(
            post=self.post_1, user=self.user_1, text="A test"
        )
        self.repost_id = BlogRepost.objects.get(pk=1)
        self.client = Client()
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)

    def test_blog_list(self):
        response = self.client.get(reverse("blog_home"))
        print(response.status_code)
        self.assertEqual(response.status_code, 302)
        # send login data
        response_login = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response_login.context['user'].is_active)
        response_blog_home = self.client.get(reverse("blog_home"))
        self.assertEqual(response_blog_home.status_code, 200)
        self.assertTemplateUsed(response_blog_home, 'blog/blog_list.html')

    def test_user_following(self):
        self.assertListEqual([str(self.user_2)], ["fred"])

    def test_blog_content(self):
        # send login data
        response = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)

        self.post = Post.objects.get(pk=1)
        response = self.client.get(
            reverse('blog_detail_view', kwargs={'pk': self.post_1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_detail.html')

    def test_repost_content(self):
        # send login data
        response = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)

        self.repost = BlogRepost.objects.get(pk=1)
        response = self.client.get(
            reverse('repost_detail_view', kwargs={'pk': self.blog_repost_1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/repost_detail.html')

    def test_error_404(self):
        # send login data
        response = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)

        response = self.client.get("http://127.0.0.1:8000/wrong-page/")
        # self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'blog/error404.html')

    # def test_create_post(self):
    #     response_login = self.client.post('/login/', self.credentials, follow=True)
    #     # should be logged in now
    #     self.assertTrue(response_login.context['user'].is_authenticated)
    #
    #     response = self.client.post(reverse("create_post"), {
    #         "content": 'Loren ipsum text 12', "os": "Windows",
    #         "author": response_login.context['user'].username
    #     }, follow=True)
    #     data = json.loads(response.content)
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(data.get("content"), "Loren ipsum text 12")

    def test_comment(self):
        # send login data
        response_login = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response_login.context['user'].is_active)
        self.post_id = Post.objects.get(pk=1)
        response_url = reverse('blog_comment', kwargs={'pk': 1})

        response = self.client.post(response_url, {
            "post": self.post_id, "user": response_login.context['user'].username,
            "comment": "comment"
        }, follow=True)

        data = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(data.get("comment"), "comment")

    def test_repost_comment(self):
        # send login data
        response_login = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response_login.context['user'].is_active)

        self.repost_id = BlogRepost.objects.get(pk=1)
        response_url = reverse('repost_comment', kwargs={'pk': 1})

        response = self.client.post(response_url, {
            "post": self.repost_id, "user": response_login.context['user'].username,
            "comment": "comment"
        }, follow=True)

        data = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(data.get("comment"), "comment")

    def test_search(self):
        response_login = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response_login.context['user'].is_authenticated)

        url = '{url}?{filter}={value}'.format(
            url=reverse('search'),
            filter='q', value='Loren')
        response = self.client.get(url)

        response_search = self.client.get(reverse("search"))
        self.assertEqual(response_search.status_code, 200)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response_search, 'blog/search.html')
        self.assertTemplateUsed(response, 'blog/search.html')

    def test_push_feed(self):
        response_login = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response_login.context['user'].is_authenticated)

        response = self.client.post(reverse("push_feed"), {
            "content": 'Loren ipsum text 14', "author": response_login.context['user'].username
        }, follow=True)
        data = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(data.get("content"), "Loren ipsum text 14")

    def test_ajax_posting(self):
        response_login = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response_login.context['user'].is_authenticated)
        response = self.client.post(reverse("join"), {
            "content": 'Loren ipsum text 14', "author": self.user_id
        }, follow=True)
        data = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertNotEqual(data.get("content"), "Loren ipsum text 14")

    def test_delete(self):
        response_login = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response_login.context['user'].is_authenticated)

        response_url = reverse('blog_detail_view', kwargs={'pk': 1})
        response_url_2 = reverse('blog_delete_view', kwargs={'pk': 1})
        response = self.client.delete(response_url, json.dumps(
            {"pk": 1}
        ))
        response_2 = self.client.delete(response_url_2, json.dumps(
            {"pk": 1}
        ))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response_2.status_code, 200)

    def test_repost_add_view(self):
        response_login = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response_login.context['user'].is_authenticated)

        response_url = reverse('repost_add_view', kwargs={'pk': 1})
        response_url_2 = reverse('repost_add_view-', kwargs={'pk': 1})

        response = self.client.post(response_url, {
            "post": self.post_id, "user": response_login.context['user'].username,
            "text": "comment"
        }, follow=True)

        response_2 = self.client.post(response_url_2, {
            "repost": self.repost_id, "user": response_login.context['user'].username,
            "text": "comment"
        }, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response_2.status_code, 200)
        self.assertTemplateNotUsed(response, "blog/repost_add_view.html")
        self.assertTemplateNotUsed(response_2, 'blog/repost_add_view_.html')
