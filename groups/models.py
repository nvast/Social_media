from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.core.exceptions import ObjectDoesNotExist


class Groups(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=25, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='group_owner')
    moderators = models.ManyToManyField(User, through="GroupsModerators", related_name="group_moderator")
    followers = models.ManyToManyField(User, through="GroupsFollowers", related_name="group_user")
    private = models.BooleanField(default=False)
    picture = models.ImageField(null=True, blank=True, upload_to="images/groups", default="../static/images/group-profile.png")
    posts = models.ManyToManyField(User, through="GroupPosts", related_name='group_posts')

    def transfer_ownership(self):
        next_owner = self.moderators.order_by("id").first()
        if next_owner:
            self.owner = next_owner
            self.moderators.remove(next_owner)
            self.followers.remove(next_owner)
            self.save()
        else:
            self.delete()


class GroupPosts(models.Model):
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.CharField(max_length=1000)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='group_post_likes', blank=True)
    comments = models.ManyToManyField(User, through="GroupComments", related_name="group_posts_comments")


class GroupComments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_user_comments", null=False)
    post = models.ForeignKey(GroupPosts, on_delete=models.CASCADE, related_name="group_post_comments", null=False)
    text = models.CharField(max_length=1000)


class GroupsFollowers(models.Model):
    groups = models.ForeignKey(Groups, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined = models.DateTimeField(auto_now_add=True)


class GroupsModerators(models.Model):
    groups = models.ForeignKey(Groups, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    privilege = models.DateTimeField(auto_now_add=True)
