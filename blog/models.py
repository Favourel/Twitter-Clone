from django.db import models
from django.utils import timezone
from djrichtextfield.models import RichTextField
# from ckeditor.fields import RichTextField

from django.conf import settings
from django.shortcuts import reverse


# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    # content = models.TextField()
    content = RichTextField()
    # content = HTMLField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='like')

    def __str__(self):
        return f"{self.author} post"

    def get_absolute_url(self):
        return reverse("blog_detail_view", kwargs={"pk": self.pk})

    def get_repost_url(self):
        return reverse("repost_add_view", kwargs={"pk": self.pk})

    def get_api_like_url(self):
        return reverse('like-api', kwargs={'pk': self.pk})


class BlogComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.post.author} comment'


class BlogRepost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL,  null=True, blank=True)
    text = models.CharField(max_length=500, null=True, blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='repost_like')
    repost = models.ForeignKey("BlogRepost", blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.user} repost'

    def get_repost_absolute_url(self):
        return reverse("repost_detail_view", kwargs={"pk": self.pk})

    def get_repost_api_like_url(self):
        return reverse('repost_like-api', kwargs={'pk': self.pk})

    def get_repost_url_(self):
        return reverse("repost_add_view-", kwargs={"pk": self.pk})


class RepostComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogRepost, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.post.user} comment'


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        (1, "likes"), (2, "comment"), (3, "follow"),
        (4, "Repost"), (5, "Liked_a_Repost"), (6, "Commented_on_a_Repost"), (7, "Post Notification"),
        (8, "Repost of repost")
                          )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                             related_name="noti_to_user")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True,
                               on_delete=models.CASCADE, related_name="noti_from_user")

    blog = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    repost_blog = models.ForeignKey(BlogRepost, null=True, blank=True, on_delete=models.CASCADE)
    # repost_of_repost = models.ForeignKey(BlogRepost.repost, null=True, blank=True, on_delete=models.CASCADE)
    notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
    text_preview = models.CharField(max_length=200, blank=True, null=True)
    notify_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='notify_users')

    date = models.DateTimeField(default=timezone.now)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} notification'


class PostNotification(models.Model):
    NOTIFICATION_TYPES = (
         (1, "Post Notification"), (2, "Like Notification")
                          )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                             related_name="notification_to_user")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True,
                               on_delete=models.CASCADE, related_name="notification_from_user")

    blog = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    repost_blog = models.ForeignKey(BlogRepost, null=True, blank=True, on_delete=models.CASCADE)
    # repost_of_repost = models.ForeignKey(BlogRepost.repost, null=True, blank=True, on_delete=models.CASCADE)
    notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)

    date = models.DateTimeField(default=timezone.now)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} notification'


class BlogImages(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="blog_images", blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)


class RecentSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    search = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name="user_search")
    search_word = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f'{self.user} search'

