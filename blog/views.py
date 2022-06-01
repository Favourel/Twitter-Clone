from abc import ABC
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect, HttpResponse
from .models import *
from .forms import UpdateForm, RepostForm, RepostCommentBox, CommentBox, ImageForm, CreateForm
from django.contrib import messages
from django.db.models import Q
from users import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, serializers
from django.views.generic import UpdateView, DeleteView, View, FormView
from itertools import chain, product
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from users.models import User, UserStat, Story
from users.forms import UserUpdateForm
from django.db.models import F
from django.http import JsonResponse
import json
from django.forms.models import model_to_dict
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, datetime
from blog.templatetags.mentions import mentions


class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, ImageFieldFile):
            try:
                return o.path
            except ValueError as e:
                return ''
        else:
            return super().default(o)


class DateExtendedEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            try:
                return o.strftime("%b %d")
            except ValueError as e:
                return ''
        else:
            return super().default(o)


@login_required
def error_404(request, exception):
    data = {}
    return render(request, 'blog/error404.html', data)


def error_500(request):
    data = {}
    return render(request, 'blog/error404.html', data)
# class Home(PusherUpdateMixin, LoginRequiredMixin, View):


@login_required
def blog_list_view(request):
    user_list = User.objects.all().order_by('?').exclude(id__in=request.user.following.all()).exclude(
        username=request.user).exclude(id__in=request.user.block_list.all())[:5]
    user_following = request.user.following.all()
    user_block_list = request.user.block_list.all()
    user_mute_list = request.user.mute_list.all()
    let_test = []
    let_test_ = []
    for let in user_block_list:
        let_test = let.post_set.all()
        let_test_ = let.blogrepost_set.all()
        print(let_test)
    posts_reposted = BlogRepost.objects.filter(
        user__in=user_following).order_by("-date_posted"
                         ).exclude(user__in=user_mute_list).exclude(user__in=user_block_list).exclude(post__in=let_test).exclude(repost__in=let_test_)[:5] | \
         BlogRepost.objects.filter(user=request.user
                                   ).order_by("-date_posted").exclude(user__in=user_mute_list).exclude(user__in=user_block_list).exclude(post__in=let_test).exclude(repost__in=let_test_)

    followers_post = Post.objects.filter(author__in=request.user.following.all()
                                         ).order_by('-date_posted').exclude(author__in=user_mute_list).exclude(author__in=user_block_list) | \
                     Post.objects.filter(author=request.user
                                         ).order_by('-date_posted'
                                                    ).exclude(author__in=user_mute_list).exclude(author__in=user_block_list) | \
                     Post.objects.filter(
                         like__in=request.user.following.all()
                     ).order_by("-date_posted").exclude(author__in=user_mute_list).exclude(author__in=user_block_list)[:8]
    combined_posts = sorted(
        chain(posts_reposted, followers_post),
        key=lambda posts: posts.date_posted, reverse=True
    )
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    post_notification_count = PostNotification.objects.filter(user=request.user, is_seen=False).count()

    # c = Product.objects.last()  # Get the last content

    # q_set = []
    # for let in Post.objects.all():
    #     q_set = let.get_most_used_words(10)
    # print(q_set)  # Get the top 10 most used words

    context = {
        'blog_post': combined_posts,
        'posts_reposted': posts_reposted,
        'user_list': user_list,
        'notification_count': notification_count,
        'post_notification_count': post_notification_count,
        "story": Story.objects.filter(user__in=user_following).distinct(),
        "form": CreateForm(),
        "recent_search": RecentSearch.objects.filter(user=request.user)
    }
    # pusher_client.trigger('my-channel', 'showMessage', {'message': 'hello world'})
    return render(request, 'blog/blog_list.html', context)


# function that triggers the pusher request
def push_feed(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('photo')
        post = Post(author=request.user, content=content)
        post.save()
        dict_obj = model_to_dict(post.author)
        dict_object = model_to_dict(post)
        if image is not None:
            uploaded_image = BlogImages(post=post, image=image)
            uploaded_image.save()

            data = {
                "message": "Your post has been made",
                "author": dict_obj.get("display_name"),
                "email": dict_obj.get("username"),
                "author_image": ExtendedEncoder.default(dict_obj.get("image"), dict_obj.get("image")),
                # "author_image": dict_obj.get("image"),
                "date": DateExtendedEncoder.default(dict_object.get("date_posted"), dict_object.get("date_posted")),
                "like": len(dict_object.get("like")),
                "comment": 0,
                "content": mentions(post.content),
                "image": uploaded_image.image.url,
                "pk": dict_object.get("id"),
            }
            return JsonResponse(data)
        for user_noti in request.user.post_notification.all():
            notify = PostNotification(blog=post, sender=request.user, user=user_noti, notification_type=1)
            notify.save()

        data = {
            "message": "Your post has been made",
            "author": dict_obj.get("display_name"),
            "email": dict_obj.get("username"),
            "author_image": ExtendedEncoder.default(dict_obj.get("image"), dict_obj.get("image")),
            "date": DateExtendedEncoder.default(dict_object.get("date_posted"), dict_object.get("date_posted")),
            "like": len(dict_object.get("like")),
            "comment": 0,
            "content": mentions(post.content),
            "pk": dict_object.get("id"),
        }
        return JsonResponse(data)


@login_required
def blog_detail_view(request, pk):
    obj = get_object_or_404(Post, pk=pk)
    comments = obj.blogcomment_set.all().order_by("-date_posted")
    obj_likes = obj.like.all()
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    post_notification_count = PostNotification.objects.filter(user=request.user, is_seen=False).count()
    # update_form = UpdateForm(instance=obj)
    if request.method == "POST":
        if obj.author == request.user:
            obj.delete()
            return redirect("blog_home")

    context = {
        'object': obj,
        'comments': comments,
        'notification_count': notification_count,
        'post_notification_count': post_notification_count,
        'obj_likes': obj_likes,
        # 'update_form': update_form,
        "form": CommentBox()
    }
    return render(request, 'blog/blog_detail.html', context)


@login_required
def repost_detail_view(request, pk):
    obj = get_object_or_404(BlogRepost, pk=pk)
    comments = obj.repostcomment_set.all().order_by("-date_posted")
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    post_notification_count = PostNotification.objects.filter(user=request.user, is_seen=False).count()
    # update_form = UpdateForm(instance=obj)
    if request.method == "POST":
        if obj.user == request.user:
            obj.delete()
            notify = Notification.objects.filter(repost_blog=obj, sender=request.user, notification_type=4)
            notify.delete()
            # return redirect("blog_home")
            next = request.POST.get('next', '/')
            return HttpResponseRedirect(next)
    context = {
        'object': obj,
        'comments': comments,
        'notification_count': notification_count,
        'post_notification_count': post_notification_count,
        # 'update_form': update_form,
        "form": RepostCommentBox()
    }
    return render(request, 'blog/repost_detail.html', context)


@login_required
def blog_comment(request, pk):
    obj = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentBox(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.post = obj
            form.save()
        dict_obj = model_to_dict(form.user)
        dict_obj_ = model_to_dict(form.post.author)
        notify = Notification(blog=obj, sender=request.user, user=obj.author,
                              notification_type=2, text_preview=form.comment)
        notify.save()
        if not UserStat.objects.filter(user=obj.author).exists():
            user_profile = UserStat.objects.create(
                user=obj.author,
                account_engaged=1
            )
            user_profile.save()
        else:
            UserStat.objects.filter(user=obj.author).update(account_engaged=F('account_engaged') + 1)

    data = {
        "comment": request.POST.get('comment', None),
        "author": dict_obj.get("display_name"),
        "author_username": dict_obj.get("username"),
        "author_image": json.dumps(dict_obj["image"], cls=ExtendedEncoder),
        "is_verified": dict_obj.get("is_verified"),
        "replying": dict_obj_["username"],
        "message": "Your comment has been sent"
    }
    print(json.dumps(dict_obj["image"], cls=ExtendedEncoder))
    print(dict_obj.get("is_verified"))
    return JsonResponse(data)


# def delete_comment(request, pk):
#     comment = get_object_or_404(BlogComment, pk=pk)
#     if request.method == "POST":
#         if request.user == comment.user | comment.post.author:
#             comment.delete()
#             return redirect(comment.post.get_repost_url)
#     return render(request, 'blog/blog_detail.html', {})


def repost_comment(request, pk):
    if request.user.is_authenticated:
        obj = get_object_or_404(BlogRepost, pk=pk)
        form = RepostCommentBox()
        if request.method == 'POST':
            form = RepostCommentBox(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                form.post = obj
                form.save()
                instance = form
                dict_obj = model_to_dict(form.user)
                dict_obj_ = model_to_dict(form.post.user)
                # serialize in new friend object in json
                ser_instance = serializers.serialize('json', [instance, ])

            notify = Notification(repost_blog=obj, sender=request.user,
                                  user=obj.user, notification_type=6, text_preview=form.comment)
            notify.save()
            if not UserStat.objects.filter(user=obj.user).exists():
                user_profile = UserStat.objects.create(
                    user=obj.user,
                    account_engaged=1
                )
                user_profile.save()
            else:
                UserStat.objects.filter(user=obj.user).update(account_engaged=F('account_engaged') + 1)

            data = {
                # "message": ser_instance,
                "comment": request.POST.get('comment', None),
                "author": dict_obj.get("display_name"),
                "author_username": dict_obj.get("username"),
                "author_image": json.dumps(dict_obj["image"], cls=ExtendedEncoder),
                "replying": dict_obj_["username"],
                "message": "Your comment has been sent"
            }
            print(json.dumps(dict_obj["image"], cls=ExtendedEncoder))
            # print(json.load(dict_obj.get("image"), default=str, sort_keys=True, indent=1))
            return JsonResponse(data)
    else:
        form = RepostCommentBox()

    data = {
        "message": 'ser_instance'
    }
    return JsonResponse(data)


@login_required
def search(request):
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    post_notification_count = PostNotification.objects.filter(user=request.user, is_seen=False).count()
    var = models.User.objects.all()
    if request.method == 'GET':
        query = request.GET.get('q')
        submitbutton = request.GET.get('submit')
        if query is not None:
            lookups_people = Q(username__icontains=query)
            lookups_post = Q(content__icontains=query)
            lookups_repost = Q(text__icontains=query)
            lookups_comment = Q(comment__icontains=query)
            results_people = models.User.objects.filter(lookups_people).distinct()
            results_post = Post.objects.filter(lookups_post).distinct().order_by("-date_posted").exclude(author__in=request.user.block_list.all())
            results_lookups_repost = BlogRepost.objects.filter(lookups_repost).order_by("-date_posted").exclude(user__in=request.user.block_list.all())
            results_lookups_comment = BlogComment.objects.filter(lookups_comment).order_by("-date_posted")
            combined = sorted(
                chain(results_post, results_lookups_repost),
                key=lambda posts: posts.date_posted, reverse=True
            )
            if not RecentSearch.objects.filter(user=request.user, search_word=query).exists():
                search = RecentSearch.objects.create(user=request.user, search_word=query)
                search.save()
            context = {
                'results_people': results_people,
                'results_post': combined,
                'submitbutton': submitbutton,
                'notification_count': notification_count,
                'post_notification_count': post_notification_count,
            }
            return render(request, 'blog/search.html', context)
        else:
            return render(request, 'blog/search.html', )
    else:
        return render(request, 'blog/search.html', {'var': var, "notification_count": notification_count})


class PostLikeApi(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        user = self.request.user
        obj = Post.objects.get(pk=pk)
        # obj = get_object_or_404(Post, pk=pk)

        updated = False
        liked = False

        if user:
            if user in obj.like.all():
                liked = False
                obj.like.remove(user)
                message_user = f'"{user}" unliked {obj}'
                # if Notification.objects.filter(blog=obj, sender=user, user=obj.author, notification_type=1).exists():
                notify = Notification.objects.get(blog=obj, sender=user, notification_type=1)
                notify.delete()
                UserStat.objects.filter(user=obj.author).update(account_engaged=F('account_engaged') - 1)
            else:
                liked = True
                obj.like.add(user)
                message_user = f'"{user}" liked {obj}'
                notify = Notification(blog=obj, sender=user, user=obj.author, notification_type=1)
                notify.save()

                if not UserStat.objects.filter(user=obj.author).exists():
                    user_profile = UserStat.objects.create(
                        user=obj.author,
                        account_engaged=1
                    )
                    user_profile.save()
                else:
                    UserStat.objects.filter(user=obj.author).update(account_engaged=F('account_engaged') + 1)

                data = {
                    'updated': updated,
                    'like': liked,
                    'like_count': obj.like.count(),
                    'message_user': message_user,
                }
                return Response(data)

            updated = True

        data = {
            'updated': updated,
            'like': liked,
            'like_count': obj.like.count(),
            'message_user': message_user,
        }
        return Response(data)


class RepostLikeApi(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        user = self.request.user
        obj = get_object_or_404(BlogRepost, pk=pk)

        updated = False
        liked = False

        if user:
            if user in obj.like.all():
                liked = False
                obj.like.remove(user)
                message_user = f'"{user}" unliked {obj}'

                if Notification.objects.filter(repost_blog=obj, sender=user, user=obj.user,
                                               notification_type=5).exists():
                    notify = Notification.objects.get(repost_blog=obj, sender=user, notification_type=5)
                    notify.delete()
                UserStat.objects.filter(user=obj.user).update(account_engaged=F('account_engaged') - 1)

            else:
                liked = True
                obj.like.add(user)
                message_user = f'"{user}" liked {obj}'
                notify = Notification(repost_blog=obj, sender=user, user=obj.user, notification_type=5)
                notify.save()
                if not UserStat.objects.filter(user=obj.user).exists():
                    user_profile = UserStat.objects.create(
                        user=obj.user,
                        account_engaged=1
                    )
                    user_profile.save()
                else:
                    UserStat.objects.filter(user=obj.user).update(account_engaged=F('account_engaged') + 1)

                data = {
                    'updated': updated,
                    'like': liked,
                    'like_count': obj.like.count(),
                    'message_user': message_user,
                }
                return Response(data)

            updated = True

        data = {
            'updated': updated,
            'like': liked,
            'like_count': obj.like.count(),
            'message_user': message_user,
        }
        return Response(data)


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


@login_required
def create_post(request):
    if request.method == 'POST':
        post_save = CreateForm(request.POST)
        image = request.FILES.get('photo')
        if post_save.is_valid():
            post_save = post_save.save(commit=False)
            post_save.author = request.user
            post_save.save()
        dict_obj = model_to_dict(post_save.author)
        dict_object = model_to_dict(post_save)

        if image is not None:
            uploaded_image = BlogImages(post=post_save, image=image)
            uploaded_image.save()

            data = {
                "message": "Your post has been made",
                "author": dict_obj.get("display_name"),
                "email": dict_obj.get("username"),
                "author_image": ExtendedEncoder.default(dict_obj.get("image"), dict_obj.get("image")),
                "date": DateExtendedEncoder.default(dict_object.get("date_posted"), dict_object.get("date_posted")),
                "like": len(dict_object.get("like")),
                "comment": 0,
                "content": mentions(post_save.content),
                "image": uploaded_image.image.url,
                "pk": dict_object.get("id"),
            }
            return JsonResponse(data)
        for user_noti in request.user.post_notification.all():
            notify = PostNotification(blog=post_save, sender=request.user, user=user_noti, notification_type=1)
            notify.save()
        dict_obj = model_to_dict(post_save.author)
        dict_object = model_to_dict(post_save)

        data = {
            "message": "Your post has been made",
            "author": dict_obj.get("display_name"),
            "email": dict_obj.get("username"),
            "author_image": ExtendedEncoder.default(dict_obj.get("image"), dict_obj.get("image")),
            "date": DateExtendedEncoder.default(dict_object.get("date_posted"), dict_object.get("date_posted")),
            "like": len(dict_object.get("like")),
            "comment": 0,
            "content": mentions(post_save.content),
            "pk": dict_object.get("id"),
        }
        print(ExtendedEncoder.default(dict_obj.get("image"), dict_obj.get("image")))
        return JsonResponse(data)


@login_required
def repost_add_view(request, pk):
    obj = get_object_or_404(Post, pk=pk)
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    post_notification_count = PostNotification.objects.filter(user=request.user, is_seen=False).count()

    if not BlogRepost.objects.filter(user=request.user, post=obj).exists():
        if request.method == 'POST':
            form = RepostForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                form.post = obj
                form.save()

            messages.success(request, "Post reposted successfully")
            notify = Notification(blog=obj, sender=request.user, user=obj.author, notification_type=4)
            notify.save()

            if not UserStat.objects.filter(user=obj.author).exists():
                user_profile = UserStat.objects.create(
                    user=obj.author,
                    account_engaged=1
                )
                user_profile.save()
                return redirect("blog_home")
            else:
                UserStat.objects.filter(user=obj.author).update(account_engaged=F('account_engaged') + 1)
                return redirect("blog_home")

        else:
            form = RepostForm()

        context = {
            "form": form,
            "obj": obj,
            "notification_count": notification_count,
            "post_notification_count": post_notification_count,
        }
        return render(request, "blog/repost_add_view.html", context)
    else:
        messages.info(request, 'Post has already been reposted')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def repost_add_view_(request, pk):
    repost_obj = get_object_or_404(BlogRepost, pk=pk)
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    post_notification_count = PostNotification.objects.filter(user=request.user, is_seen=False).count()

    if not BlogRepost.objects.filter(user=request.user, repost=repost_obj).exists():
        if request.method == 'POST':
            form = RepostForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                form.repost = repost_obj
                form.save()

            messages.success(request, "Post reposted successfully")
            notify = Notification(repost_blog=form.repost, sender=request.user, user=repost_obj.user,
                                  notification_type=8)
            notify.save()

            if not UserStat.objects.filter(user=repost_obj.user).exists():
                user_profile = UserStat.objects.create(
                    user=repost_obj.user,
                    account_engaged=1
                )
                user_profile.save()
                return redirect("blog_home")
            else:
                UserStat.objects.filter(user=repost_obj.user).update(account_engaged=F('account_engaged') + 1)
                return redirect("blog_home")

        else:
            form = RepostForm()
        context = {
            "form": form,
            "obj": repost_obj,
            "notification_count": notification_count,
            "post_notification_count": post_notification_count,
        }
        return render(request, "blog/repost_add_view_.html", context)
    else:
        messages.info(request, 'Post has already been reposted')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView, ABC):
    # template_name = "blog/blog_detail.html"
    form_class = UpdateForm

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        return get_object_or_404(Post, pk=pk)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return True


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView, ABC):
    model = BlogComment

    def get_success_url(self):
        post = self.get_object()
        messages.success(self.request, "Post deleted")
        return reverse("blog_home")

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.post.author | post.user:
            return True
        return False


@login_required
def a_follower_post_view(request, username):
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
                        return redirect(f"../{request.user}/blog/")
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


def story_view(request, username):
    user = get_object_or_404(User, username=username)
    story = Story.objects.filter(user=user)
    context = {
        "story": story
    }
    return render(request, "blog/story.html", context)


# @login_required
# def post(request):
#     ImageFormSet = modelformset_factory(BlogImages, form=ImageForm, extra=4)
#     if request.method == 'POST':
#
#         postForm = CreateForm(request.POST)
#         formset = ImageFormSet(request.POST, request.FILES,
#                                queryset=BlogImages.objects.none())
#
#         if postForm.is_valid() and formset.is_valid():
#             post_form = postForm.save(commit=False)
#             post_form.user = request.user
#             post_form.save()
#
#             for form in formset.cleaned_data:
#                 # this helps to not crash if the user
#                 # do not upload all the photos
#                 if form:
#                     image = form['image']
#                     photo = BlogImages(post=post_form, image=image)
#                     photo.save()
#             # use django messages framework
#             messages.success(request,
#                              "Yeeew, check it out on the home page!")
#             return HttpResponseRedirect("/")
#         else:
#             print(postForm.errors, formset.errors)
#     else:
#         postForm = BlogImages()
#         formset = ImageFormSet(queryset=BlogImages.objects.none())
#     return render(request, 'products/navbar.html',
#                   {'postForm': postForm, 'formset': formset})


def ajax_posting(request):
    if request:
        content = request.POST.get('content', None)  # getting data from first_name input
        response_data = {}

        post = Post(author=request.user, content=content)
        post.save()

        if content:  # checking if first_name and last_name have value
            data = {
                'msg': 'Your form has been submitted successfully'  # response message
            }
            return JsonResponse(data)  # return response as JSON


def ajax_posting_comment(request, pk):
    if request:
        blog_post = get_object_or_404(Post, pk=pk)
        content = request.POST.get('content', None)  # getting data from first_name input
        response_data = {}

        post = Post(author=request.user, content=content)
        post.save()

        if content:  # checking if first_name and last_name have value
            data = {
                'msg': 'Your form has been submitted successfully'  # response message
            }
            return JsonResponse(data)  # return response as JSON
