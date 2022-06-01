from django.urls import path
from . import views as user_views
from .middlewares import LogoutCheckMiddleware


urlpatterns = [
    path('register/', LogoutCheckMiddleware(user_views.register), name='register'),
    path('update-profile/', user_views.update_profile, name='update_profile'),

    path("notification/", user_views.notification_view, name="notification"),

    path("<str:username>/follow/", user_views.follower_view, name="follow"),

    path('ajax/validate_username/', user_views.validate_username, name='validate_username'),

    # path(r'^ajax/validate_username/$', user_views.validate_username, name='validate_username'),

]