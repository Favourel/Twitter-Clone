from django.urls import path
from . import views as blog_view

urlpatterns = [
    path('', blog_view.blog_list_view, name='blog_home'),
    path('post/<int:pk>/', blog_view.blog_detail_view, name='blog_detail_view'),
    path('repost/<int:pk>/', blog_view.repost_detail_view, name='repost_detail_view'),
    path('comment/<int:pk>/', blog_view.blog_comment, name='blog_comment'),
    path('repost/comment/<int:pk>/', blog_view.repost_comment, name='repost_comment'),
    path('repost/<int:pk>/add/', blog_view.repost_add_view, name='repost_add_view'),
    path('repost-/<int:pk>/add/', blog_view.repost_add_view_, name='repost_add_view-'),
    path('search/', blog_view.search, name='search'),
    path('api/<int:pk>/add/', blog_view.PostLikeApi.as_view(), name='like-api'),
    path('repost/<int:pk>/add_like/', blog_view.RepostLikeApi.as_view(), name='repost_like-api'),
    path('create_post/', blog_view.create_post, name='create_post'),
    # path('blog/<int:pk>/update/', blog_view.PostUpdateView.as_view(), name='blog_detail_view'),
    path('post/<int:pk>/delete/', blog_view.PostDeleteView.as_view(), name='blog_delete_view'),

    path('form/', blog_view.ajax_posting, name="join"),

    path('push_feed/', blog_view.push_feed, name="push_feed"),

]