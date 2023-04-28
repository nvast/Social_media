from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from groups.models import Groups


class Posts(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", null=False)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_for")
    user_profile_name = models.CharField(null=True, max_length=1000)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    post = models.CharField(max_length=1000)
    likes = models.ManyToManyField(User, through="PostsLikes", related_name='post_likes', blank=True)
    username = models.CharField(max_length=1000, null=True)
    comments = models.ManyToManyField(User, through="Comments", related_name="posts_comments")


class Comments(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usercomments", null=False)
    post_id = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="postcomments", null=False)
    username = models.CharField(max_length=200, null=True)
    text = models.CharField(max_length=1000)


class Follow(models.Model):
    from_user = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userinfo")
    profile_pic = models.ImageField(null=True, blank=True, upload_to="images/profile", default="../static/images/user.png")
    name = models.CharField(max_length=1000, null=True)
    sex = models.CharField(max_length=10, null=True)
    date_of_birth = models.CharField(max_length=100, null=True)
    live_in = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created:
        UserInfo.objects.create(user=instance, sex="", date_of_birth="", live_in="", email="", phone="", name=instance.username)

    post_save.connect(create_user_info, sender=User)


class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    conversation_id = models.CharField(max_length=10485760)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()


class PostsLikes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="like_from")
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="user_post")
    timestamp = models.DateTimeField(auto_now_add=True)


class GroupInvites(models.Model):
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, related_name="group_invites")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_invites_user")
    timestamp = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('Follow', 'Follow'),
        ('Comment', 'Comment'),
        ('Like', 'Like'),
        ('Chat', 'Chat'),
        ('Post', 'Post'),
        ('Invite', 'Invite')
    )

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_from')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_to')
    notification_type = models.CharField(max_length=25, choices=NOTIFICATION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    follow = models.ForeignKey(Follow, on_delete=models.CASCADE, related_name="notification_follow", null=True, blank=True)
    comment = models.ForeignKey(Comments, on_delete=models.CASCADE, related_name="notification_comment", null=True, blank=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="notification_chat", null=True, blank=True)
    like = models.ForeignKey(PostsLikes, on_delete=models.CASCADE, related_name="notification_like", null=True, blank=True)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="notification_post", null=True, blank=True)
    invite = models.ForeignKey(GroupInvites, on_delete=models.CASCADE, related_name="notification_invites", null=True, blank=True)










class User(AbstractBaseUser, PermissionsMixin):
    groups = models.ManyToManyField(Group, verbose_name=_('groups'), blank=True, related_name='main_users')
    user_permissions = models.ManyToManyField(Permission, verbose_name=_('user permissions'), blank=True, related_name='main_users')
    following = models.ManyToManyField('self', through=Follow, symmetrical=False, related_name='followers')

