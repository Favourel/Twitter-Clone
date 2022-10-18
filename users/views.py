from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import auth
import os
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import *
from blog.models import *
from users.models import User
from itertools import chain
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, serializers
from users import models


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('register')
            elif len(password1) < 8 and len(password2) < 8:
                messages.error(request, 'Password can not be less than 8')
                return redirect('register')
            elif password1 and password2 == username:
                messages.error(request, 'Password can not similar to username')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)

                user.save()
                auth_login = auth.authenticate(username=username, password=password1)
                auth.login(request, auth_login)
                messages.success(request, f"Account created for {username}")
                return redirect('blog_home')
        else:
            messages.error(request, "Password doesn't match")
            return redirect('register')
    context = {

    }
    return render(request, 'users/register.html', context)


# def register(request):
#     form = RegisterForm()
#     if request.method == "POST":
#         if form.is_valid():
#             form = form.save()
#
#             auth_user = auth.authenticate(username=form.username, password=form.password)
#             auth.login(request, auth_user)
#             messages.success(request, f"Account created for {form.username}")
#             return redirect('blog_home')
#         # else:
#         #     return render(request, "users/register.html", {'form':form})
#         return render(request, "users/register.html", {'form': form})
#     else:
#         return render(request, "users/register.html", {'form':form})


def validate_username(request):
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists(),
        'is_taken_email': User.objects.filter(email__iexact=email).exists(),
    }
    return JsonResponse(data)


@login_required
def update_profile(request):
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form = form.save(commit=False)
            image_path = form.image.path

            # if os.path.exists(image_path):
            #     os.remove(image_path)
            #     print(image_path)

            form.save()
            print(image_path)

            messages.success(request, 'Your account has been updated!')
            return redirect(f"../{request.user}/post/")
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            # i changed the error popup
            messages.warning(request, 'error')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form = UserUpdateForm(instance=request.user)
    context = {
        "form": form,
        "notification_count": notification_count,
        "post_notification_count": PostNotification.objects.filter(user=request.user, is_seen=False).count()

    }
    return render(request, 'users/update_profile.html', context)


@login_required
def notification_view(request):
    followed_by = request.user.following.filter(id__in=request.user.follower.all())[:1]
    followed_by_ = request.user.following.filter(id__in=request.user.follower.all())
    followed_by_count = followed_by_.count()
    notification = Notification.objects.filter(user=request.user, is_seen=False)
    post_notification = Notification.objects.filter(user=request.user, is_seen=False)

    posts_mentions = BlogRepost.objects.filter(text__icontains=f"@{request.user}").order_by("-date_posted")

    followers_mentions = Post.objects.filter(content__icontains=f"@{request.user}").order_by('-date_posted')
    combined_mentions = sorted(
        chain(posts_mentions, followers_mentions),
        key=lambda posts: posts.date_posted, reverse=True
    )
    if not notification:
        notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
        post_notification_count = PostNotification.objects.filter(user=request.user, is_seen=False).count()
        notification_list = Notification.objects.filter(user=request.user).order_by("-date")
        post_notification_list = PostNotification.objects.filter(user=request.user).order_by("-date")

        queryset = []
        for single_notification in notification_list:
            queryset.append(single_notification.blog)
        context = {
            "notification_list": notification_list,
            "notification_count": notification_count,
            "followed_by": followed_by,
            "followed_by_count": followed_by_count,
            "post_notification_list": post_notification_list,
            "post_notification_count": post_notification_count,
            "combined_mentions": combined_mentions,
            # "queryset": queryset
        }
        return render(request, "users/notification.html", context)
    elif not post_notification:
        notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
        post_notification_count = PostNotification.objects.filter(user=request.user, is_seen=False).count()
        notification_list = Notification.objects.filter(user=request.user).order_by("-date")
        post_notification_list = PostNotification.objects.filter(user=request.user).order_by("-date")

        queryset = []
        for single_notification in notification_list:
            queryset.append(single_notification.blog)
        context = {
            "notification_list": notification_list,
            "notification_count": notification_count,
            "followed_by": followed_by,
            "followed_by_count": followed_by_count,
            "post_notification_list": post_notification_list,
            "post_notification_count": post_notification_count,
            "combined_mentions": combined_mentions,
            # "queryset": queryset
        }
        return render(request, "users/notification.html", context)
    else:
        notification_list = Notification.objects.filter(user=request.user).order_by("-date").exclude(notification_type=7)
        notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
        post_notification_count = PostNotification.objects.filter(user=request.user, is_seen=False).count()
        post_notification_list = PostNotification.objects.filter(user=request.user).order_by("-date")

        PostNotification.objects.filter(user=request.user).update(is_seen=True)

        queryset = []
        for user_notification in Notification.objects.filter(user=request.user):
            queryset.append(user_notification.is_seen == True)
            user_notification.is_seen = True
            user_notification.save()

        queryset = []
        for user_post_notification in PostNotification.objects.filter(user=request.user):
            queryset.append(user_post_notification.is_seen == True)
            user_post_notification.is_seen = True
            user_post_notification.save()

        context = {
            "notification_list": notification_list,
            "notification_count": notification_count,
            "followed_by": followed_by,
            "followed_by_count": followed_by_count,
            "post_notification_list": post_notification_list,
            "post_notification_count": post_notification_count,
            "combined_mentions": combined_mentions,
        }
        return render(request, "users/notification.html", context)


@login_required
def follower_view(request, username):
    obj = get_object_or_404(User, username=username)
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    post_notification_count = PostNotification.objects.filter(user=request.user, is_seen=False).count()
    follower = obj.follower.all()
    following = obj.following.all()

    context = {
        "follower": follower,
        "following": following,
        "notification_count": notification_count,
        "post_notification_count": post_notification_count,
    }
    return render(request, "users/follows.html", context)


@login_required
def profile_view(request, username):
    try:
        if User.objects.get(username=username).is_active:
            user_profile = get_object_or_404(User, username=username)
            if request.user not in user_profile.block_list.all():
                user_profile = get_object_or_404(User, username=username)
                notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
                post_notification_count = PostNotification.objects.filter(user=request.user, is_seen=False).count()
                posts = Post.objects.filter(author=user_profile).order_by("-date_posted")
                posts_commented = BlogComment.objects.filter(user=user_profile).order_by("-date_posted")
                posts_reposted = BlogRepost.objects.filter(user=user_profile).order_by("-date_posted")
                posts_liked = Post.objects.filter(like=user_profile).order_by("-date_posted")
                # editing the next line
                suggested_followers = user_profile.following.all().exclude(id__in=request.user.following.all()).exclude(
                    id=request.user.id).order_by("?")[:5]

                followed_by = request.user.following.filter(id__in=user_profile.follower.all())[:1]
                followed_by_ = request.user.following.filter(id__in=user_profile.follower.all())
                followed_by_count = followed_by_.count()

                # UserStat.objects.filter(user=user_profile).update(account_visit=F('account_visit')+1)
                if not request.user == user_profile:
                    user_profile.account_visit = (user_profile.account_visit + 1)
                    user_profile.save()

                if request.method == 'POST':
                    form = UserUpdateForm(request.POST, request.FILES, instance=request.user)

                    if form.is_valid():
                        form = form.save(commit=False)
                        image_path = form.image.path

                        # if os.path.exists(image_path):
                        #     os.remove(image_path)
                        #     print(image_path)

                        form.save()
                        print(image_path)

                        messages.success(request, 'Your account has been updated!')
                        return redirect(f"../{request.user}/post/")
                        # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    else:
                        # i changed the error popup
                        messages.warning(request, 'error')
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    form = UserUpdateForm(instance=request.user)

                account_engaged = user_profile.userstat_set.all()

                user_profile_posts = user_profile.post_set.all()
                media_count = BlogImages.objects.filter(post__in=user_profile_posts).count()
                context = {
                    "form": form,
                    "posts": posts,
                    "posts_liked": posts_liked,
                    "posts_commented": posts_commented,
                    "posts_reposted": posts_reposted,
                    "user_profile": user_profile,
                    "suggested_followers": suggested_followers,
                    "notification_count": notification_count,
                    "followed_by": followed_by,
                    "followed_by_count": followed_by_count,
                    "account_engaged_count": account_engaged,
                    "media_count": media_count,
                    "post_notification_count": post_notification_count,
                }
                return render(request, "blog/a_follower_post_view.html", context)
            else:
                messages.warning(request, "This user restricted you from viewing their profile")
                return redirect("/")
        else:
            messages.warning(request, "This account can't be reached because it has been restricted by Elodimuor")
            return redirect("/")
    except ObjectDoesNotExist:
        messages.error(request, "NO ACTIVE USER FOUND")
        return redirect("error404")


class UserFollowerApi(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username, format=None):
        obj = get_object_or_404(models.User, username=username)
        user = request.user
        updated = False
        following = False
        if not user in obj.block_list.all():
            if user in obj.follower.all():
                following = False
                obj.follower.remove(user)
                user.following.remove(obj)
                user.post_notification.remove(obj)
                # user.block_list.add(obj)

                notify = Notification.objects.get(sender=user, user=obj, notification_type=3)
                notify.delete()

            else:
                following = True
                obj.follower.add(user)
                user.following.add(obj)

                notify = Notification(sender=user, user=obj, notification_type=3)
                notify.save()

                data = {
                    'updated': updated,
                    'following': following,
                    'follower_count': obj.follower.count(),
                }
                return Response(data)
            updated = True
        else:
            following = False
            not_follow = True
            data = {
                # 'updated': updated,
                # 'following': following,
                'not_follow': not_follow,
                'messages': f"Can not follow {obj}",
            }
            return Response(data)
        data = {
            'updated': updated,
            'following': following,
            'follower_count': obj.follower.count(),
        }
        return Response(data)


class PostNotificationApi(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username, format=None):
        user = request.user
        obj = get_object_or_404(User, username=username)
        updated = False
        post_notify = False
        if user:
            if user in obj.post_notification.all():
                post_notify = False
                obj.post_notification.remove(user)
            else:
                post_notify = True
                obj.post_notification.add(user)

                data = {
                    "updated": updated,
                    "post_notify": post_notify,
                    "messages": "You will get notified when they post"
                }
                return Response(data)
            updated = True
        data = {
            "updated": updated,
            "post_notify": post_notify,
            "messages": "You will get notified when they post"
        }
        return Response(data)


class MuteProfileApi(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username, format=None):
        user = request.user
        obj = get_object_or_404(User, username=username)
        updated = False
        mute_profile = False

        if obj in user.mute_list.all():
            mute_profile = False
            user.mute_list.remove(obj)
            updated = True
            data = {
                "updated": updated,
                "mute_profile": mute_profile,
                "messages": f"{obj} has been unmuted."
            }

            return Response(data)

        else:
            mute_profile = True
            user.mute_list.add(obj)
            updated = True

            data = {
                "updated": updated,
                "mute_profile": mute_profile,
                "messages": f"{obj} has been muted."
            }

            return Response(data)


class BlockProfileApi(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username, format=None):
        user = request.user
        obj = get_object_or_404(User, username=username)
        updated = False
        block_profile = False

        if obj in user.block_list.all():
            block_profile = False
            user.block_list.remove(obj)
            updated = True
            data = {
                "updated": updated,
                "block_profile": block_profile,
                "messages": f"{obj} has been unblocked."
            }

            return Response(data)

        else:
            block_profile = True
            user.block_list.add(obj)
            user.post_notification.remove(obj)
            user.follower.remove(obj)
            obj.following.remove(user)
            notify = Notification.objects.get(sender=user, user=obj, notification_type=3)
            notify.delete()
            updated = True

            data = {
                "updated": updated,
                "block_profile": block_profile,
                "messages": f"{obj} has been blocked."
            }

            return Response(data)
