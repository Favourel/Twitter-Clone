from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import reverse
from django.conf import settings

# Create your models here.


class User(AbstractUser):
    display_name = models.CharField(max_length=20, null=True, blank=True)
    about = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(default='profile.png', upload_to='profile_picture')

    follower = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='follower_list')
    following = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='following_list')

    background_image = models.ImageField(default="WIN_20220328_15_20_55_Pro.jpg", upload_to="profile_background_image")
    account_visit = models.IntegerField(default=0)
    account_engaged = models.IntegerField(default=0)
    has_viewed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    post_notification = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='post_notify')
    mute_list = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='mute')
    block_list = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='block')

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def get_follower_api_url(self):
        return reverse('follower-api', kwargs={'username': self.username})

    def post_notify_api_url(self):
        return reverse('post_notify', kwargs={'username': self.username})


class UserStat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, on_delete=models.CASCADE)
    account_visit = models.IntegerField(default=0)
    account_engaged = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} stat"


class Story(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    story_image = models.ImageField(upload_to='story_picture', blank=True, null=True)

    def __str__(self):
        return f"{self.user} story"
