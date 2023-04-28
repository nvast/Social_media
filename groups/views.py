from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .forms import CreateGroupForm
from .models import Groups, GroupPosts, GroupComments, GroupsFollowers, GroupsModerators
from django.contrib.auth.models import User
from random import *
from main.forms import NewPostForm, CommentForm
from urllib.parse import quote
from main.models import Follow, UserInfo, Notification, GroupInvites


@login_required
def groups(request):
    all_groups = Groups.objects.all()
    current_user_groups = [group for group in all_groups if request.user in group.followers.all()]
    current_user_mods = [group for group in all_groups if request.user in group.moderators.all()]
    owned_groups = [group for group in all_groups if request.user == group.owner]
    random_groups = sample(set(all_groups), min(len(all_groups), 10))

    if request.method == "POST":
        if "join_now" in request.POST:
            name = request.POST.get("name")
            group_pk = request.POST.get("pk")
            group = Groups.objects.get(id=group_pk)
            group.followers.add(request.user)
            return redirect(f"/groups/{quote(name)}/")

        if "leave_group" in request.POST:
            group_pk = request.POST.get("pk")
            group = Groups.objects.get(id=group_pk)
            group.followers.remove(request.user)
            return redirect("groups")
    return render(request, 'groups/groups.html', {"random_groups": random_groups,
                                                  "current_user_groups": current_user_groups,
                                                  "owned_groups": owned_groups,
                                                  "current_user_mods": current_user_mods, })


@login_required
def create_group(request):

    if request.method == "POST":
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"].title()

            if Groups.objects.filter(name=name).exists():
                form.add_error("name", "Group with this name already exists, choose another one.")
            else:
                type = form.cleaned_data["type"].capitalize()
                owner = request.user
                private = form.cleaned_data["private"]
                new_group = Groups(name=name, owner=owner, private=private, type=type)
                new_group.save()
                return redirect(f"/groups/{quote(name)}/")
    else:
        form = CreateGroupForm()
    return render(request, 'groups/create_group.html', {'form': form, })


@login_required
def group(request, group_name):
    current_group = get_object_or_404(Groups, name=group_name)
    all_posts = GroupPosts.objects.all().order_by('-date', '-time')
    post_comments = GroupComments.objects.all().order_by("-id")
    owner = current_group.owner
    all_mods = current_group.moderators.all()

    if current_group.followers.filter(id=request.user.id).exists():
        member = True
    else:
        member = False

    if request.method == 'POST':
        if "post-submit" in request.POST:
            create_post_form = NewPostForm(request.POST)
            if create_post_form.is_valid():
                post = create_post_form.cleaned_data['post']
                new_post = GroupPosts(group=current_group, user=request.user, post=post)
                new_post.save()
                return redirect(f"/groups/{quote(group_name)}/")

        elif "comment-submit" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.cleaned_data["comment"]
                post_id = request.POST.get('post_id')
                post = GroupPosts.objects.get(id=post_id)
                new_comment = GroupComments(user=request.user, post=post, text=comment)
                new_comment.save()
                return redirect(f"/groups/{quote(group_name)}/")

        elif "group_photo" in request.FILES:
            current_group.picture = request.FILES["group_photo"]
            current_group.save()

        elif "join_now" in request.POST:
            name = request.POST.get("name")
            group_pk = request.POST.get("pk")
            group = Groups.objects.get(id=group_pk)
            group.followers.add(request.user)
            return redirect(f"/groups/{quote(name)}/")

        elif "leave_group" in request.POST:
            group_pk = request.POST.get("pk")
            group = Groups.objects.get(id=group_pk)
            group.followers.remove(request.user)
            group.moderators.remove(request.user)
            return redirect("groups")

    create_post_form = NewPostForm()
    comment_form = CommentForm()
    return render(request, 'groups/group.html', {"create_post_form": create_post_form,
                                                 "comment_form": comment_form,
                                                 "all_posts": all_posts,
                                                 "current_user": request.user,
                                                 "current_group": current_group,
                                                 "comments": post_comments,
                                                 "member": member,
                                                 "owner": owner,
                                                 "all_mods": all_mods, })

@login_required
def delete_group_post(request):
    if request.method == "POST":
        post_id = request.POST.get("post")
        GroupPosts.objects.filter(id=post_id).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def edit_group_post(request, post_id):
    post = GroupPosts.objects.filter(id=post_id).values('post').first()
    post_text = post["post"]

    if request.method == "POST":
        new_post = request.POST.get("post_text")
        post = GroupPosts.objects.get(id=post_id)
        if new_post:
            post.post = new_post
            post.save()
        return redirect("group", group_name=GroupPosts.objects.get(id=post_id).group.name)

    return render(request, 'main/edit_post.html', {"post_id": post_id,
                                                   "post_text": post_text, })


@login_required
def group_post_like(request, post_id):
    post = get_object_or_404(GroupPosts, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def edit_group(request, group_name):
    group = Groups.objects.get(name=group_name)

    if request.method == "POST":
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group.name = form.cleaned_data["name"]
            group.type = form.cleaned_data["type"]
            group.private = form.cleaned_data["private"]
            group.save()
            return redirect(f'/groups/{quote(group_name)}/')
    else:
        form = CreateGroupForm(initial={'name': group.name, 'type': group.type, 'private': group.private})
    return render(request, 'main/edit_profile.html', {"form": form})


@login_required
def group_followers(request, group_name):
    current_group = get_object_or_404(Groups, name=group_name)
    current_user = request.user
    all_followers = current_group.followers.all()
    all_mods = current_group.moderators.all()
    owner = current_group.owner

    for follower in all_followers:
        follower.joined_date = GroupsFollowers.objects.get(groups=current_group, user=follower).joined
    return render(request, 'groups/group_followers.html', {"current_group": current_group,
                                                           "all_followers": all_followers,
                                                           "all_mods": all_mods,
                                                           "owner": owner,
                                                           "current_user": current_user, })


@login_required
def group_moderators(request, group_name):
    current_group = get_object_or_404(Groups, name=group_name)
    all_mods = current_group.moderators.all()


    for mod in all_mods:
        mod.privilege_given = GroupsModerators.objects.get(groups=current_group, user=mod).privilege

    return render(request, 'groups/group_moderators.html', {"current_group": current_group,
                                                            "all_mods": all_mods, })

@login_required
def leave_group(request, group_name):
    current_group = get_object_or_404(Groups, name=group_name)
    current_group.followers.remove(request.user)
    current_group.moderators.remove(request.user)
    return redirect("groups")


@login_required
def delete_follower(request, group_name):
    current_group = get_object_or_404(Groups, name=group_name)
    if request.user == current_group.owner:
        current_group.transfer_ownership()
        return redirect("groups")
    if request.method == "POST":
        if "delete_follower" in request.POST:
            follower = request.POST.get("group_follower")
            user = User.objects.get(username=follower)
            current_group.followers.remove(user)
            GroupPosts.objects.filter(user=user).delete()
    return redirect('group_followers', group_name=group_name)


@login_required
def delete_moderator(request, group_name):
    if request.method == "POST":
        if "delete_moderator" in request.POST:
            current_group = get_object_or_404(Groups, name=group_name)
            follower = request.POST.get("group_follower")
            user = User.objects.get(username=follower)
            current_group.moderators.remove(user)
            current_group.followers.add(user)
    return redirect('group_moderators', group_name=group_name)


@login_required
def add_moderator(request, group_name):
    if request.method == "POST":
        if "add_moderator" in request.POST:
            current_group = get_object_or_404(Groups, name=group_name)
            follower = request.POST.get("group_follower")
            user = User.objects.get(username=follower)
            current_group.moderators.add(user)
            current_group.followers.remove(user)
    return redirect('group_moderators', group_name=group_name)


@login_required
def group_invite(request, group_name):
    current_group = get_object_or_404(Groups, name=group_name)
    all_follows = Follow.objects.all()
    userinfo = UserInfo.objects.all()
    current_user = request.user
    current_group_invites = GroupInvites.objects.filter(group=current_group).all()
    current_group_invites = [user.user for user in current_group_invites]

    if request.method == "POST":
        name = request.POST.get("name")
        to_user = User.objects.get(username=name)

        if "invite" in request.POST:
            new_invite = GroupInvites(user=to_user, group=current_group)
            new_invite.save()
            new_notification = Notification(notification_type="Invite", invite=new_invite, from_user=request.user, to_user=to_user)
            new_notification.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        elif "cancel_invite" in request.POST:
            GroupInvites.objects.get(group=current_group, user=to_user).delete()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'groups/group_invite.html', {"all_follows": all_follows,
                                                        "userinfo": userinfo,
                                                        "current_user": current_user,
                                                        "current_group": current_group,
                                                        "current_group_invites": current_group_invites, })


@login_required
def search_groups(request):
    all_groups = Groups.objects.all()

    if request.method == "GET":
        find = request.GET.get("search")
        find_groups = Groups.objects.filter(name__icontains=find)

    current_user_groups = [group for group in all_groups if request.user in group.followers.all()]
    current_user_mods = [group for group in all_groups if request.user in group.moderators.all()]
    owned_groups = [group for group in all_groups if request.user == group.owner]

    if request.method == "POST":
        if "join_now" in request.POST:
            name = request.POST.get("name")
            group_pk = request.POST.get("pk")
            group = Groups.objects.get(id=group_pk)
            group.followers.add(request.user)
            return redirect(f"/groups/{quote(name)}/")

        if "leave_group" in request.POST:
            group_pk = request.POST.get("pk")
            group = Groups.objects.get(id=group_pk)
            group.followers.remove(request.user)
            return redirect("groups")

    return render(request, 'groups/groups_search.html', {"find_groups": find_groups,
                                                         "current_user_groups": current_user_groups,
                                                         "owned_groups": owned_groups,
                                                         "current_user_mods": current_user_mods, })