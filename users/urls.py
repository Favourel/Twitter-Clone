from django.urls import path
from . import views as user_views
from .middlewares import LogoutCheckMiddleware


urlpatterns = [
    path('register/', LogoutCheckMiddleware(user_views.register), name='register'),
    path('update-profile/', user_views.update_profile, name='update_profile'),

    path("notification/", user_views.notification_view, name="notification"),

    path("<str:username>/follow/", user_views.follower_view, name="follow"),
    path('<str:username>/post/', user_views.profile_view, name='a_follower_post_view'),

    path('api/<str:username>/follow/', user_views.UserFollowerApi.as_view(), name='follower-api'),
    path('api/<str:username>/post_notify/', user_views.PostNotificationApi.as_view(), name='post_notify'),
    path('api/<str:username>/mute_profile/', user_views.MuteProfileApi.as_view(), name='mute_profile'),
    path('api/<str:username>/block_user/', user_views.BlockProfileApi.as_view(), name='block_user'),

    path('ajax/validate_username/', user_views.validate_username, name='validate_username'),

    # path(r'^ajax/validate_username/$', user_views.validate_username, name='validate_username'),

]