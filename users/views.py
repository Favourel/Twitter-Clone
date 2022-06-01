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
import re
from django.db.models import F


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        # value = re.sub(r'^[\w.@+-]+\Z(\w+)', r'^[\w.@+-]+\Z\1', username)
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
            # elif value in username:
            #     messages.error(request, 'Enter a valid username. This value may contain only English letters,')
            #     return redirect('register')
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


# def registerr(request):
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
    }
    return render(request, 'users/update_profile.html', context)


@login_required
def notification_view(request):
    followed_by = request.user.following.filter(id__in=request.user.follower.all())[:1]
    followed_by_ = request.user.following.filter(id__in=request.user.follower.all())
    followed_by_count = followed_by_.count()
    notification = Notification.objects.filter(user=request.user, is_seen=False)
    post_notification = Notification.objects.filter(user=request.user, is_seen=False)
    combined_notification = sorted(
        chain(notification, post_notification),
        key=lambda posts: posts.id
    )
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
        for let in notification_list:
            queryset.append(let.blog)
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
        for let in notification_list:
            queryset.append(let.blog)
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
        for let in Notification.objects.filter(user=request.user):
            queryset.append(let.is_seen == True)
            let.is_seen = True
            let.save()

        queryset = []
        for let in PostNotification.objects.filter(user=request.user):
            queryset.append(let.is_seen == True)
            let.is_seen = True
            let.save()

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