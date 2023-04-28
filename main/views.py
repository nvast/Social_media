from django.shortcuts import render, redirect, get_object_or_404
from .forms import NewPostForm, CommentForm, ProfileInfoForm, ChatForm
from .models import Posts, Comments, Follow, UserInfo, Chat, Notification, PostsLikes
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
import uuid


def index(request):
    return render(request, 'main/index.html', {})


@login_required
def display_notification(request, notification_type, item_id):
    item = Notification.objects.get(pk=item_id)
    all_post_comments = Comments.objects.all().order_by("-id")
    current_user = request.user
    comment_form = CommentForm()

    if notification_type == "Like" or notification_type == "Comment" or notification_type == "Post":
        if notification_type == "Like":
            post = item.like.post
        elif notification_type == "Comment":
            post = item.comment.post_id
        elif notification_type == "Post":
            post = item.post

        related_users = []
        for comment in all_post_comments:
            if comment.post_id == post:
                related_users.append(comment.user_id)

        related_users = set(user for user in related_users)

        if "comment-submit" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.cleaned_data["comment"]
                user_id = request.user
                post_id = request.POST.get('post_id')
                username = request.user.username
                post = Posts.objects.get(id=post_id)
                new_comment = Comments(user_id=user_id, post_id=post, text=comment, username=username)
                new_comment.save()
                for user in related_users:
                    if user != request.user:
                        new_comment = Comments.objects.get(id=new_comment.id)
                        new_notification = Notification(from_user=request.user, to_user=user, comment=new_comment, notification_type="Comment")
                        new_notification.save()
                return redirect(request.path)

        return render(request, 'main/post.html', {"post": post,
                                                  "comments": all_post_comments,
                                                  "current_user": current_user,
                                                  'comment_form': comment_form,
                                                  })

    elif notification_type == "Chat":
        return redirect('chat', conversation_id=item.chat.conversation_id)

    elif notification_type == "Invite":
        return redirect('group', group_name=item.invite.group.name)

    elif notification_type == "Follow":
        return redirect('profile', username=item.from_user)


@login_required
def profile(request, username):
    users_profile = User.objects.get(username=username)
    all_posts = Posts.objects.all().order_by('-date', '-time')
    user_posts = Posts.objects.filter(user_id=users_profile.id)
    post_comments = Comments.objects.all().order_by("-id")
    other_user = get_object_or_404(User, username=username)
    is_followed = Follow.objects.filter(from_user=request.user, to_user=other_user)
    profile_info = UserInfo.objects.get(name=username)
    profile_followers = Follow.objects.filter(to_user=users_profile)
    profile_follows = len(profile_followers)



    if request.method == 'POST':
        if "post-submit" in request.POST:
            create_post_form = NewPostForm(request.POST)
            if create_post_form.is_valid():
                user_id = request.user
                post = create_post_form.cleaned_data['post']
                users_post = request.user.username
                new_post = Posts(user_id=user_id, post=post, username=users_post, to_user=users_profile, user_profile_name=username)
                new_post.save()
                if users_profile != request.user.username:
                    new_notification = Notification(from_user=request.user, to_user=users_profile, post=new_post, notification_type="Post")
                    new_notification.save()
                return redirect(request.path)

        elif "comment-submit" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.cleaned_data["comment"]
                user_id = request.user
                post_id = request.POST.get('post_id')
                username = request.user.username
                post = Posts.objects.get(id=post_id)
                new_comment = Comments(user_id=user_id, post_id=post, text=comment, username=username)
                new_comment.save()

                related_users = []
                for comment in post_comments:
                    if comment.post_id == post:
                        related_users.append(comment.user_id)

                related_users = set(user for user in related_users)

                for user in related_users:
                    if user != request.user:
                        new_comment = Comments.objects.get(id=new_comment.id)
                        new_notification = Notification(from_user=request.user, to_user=user, comment=new_comment, notification_type="Comment")
                        new_notification.save()
                return redirect(request.path)

        elif "profile_photo" in request.FILES:
            profile_info.profile_pic = request.FILES["profile_photo"]
            profile_info.save()


    create_post_form = NewPostForm()
    comment_form = CommentForm()

    return render(request, 'main/profile.html', {'create_post_form': create_post_form,
                                               'comment_form': comment_form,
                                               "current_user": request.user,
                                               "user_posts": user_posts,
                                               "comments": post_comments,
                                               "username": username,
                                               "other_user": other_user,
                                               "is_followed": is_followed,
                                               "all_posts": all_posts,
                                               "profile_info": profile_info,
                                               "profile_follows": profile_follows})


@login_required
def post_like(request, post_id):
    post = get_object_or_404(Posts, id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        new_like = PostsLikes.objects.filter(post_id=post_id).first()

        new_notification = Notification(notification_type="Like", like_id=new_like.id, from_user=new_like.user, to_user=post.to_user)
        new_notification.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def home(request):
    all_posts = Posts.objects.all().order_by('-date', '-time')
    post_comments = Comments.objects.all().order_by("-id")
    is_following = Follow.objects.filter(from_user=request.user).values_list("to_user", flat=True)
    is_following = [value for value in is_following]

    if request.method == 'POST':
        if "post-submit" in request.POST:
            create_post_form = NewPostForm(request.POST)
            if create_post_form.is_valid():
                user_id = request.user
                post = create_post_form.cleaned_data['post']
                users_post = request.user.username
                new_post = Posts(user_id=user_id, post=post, username=users_post, to_user=user_id, user_profile_name=users_post)
                new_post.save()
                return redirect(request.path)

        elif "comment-submit" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.cleaned_data["comment"]
                user_id = request.user
                post_id = request.POST.get('post_id')
                username = request.user.username
                post = Posts.objects.get(id=post_id)
                new_comment = Comments(user_id=user_id, post_id=post, text=comment, username=username)
                new_comment.save()

                related_users = []
                for comment in post_comments:
                    if comment.post_id == post:
                        related_users.append(comment.user_id)

                related_users = set(user for user in related_users)

                for user in related_users:
                    if user != request.user:
                        new = Comments.objects.get(id=new_comment.id)
                        new_notification = Notification(from_user=request.user, to_user=post.user_id, comment=new, notification_type="Comment")
                        new_notification.save()
                return redirect(request.path)

    else:
        create_post_form = NewPostForm()
        comment_form = CommentForm()

    return render(request, 'main/home.html', {'create_post_form': create_post_form,
                                               'comment_form': comment_form,
                                               "current_user": request.user,
                                               "comments": post_comments,
                                               "all_posts": all_posts,
                                               "is_following": is_following, })


@login_required
def follow(request, username):
    user = get_object_or_404(User, username=username)
    new_follow = Follow(from_user=request.user, to_user=user)
    new_follow.save()
    if request.user != user:
        new_notification = Notification(notification_type="Follow", follow_id=new_follow.id, from_user=request.user, to_user=user)
        new_notification.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def unfollow(request, username):
    user = get_object_or_404(User, username=username)
    Follow.objects.filter(from_user=request.user, to_user=user).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# code for follows section needed to remove your follows / followed by
@login_required
def cancel_follow(request, username):
    user = get_object_or_404(User, username=username)
    Follow.objects.filter(from_user=user, to_user=request.user).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def follows(request):
    all_follows = Follow.objects.all()
    userinfo = UserInfo.objects.all()
    return render(request, 'main/follows.html', {"all_follows": all_follows,
                                                 "current_user": request.user,
                                                 "userinfo": userinfo, })


@login_required
def search_users(request):
    find_user = None
    current_user_follows = Follow.objects.filter(from_user=request.user).all()
    current_user_follows = [user.to_user for user in current_user_follows]

    if request.method == "GET":
        find = request.GET.get("search")
        find_user = User.objects.filter(username__icontains=find)

    return render(request, 'main/search.html', {'find_user': find_user,
                                                "current_user_follows": current_user_follows, })

@login_required
def delete_post(request):
    if request.method == "POST":
        post_id = request.POST.get("post")
        Posts.objects.filter(id=post_id).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def edit_post(request, post_id):
    post = Posts.objects.filter(id=post_id).values('post').first()
    post_text = post["post"]

    if request.method == "POST":
        new_post = request.POST.get("post_text")
        post = Posts.objects.get(id=post_id)
        if new_post:
            post.post = new_post
            post.save()
        return redirect("home")

    return render(request, 'main/edit_post.html', {"post_id": post_id,
                                                   "post_text": post_text, })


@login_required
def delete_comment(request):
    if request.method == "POST":
        comment_id = request.POST.get("comment")
        Comments.objects.get(id=comment_id).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def edit_profile(request, username):
    user = get_object_or_404(User, username=username)
    userinfo = UserInfo.objects.get(user=user)

    if request.method == "POST":
        form = ProfileInfoForm(request.POST, instance=userinfo)
        if form.is_valid():
            userinfo = form.save(commit=False)
            email = form.cleaned_data["email"]
            userinfo.email = user.email if email else ""
            userinfo.user = user
            userinfo.name = username
            userinfo.save()
            return redirect('profile', username=username)
    else:
        form = ProfileInfoForm(instance=userinfo)
    return render(request, 'main/edit_profile.html', {"form": form})


@login_required
def chat(request, conversation_id):
    form = ChatForm()
    current_user = request.user

    current_chat = Chat.objects.filter(conversation_id=conversation_id).order_by("-timestamp")

    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            try:
                recipient_name = request.GET.get('name')
                recipient = User.objects.get(username=recipient_name)
            except ObjectDoesNotExist:
                if current_chat.first().sender == current_user:
                    recipient = current_chat.first().recipient
                else:
                    recipient = current_chat.first().sender
            new_chat = Chat(conversation_id=conversation_id, message=form.cleaned_data['message'], sender=current_user, recipient=recipient)
            new_chat.save()
            print(new_chat.recipient)
            new_notification = Notification(notification_type="Chat", chat_id=new_chat.id, from_user=new_chat.sender, to_user=new_chat.recipient)
            new_notification.save()

    return render(request, 'main/chat.html', {"chat_form": form,
                                              "current_chat": current_chat,
                                              "current_user": current_user, })



@login_required
def chat_choice(request, username):
    form = ChatForm
    current_user = request.user
    unique_conversation_ids = Chat.objects.values_list('conversation_id', flat=True).distinct()

    all_chats = [Chat.objects.filter(conversation_id=conversation_id).order_by("-timestamp").first() for conversation_id in unique_conversation_ids]
    all_chats.sort(key=lambda x: x.timestamp, reverse=True)

    my_follows = Follow.objects.filter(from_user=request.user)
    unique_id = str(uuid.uuid4())

    return render(request, 'main/chat_choice.html', {"chat_form": form,
                                                     "all_chats": all_chats,
                                                     "current_user": current_user,
                                                     "my_follows": my_follows,
                                                     "unique_id": unique_id, })

@login_required
def chat_delete(request):
    if request.method == "POST":
        chat_id = request.POST.get("chat")
        Chat.objects.filter(conversation_id=chat_id).delete()
    return redirect('chat_choice', username=request.user.username)
