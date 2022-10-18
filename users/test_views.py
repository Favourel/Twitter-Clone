from django.test import TestCase, Client
from .models import *
from django.shortcuts import reverse
from .models import *
import json


class ViewTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        self.user_id = User.objects.get(username="jacob")
        self.user_2 = User.objects.create(
            username='fred', email='fred@gmail.com', password='top_secret')
        self.user_1.following.set([self.user_2])

        self.client = Client()
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)
        response_login = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response_login.context['user'].is_authenticated)
        self.assertTrue(response_login.context['user'].is_active)

    def test_register(self):
        response = self.client.post(reverse("register"), {
            "username": 'paul', "email": "paul@gmail.com", "password1": "topsecret",
            "password2": "topsecret"
        }, follow=True)
        data = {
            "username": 'paul',
            "password": "topsecret",
        }

        response_login = self.client.post('/login/', data=data, follow=True)
        # should be logged in now
        self.assertTrue(response_login.context['user'].is_authenticated)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, "/")

    def test_notification(self):
        response_notification = self.client.get(reverse("notification"))
        self.assertEqual(response_notification.status_code, 200)
        self.assertTemplateUsed(response_notification, 'users/notification.html')

    def test_follower(self):
        response = self.client.get(
            reverse("follow", kwargs={'username': self.user_1.username}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/follows.html')

    def test_profile(self):
        response = self.client.get(
            reverse("a_follower_post_view", kwargs={'username': self.user_1.username}))
        print(self.user_id.username)
        self.assertEquals(response.status_code, 200)
        data = {
            "username": "favour"
        }
        response_update = self.client.post(reverse("a_follower_post_view",
                                                   kwargs={'username': self.user_1.username}), data=data, follow=True)
        self.assertEquals(response_update.status_code, 200)

    def test_update_profile(self):
        response= self.client.get(reverse("update_profile"))
        self.assertEquals(response.status_code, 200)

        data = {
            "username": "abram"
        }
        response_update = self.client.post(reverse("update_profile"), data=data, follow=True)
        self.assertEquals(response_update.status_code, 200)
        # self.assertTemplateUsed(response_update, 'users/update_profile.html')
