from django.contrib import admin
from .models import *

# Register your models here.


class CommentInline(admin.TabularInline):
    model = BlogComment


class RepostCommentInline(admin.TabularInline):
    model = BlogRepost


class PostAdmin(admin.ModelAdmin):
    list_display = ['content', 'author', 'date_posted']
    search_fields = ["content"]
    filter_horizontal = ['like']
    list_filter = ['author', 'date_posted']
    list_per_page = 10
    inlines = [CommentInline]


class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['user', "post", 'date_posted']


class NotificationAdmin(admin.ModelAdmin):
    list_display = ["sender", "notification_type", "user", "is_seen"]
    search_fields = ('sender', 'user')


class PostNotificationAdmin(admin.ModelAdmin):
    list_display = ["sender", "notification_type", "user", "is_seen"]
    search_fields = ('sender', 'user')


class BlogRepostAdmin(admin.ModelAdmin):
    list_display = ['user', "post", "repost", 'date_posted']
    inlines = [RepostCommentInline]


class BlogImagesAdmin(admin.ModelAdmin):
    list_display = ["post", "image", "date_posted"]


admin.site.register(Post, PostAdmin)
admin.site.register(BlogComment, BlogCommentAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(PostNotification, PostNotificationAdmin)
admin.site.register(BlogRepost, BlogRepostAdmin)
admin.site.register(RepostComment)
admin.site.register(BlogImages, BlogImagesAdmin)
admin.site.register(RecentSearch)
